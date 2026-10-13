from app.engine.models import (
    DecisionInput,
    DecisionResult,
    Priority,
    QueueComparison,
    Recommendation,
    RecommendationAction,
    Route,
)
from app.engine.priority import priority_rank


def build_recommendation(
    incident: DecisionInput,
    result_priority: Priority | None,
    score: float | None,
    urgent_review: bool,
    route: Route,
    data_conflict: bool,
    rationale: tuple[str, ...],
    age_hours: float | None,
) -> Recommendation:
    if urgent_review:
        action = RecommendationAction.INSPECT_URGENTLY
    elif route == Route.TRIAGE and incident.status.value == "reported":
        action = RecommendationAction.NEEDS_TRIAGE
    elif (
        not rationale
        or data_conflict
        or not result_priority
        or not all(
            (
                incident.pedestrian_use is not None,
                age_hours is not None,
                incident.sensitive_location is not None,
            )
        )
    ):
        action = RecommendationAction.VERIFY_ON_SITE
    elif result_priority == Priority.HIGH:
        action = RecommendationAction.REPAIR_PRIORITY
    else:
        action = RecommendationAction.REPAIR_SCHEDULED

    return Recommendation(
        action=action,
        rationale=rationale,
        queue_key=(
            urgent_review,
            priority_rank(result_priority),
            score,
            age_hours,
            incident.id,
        ),
    )


def queue_sort_key(decision: DecisionResult) -> tuple[bool, int, bool, float, bool, float, str]:
    urgent_review, rank, score, age_hours, incident_id = (
        decision.recommendation.queue_key
    )
    return (
        not urgent_review,
        -rank,
        score is None,
        -(score if score is not None else 0),
        age_hours is None,
        -(age_hours if age_hours is not None else 0),
        incident_id,
    )


def sort_decisions(
    decisions: list[DecisionResult],
) -> list[DecisionResult]:
    ids = [decision.incident_id for decision in decisions]
    if len(ids) != len(set(ids)):
        raise ValueError("La cola no puede contener identificadores duplicados.")
    return sorted(decisions, key=queue_sort_key)


def compare(a: DecisionResult, b: DecisionResult) -> QueueComparison:
    urgent_a, rank_a, score_a, age_a, id_a = a.recommendation.queue_key
    urgent_b, rank_b, score_b, age_b, id_b = b.recommendation.queue_key
    comparisons = (
        (
            "urgent_review",
            urgent_a,
            urgent_b,
            "revisión urgente",
        ),
        (
            "final_priority",
            rank_a,
            rank_b,
            "rango de prioridad final",
        ),
        ("score", score_a, score_b, "puntuación"),
        ("age_hours", age_a, age_b, "antigüedad"),
        ("id", id_a, id_b, "identificador"),
    )
    for criterion, value_a, value_b, label in comparisons:
        if value_a != value_b:
            if criterion == "urgent_review":
                first = a.incident_id if value_a else b.incident_id
                explanation = f"{first} va antes por revisión urgente."
            elif criterion == "final_priority":
                first = a.incident_id if value_a > value_b else b.incident_id
                explanation = (
                    f"{first} va antes por rango de prioridad final "
                    f"({value_a} frente a {value_b})."
                )
            elif criterion == "score":
                first = (
                    a.incident_id
                    if value_a is not None
                    and (value_b is None or value_a > value_b)
                    else b.incident_id
                )
                explanation = (
                    f"{first} va antes por puntuación "
                    f"({value_a} frente a {value_b})."
                )
            elif criterion == "age_hours":
                first = (
                    a.incident_id
                    if value_a is not None
                    and (value_b is None or value_a > value_b)
                    else b.incident_id
                )
                explanation = (
                    f"{first} va antes por antigüedad "
                    f"({value_a} frente a {value_b})."
                )
            else:
                first = a.incident_id if value_a < value_b else b.incident_id
                explanation = f"{first} va antes por {label}."
            return QueueComparison(
                criterion=criterion,
                incident_a=a.incident_id,
                value_a=str(value_a),
                incident_b=b.incident_id,
                value_b=str(value_b),
                explanation=explanation,
            )
    return QueueComparison(
        criterion="tie",
        incident_a=a.incident_id,
        value_a="igual",
        incident_b=b.incident_id,
        value_b="igual",
        explanation="Las dos decisiones tienen la misma clave de ordenación.",
    )
