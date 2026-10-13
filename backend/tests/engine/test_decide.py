import json
from datetime import datetime

import pytest
from pydantic import TypeAdapter

from app.engine.decide import decide
from app.engine.models import (
    DecisionInput,
    IncidentCategory,
    IncidentStatus,
    Priority,
    RecommendationAction,
    SourceType,
)
from app.engine.recommendation import compare, sort_decisions


def test_same_input_and_time_serialize_identically(incident, evaluated_at):
    first = decide(incident, evaluated_at).model_dump_json()
    for _ in range(20):
        assert decide(incident, evaluated_at).model_dump_json() == first


def test_queue_key_serializes_as_the_documented_ordering_tuple(
    incident, evaluated_at
):
    serialized = json.loads(decide(incident, evaluated_at).model_dump_json())
    assert serialized["recommendation"]["queue_key"] == [
        False,
        3,
        92.13,
        26.0,
        "INC-001",
    ]


def test_engine_uses_explicit_evaluation_time(incident, evaluated_at):
    result = decide(incident, evaluated_at)
    later = decide(
        incident.model_copy(update={"age_hours": None, "created_at": evaluated_at}),
        datetime.fromisoformat("2026-10-13T11:00:00+00:00"),
    )
    assert result.inputs.age_hours == 26
    assert later.inputs.age_hours == 1


def test_naive_evaluation_time_is_rejected(incident):
    with pytest.raises(ValueError, match="zona horaria"):
        decide(incident, datetime(2026, 10, 13, 10))


def test_priority_floor_and_contributing_rule_are_explained(incident, evaluated_at):
    incident = incident.model_copy(
        update={"pedestrian_use": 0, "age_hours": 0, "sensitive_location": 0}
    )
    incident = incident.model_copy(update={"category": IncidentCategory.DAMAGED_POLE})
    result = decide(incident, evaluated_at)
    assert result.safety.priority_floor == Priority.HIGH
    assert result.priority.final_priority == Priority.HIGH
    assert result.safety.conflicts
    assert any("mínimo de prioridad high" in line for line in result.recommendation.rationale)
    assert any("Uso peatonal estimado" in line for line in result.explanation)


def test_no_context_for_report_is_never_low_by_default(incident, evaluated_at):
    incident = incident.model_copy(
        update={
            "id": "REPORT-1",
            "source_type": SourceType.RESIDENT_REPORT,
            "status": IncidentStatus.REPORTED,
            "verification": "unverified",
            "pedestrian_use": None,
            "age_hours": None,
            "sensitive_location": None,
            "context_provenance": {},
        }
    )
    result = decide(incident, evaluated_at)
    assert result.priority.score is None
    assert result.priority.final_priority is None
    assert result.recommendation.action == RecommendationAction.NEEDS_TRIAGE
    assert result.safety.route.value == "triage"


def test_simulated_provenance_is_exposed(incident, evaluated_at):
    assert decide(incident, evaluated_at).is_simulated is True
    real = incident.model_copy(
        update={
            "source_type": SourceType.MUNICIPAL_OPEN_DATA,
            "context_provenance": {
                "pedestrian_use": "municipal",
                "sensitive_location": "municipal",
            },
        }
    )
    assert decide(real, evaluated_at).is_simulated is False


def test_context_provenance_key_order_does_not_change_serialization(incident, evaluated_at):
    reversed_provenance = incident.model_copy(
        update={"context_provenance": dict(reversed(list(incident.context_provenance.items())))}
    )
    assert decide(incident, evaluated_at).model_dump_json() == decide(
        reversed_provenance, evaluated_at
    ).model_dump_json()


def test_queue_order_uses_priority_and_id_as_deterministic_tiebreaker(
    incident, evaluated_at
):
    one = decide(incident.model_copy(update={"id": "B"}), evaluated_at)
    two = decide(incident.model_copy(update={"id": "A"}), evaluated_at)
    assert [item.incident_id for item in sort_decisions([one, two])] == ["A", "B"]


def test_urgent_decision_is_ahead_of_high_score_decision(incident, evaluated_at):
    urgent = decide(
        incident.model_copy(update={"category": IncidentCategory.DAMAGED_POLE}),
        evaluated_at,
    )
    non_urgent = decide(
        incident.model_copy(
            update={"id": "INC-002", "category": IncidentCategory.OTHER}
        ),
        evaluated_at,
    )
    assert sort_decisions([non_urgent, urgent]) == [urgent, non_urgent]
    comparison = compare(urgent, non_urgent)
    assert comparison.criterion == "urgent_review"
    assert "va antes por revisión urgente" in comparison.explanation


def test_missing_score_sorts_after_scores_at_the_same_final_priority(
    incident, evaluated_at
):
    with_score = decide(
        incident.model_copy(update={"category": IncidentCategory.DAMAGED_POLE}),
        evaluated_at,
    )
    without_score = decide(
        incident.model_copy(
            update={
                "id": "INC-002",
                "category": IncidentCategory.DAMAGED_POLE,
                "pedestrian_use": None,
                "age_hours": None,
                "sensitive_location": None,
            }
        ),
        evaluated_at,
    )
    assert [item.incident_id for item in sort_decisions([without_score, with_score])] == [
        "INC-001",
        "INC-002",
    ]


def test_queue_rejects_duplicate_ids(incident, evaluated_at):
    result = decide(incident, evaluated_at)
    with pytest.raises(ValueError, match="identificadores duplicados"):
        sort_decisions([result, result])


def test_seed_file_contains_only_explicitly_tagged_records():
    from pathlib import Path

    data_path = Path(__file__).parents[3] / "data" / "synthetic" / "seed.json"
    records = TypeAdapter(list[DecisionInput]).validate_python(
        json.loads(data_path.read_text())
    )
    assert records
    assert all(record.is_simulated for record in records)
