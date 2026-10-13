from datetime import UTC, datetime

from app.engine.config import DEFAULT_CONFIG
from app.engine.decide import decide
from app.engine.models import (
    DecisionInput,
    DecisionResult,
    IncidentStatus,
    SourceType,
)
from app.engine.recommendation import compare, sort_decisions
from app.repositories.json_store import JsonStore


def evaluate_incident(
    incident: DecisionInput,
    evaluated_at: datetime | None = None,
) -> DecisionResult:
    return decide(incident, evaluated_at or datetime.now(UTC), DEFAULT_CONFIG)


def list_decisions(
    store: JsonStore,
    *,
    include_closed: bool = True,
) -> list[DecisionResult]:
    evaluated_at = datetime.now(UTC)
    decisions = [
        decide(incident, evaluated_at)
        for incident in store.list_incidents()
        if include_closed
        or incident.status
        not in {IncidentStatus.RESOLVED, IncidentStatus.REJECTED}
    ]
    return sort_decisions(decisions)


def queue_decisions(store: JsonStore) -> list[DecisionResult]:
    return [
        decision
        for decision in list_decisions(store, include_closed=False)
        if decision.safety.route.value == "queue"
        and decision.inputs.status != IncidentStatus.REPORTED
    ]


def compare_incidents(
    store: JsonStore, incident_a_id: str, incident_b_id: str
):
    incidents = {incident.id: incident for incident in store.list_incidents()}
    if incident_a_id not in incidents or incident_b_id not in incidents:
        return None
    evaluated_at = datetime.now(UTC)
    return compare(
        decide(incidents[incident_a_id], evaluated_at),
        decide(incidents[incident_b_id], evaluated_at),
    )


def filter_decisions(
    decisions: list[DecisionResult],
    *,
    status: IncidentStatus | None,
    priority: str | None,
    source_type: SourceType | None,
    urgent: bool | None,
    sort: str,
) -> list[DecisionResult]:
    filtered = [
        decision
        for decision in decisions
        if (status is None or decision.inputs.status == status)
        and (priority is None or decision.priority.final_priority == priority)
        and (source_type is None or decision.inputs.source_type == source_type)
        and (urgent is None or decision.safety.urgent_review is urgent)
    ]
    if sort == "score_desc":
        filtered.sort(
            key=lambda item: (
                item.priority.score is None,
                -(item.priority.score or 0),
                item.incident_id,
            )
        )
    elif sort == "age_desc":
        filtered.sort(
            key=lambda item: (
                item.inputs.age_hours is None,
                -(item.inputs.age_hours or 0),
                item.incident_id,
            )
        )
    elif sort == "created_desc":
        filtered.sort(
            key=lambda item: (
                item.inputs.created_at is None,
                -(item.inputs.created_at.timestamp() if item.inputs.created_at else 0),
                item.incident_id,
            )
        )
    return filtered
