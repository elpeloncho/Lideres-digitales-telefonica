from app.engine.config import DEFAULT_CONFIG, EngineConfig
from app.engine.models import (
    DecisionInput,
    IncidentCategory,
    Priority,
    RecommendationAction,
    Route,
    SafetyEffect,
    SafetyResult,
    SourceType,
    TriggeredRule,
    VerificationStatus,
)
from app.engine.priority import priority_rank


def evaluate_safety_rules(
    incident: DecisionInput,
    config: EngineConfig = DEFAULT_CONFIG,
    age_hours: float | None = None,
) -> SafetyResult:
    triggered: list[TriggeredRule] = []

    if incident.category in {
        IncidentCategory.ELECTRICAL_HAZARD,
        IncidentCategory.DAMAGED_POLE,
    }:
        triggered.append(
            TriggeredRule(
                id="SR-01",
                reason="La categoría requiere una inspección urgente.",
                effect=SafetyEffect(
                    priority_floor=Priority.HIGH,
                    urgent_review=True,
                    proposed_action=RecommendationAction.INSPECT_URGENTLY,
                ),
            )
        )

    if (
        incident.category == IncidentCategory.STREETLIGHT_FAILURE
        and incident.sensitive_location is not None
        and incident.sensitive_location >= config.sensitive_location_threshold
    ):
        triggered.append(
            TriggeredRule(
                id="SR-02",
                reason=(
                    "La incidencia afecta a un entorno de importancia "
                    f"{incident.sensitive_location:.0f}/100."
                ),
                effect=SafetyEffect(priority_floor=Priority.HIGH),
            )
        )

    if not incident.has_valid_coordinates or (
        incident.pedestrian_use is None
        and age_hours is None
        and incident.sensitive_location is None
    ):
        triggered.append(
            TriggeredRule(
                id="SR-03",
                reason="Faltan coordenadas válidas o todos los factores de prioridad.",
                effect=SafetyEffect(
                    route=Route.TRIAGE,
                    proposed_action=RecommendationAction.NEEDS_TRIAGE,
                ),
            )
        )

    if (
        incident.source_type == SourceType.RESIDENT_REPORT
        and incident.verification != VerificationStatus.VERIFIED
    ):
        triggered.append(
            TriggeredRule(
                id="SR-04",
                reason="El reporte de residente todavía no ha sido verificado.",
                effect=SafetyEffect(route=Route.TRIAGE),
            )
        )

    if (
        incident.category == IncidentCategory.STREETLIGHT_FAILURE
        and incident.lighting_status.state.value == "on"
    ):
        triggered.append(
            TriggeredRule(
                id="SR-05",
                reason=(
                    "El reporte indica una luminaria apagada, pero el proveedor "
                    "de contexto informa que está encendida."
                ),
                effect=SafetyEffect(route=Route.TRIAGE),
            )
        )

    triggered.sort(key=lambda rule: rule.id)
    floors = {
        rule.effect.priority_floor
        for rule in triggered
        if rule.effect.priority_floor is not None
    }
    priority_floor = (
        max(floors, key=priority_rank) if floors else None
    )
    routes = {rule.effect.route for rule in triggered}
    route = Route.TRIAGE if Route.TRIAGE in routes else Route.QUEUE
    urgent_review = any(rule.effect.urgent_review for rule in triggered)

    conflicts: list[str] = []
    if len(floors) > 1:
        conflicts.append(
            "Varias reglas fijan suelos de prioridad; se aplica el más alto."
        )
    actions = {
        rule.effect.proposed_action
        for rule in triggered
        if rule.effect.proposed_action is not None
    }
    if len(actions) > 1:
        conflicts.append(
            "Varias reglas proponen acciones; se aplica la de mayor precedencia."
        )
    if route == Route.TRIAGE and urgent_review:
        conflicts.append(
            "La revisión urgente conserva la validación humana requerida por triaje."
        )

    return SafetyResult(
        triggered_rules=tuple(triggered),
        priority_floor=priority_floor,
        urgent_review=urgent_review,
        route=route,
        data_conflict=any(rule.id == "SR-05" for rule in triggered),
        conflicts=tuple(conflicts),
    )
