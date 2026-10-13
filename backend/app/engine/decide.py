from datetime import datetime

from app.engine.config import DEFAULT_CONFIG, EngineConfig
from app.engine.models import (
    DecisionInput,
    DecisionResult,
    Route,
)
from app.engine.priority import calculate_priority, explain_priority, priority_rank
from app.engine.recommendation import build_recommendation
from app.engine.safety_rules import evaluate_safety_rules

ENGINE_VERSION = "0.2.0"


def decide(
    incident: DecisionInput,
    evaluated_at: datetime,
    config: EngineConfig = DEFAULT_CONFIG,
) -> DecisionResult:
    if evaluated_at.tzinfo is None or evaluated_at.utcoffset() is None:
        raise ValueError("evaluated_at debe incluir zona horaria.")

    age_hours = incident.age_hours
    if age_hours is None and incident.created_at is not None:
        if incident.created_at.tzinfo is None or incident.created_at.utcoffset() is None:
            raise ValueError("created_at debe incluir zona horaria.")
        elapsed = (evaluated_at - incident.created_at).total_seconds() / 3600
        if elapsed < 0:
            raise ValueError("created_at no puede ser posterior a evaluated_at.")
        age_hours = elapsed

    safety = evaluate_safety_rules(incident, config, age_hours)
    priority = calculate_priority(
        pedestrian_use=incident.pedestrian_use,
        age_hours=age_hours,
        sensitive_location=incident.sensitive_location,
        config=config,
        priority_floor=safety.priority_floor,
    )
    conflicts = list(safety.conflicts)
    if (
        safety.priority_floor is not None
        and priority.score_priority is not None
        and priority_rank(priority.score_priority) < priority_rank(safety.priority_floor)
    ):
        conflicts.append(
            "El suelo de seguridad prevalece sobre la prioridad calculada por puntuación."
        )
    if conflicts != list(safety.conflicts):
        safety = safety.model_copy(update={"conflicts": tuple(conflicts)})

    explanation = explain_priority(
        priority,
        incident.pedestrian_use,
        age_hours,
        incident.sensitive_location,
        config,
    )
    rationale: list[str] = []
    if safety.urgent_review:
        rationale.append("Una regla de seguridad requiere revisión humana urgente.")
    if safety.route == Route.TRIAGE:
        rationale.append("La incidencia requiere validación humana antes de entrar en la cola.")
    if priority.final_priority is not None:
        score_value = (
            "sin puntuación disponible"
            if priority.score is None
            else f"{priority.score:.2f}/100"
        )
        rationale.append(
            f"Prioridad final {priority.final_priority.value} "
            f"(puntuación: {score_value})."
        )
    if safety.priority_floor is not None:
        rationale.append(
            f"Las reglas de seguridad fijan un mínimo de prioridad "
            f"{safety.priority_floor.value}."
        )
    if safety.data_conflict:
        rationale.append("Hay datos contradictorios; no se descarta el reporte.")
    rationale.extend(priority.warnings)

    recommendation = build_recommendation(
        incident=incident,
        result_priority=priority.final_priority,
        score=priority.score,
        urgent_review=safety.urgent_review,
        route=safety.route,
        data_conflict=safety.data_conflict,
        rationale=tuple(rationale),
        age_hours=age_hours,
    )
    return DecisionResult(
        incident_id=incident.id,
        engine_version=ENGINE_VERSION,
        config_version=config.config_version,
        evaluated_at=evaluated_at,
        is_simulated=incident.is_simulated,
        inputs=incident.model_copy(
            update={
                "age_hours": age_hours,
                "context_provenance": dict(sorted(incident.context_provenance.items())),
            }
        ),
        safety=safety,
        priority=priority,
        recommendation=recommendation,
        explanation=explanation,
    )
