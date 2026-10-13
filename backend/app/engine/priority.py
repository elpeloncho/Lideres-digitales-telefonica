from math import isfinite

from app.engine.config import DEFAULT_CONFIG, EngineConfig
from app.engine.models import Priority, PriorityResult

FACTOR_LABELS = {
    "pedestrian_use": "uso peatonal estimado",
    "age": "antigüedad",
    "sensitive_location": "importancia del entorno",
}


def classify(score: float, config: EngineConfig = DEFAULT_CONFIG) -> Priority:
    if score >= config.high_threshold:
        return Priority.HIGH
    if score >= config.medium_threshold:
        return Priority.MEDIUM
    return Priority.LOW


def priority_rank(priority: Priority | None) -> int:
    return {None: 0, Priority.LOW: 1, Priority.MEDIUM: 2, Priority.HIGH: 3}[priority]


def _level(value: float) -> str:
    if value >= 70:
        return "elevado"
    if value >= 40:
        return "moderado"
    return "bajo"


def calculate_priority(
    pedestrian_use: float | None,
    age_hours: float | None,
    sensitive_location: float | None,
    config: EngineConfig = DEFAULT_CONFIG,
    priority_floor: Priority | None = None,
) -> PriorityResult:
    for name, value in (
        ("pedestrian_use", pedestrian_use),
        ("sensitive_location", sensitive_location),
    ):
        if value is not None and (
            not isfinite(value) or not 0 <= value <= 100
        ):
            raise ValueError(f"{name} fuera de rango [0, 100]: {value}")
    if age_hours is not None and (not isfinite(age_hours) or age_hours < 0):
        raise ValueError(f"age_hours no puede ser negativo: {age_hours}")

    age_score = (
        None
        if age_hours is None
        else min(age_hours / config.age_reference_hours, 1) * 100
    )
    factors = {
        "pedestrian_use": pedestrian_use,
        "age": age_score,
        "sensitive_location": sensitive_location,
    }
    base_weights = {
        "pedestrian_use": config.weight_pedestrian_use,
        "age": config.weight_age,
        "sensitive_location": config.weight_sensitive_location,
    }
    available = {name: value for name, value in factors.items() if value is not None}
    missing = tuple(name for name in factors if name not in available)
    warnings = [
        f"Factor ausente: {FACTOR_LABELS[name]}. La puntuación no lo incluye."
        for name in missing
    ]

    total_weight = sum(base_weights[name] for name in available)
    if not available or total_weight <= 0:
        return PriorityResult(
            score=None,
            score_priority=None,
            final_priority=priority_floor,
            complete=False,
            missing_factors=missing,
            weights={},
            contributions={},
            warnings=(
                *warnings,
                "No hay factores suficientes para calcular una prioridad.",
            ),
        )

    weights = {
        name: base_weights[name] / total_weight
        for name in available
    }
    if missing:
        warnings.append(
            "Puntuación parcial: los pesos se han repartido entre los factores disponibles."
        )

    contributions = {
        name: round(weights[name] * value, 2)
        for name, value in available.items()
    }
    score = round(
        sum(weights[name] * value for name, value in available.items()),
        2,
    )
    score_priority = classify(score, config)
    final_priority = (
        score_priority
        if priority_rank(score_priority) >= priority_rank(priority_floor)
        else priority_floor
    )
    return PriorityResult(
        score=score,
        score_priority=score_priority,
        final_priority=final_priority,
        complete=not missing,
        missing_factors=missing,
        weights=weights,
        contributions=contributions,
        warnings=tuple(warnings),
    )


def explain_priority(
    result: PriorityResult,
    pedestrian_use: float | None,
    age_hours: float | None,
    sensitive_location: float | None,
    config: EngineConfig = DEFAULT_CONFIG,
) -> tuple[str, ...]:
    age_score = (
        None
        if age_hours is None
        else min(age_hours / config.age_reference_hours, 1) * 100
    )
    values = {
        "pedestrian_use": pedestrian_use,
        "age": age_score,
        "sensitive_location": sensitive_location,
    }
    ordered = sorted(
        result.contributions,
        key=lambda name: (-result.contributions[name], name),
    )
    explanations = []
    for name in ordered:
        value = values[name]
        if value is None:
            continue
        label = FACTOR_LABELS[name].capitalize()
        level = _level(value)
        if name == "age":
            level = {"elevado": "elevada", "moderado": "moderada", "bajo": "baja"}[
                level
            ]
        explanations.append(
            f"{label} {level} ({value:.0f}/100): "
            f"aporta {result.contributions[name]:.1f} puntos."
        )
    return tuple(explanations)
