from app.engine.config import EngineConfig
from app.engine.decide import decide
from app.engine.models import (
    DecisionInput,
    IncidentCategory,
    IncidentStatus,
    LightingState,
    LightingStatus,
    Priority,
    RecommendationAction,
    Route,
    SourceType,
    VerificationStatus,
)
from app.engine.safety_rules import evaluate_safety_rules


def test_sr01_forces_high_and_urgent_even_when_score_is_zero(incident, evaluated_at):
    incident = incident.model_copy(
        update={
            "category": IncidentCategory.ELECTRICAL_HAZARD,
            "pedestrian_use": 0,
            "age_hours": 0,
            "sensitive_location": 0,
        }
    )
    result = decide(incident, evaluated_at)
    assert result.priority.score_priority == Priority.LOW
    assert result.priority.final_priority == Priority.HIGH
    assert result.safety.urgent_review is True
    assert result.recommendation.action == RecommendationAction.INSPECT_URGENTLY


def test_sr02_threshold_boundary_is_inclusive(incident):
    at_threshold = incident.model_copy(update={"sensitive_location": 90})
    below_threshold = incident.model_copy(update={"sensitive_location": 89})
    assert "SR-02" in {
        rule.id for rule in evaluate_safety_rules(at_threshold).triggered_rules
    }
    assert "SR-02" not in {
        rule.id for rule in evaluate_safety_rules(below_threshold).triggered_rules
    }


def test_sr03_sends_missing_coordinates_to_triage(incident):
    result = evaluate_safety_rules(incident.model_copy(update={"latitude": None}))
    assert result.route == Route.TRIAGE
    assert "SR-03" in {rule.id for rule in result.triggered_rules}


def test_sr03_routes_an_incident_with_no_factors_to_triage(incident):
    result = evaluate_safety_rules(
        incident.model_copy(
            update={
                "pedestrian_use": None,
                "age_hours": None,
                "sensitive_location": None,
            }
        )
    )
    assert result.route == Route.TRIAGE


def test_sr04_unverified_resident_report_requires_triage(incident):
    result = evaluate_safety_rules(
        incident.model_copy(
            update={
                "source_type": SourceType.RESIDENT_REPORT,
                "verification": VerificationStatus.UNVERIFIED,
            }
        )
    )
    assert result.route == Route.TRIAGE
    assert "SR-04" in {rule.id for rule in result.triggered_rules}


def test_sr05_marks_contradictory_lighting_status(incident):
    incident = incident.model_copy(
        update={
            "lighting_status": LightingStatus(
                state=LightingState.ON,
                source="simulated_provider",
                provenance="synthetic",
            )
        }
    )
    result = evaluate_safety_rules(incident)
    assert result.route == Route.TRIAGE
    assert result.data_conflict is True
    assert "SR-05" in {rule.id for rule in result.triggered_rules}


def test_urgent_review_and_triage_are_both_preserved(incident, evaluated_at):
    incident = incident.model_copy(
        update={
            "category": IncidentCategory.DAMAGED_POLE,
            "source_type": SourceType.RESIDENT_REPORT,
            "verification": VerificationStatus.UNVERIFIED,
            "status": IncidentStatus.REPORTED,
        }
    )
    result = decide(incident, evaluated_at)
    assert result.safety.urgent_review is True
    assert result.safety.route == Route.TRIAGE
    assert result.recommendation.action == RecommendationAction.INSPECT_URGENTLY
    assert result.safety.conflicts


def test_conflicting_proposed_actions_are_reported(incident):
    incident = incident.model_copy(
        update={
            "id": "NO-COORDS-HAZARD",
            "category": IncidentCategory.DAMAGED_POLE,
            "latitude": None,
            "longitude": None,
        }
    )
    result = evaluate_safety_rules(incident)
    assert {rule.id for rule in result.triggered_rules} >= {"SR-01", "SR-03"}
    assert any("acciones" in conflict for conflict in result.conflicts)


def test_safety_floor_is_not_affected_by_scoring_configuration(incident, evaluated_at):
    incident = incident.model_copy(
        update={
            "category": IncidentCategory.DAMAGED_POLE,
            "pedestrian_use": 0,
            "age_hours": 0,
            "sensitive_location": 0,
        }
    )
    config = EngineConfig(high_threshold=100)
    result = decide(incident, evaluated_at, config)
    assert result.priority.score_priority == Priority.LOW
    assert result.priority.final_priority == Priority.HIGH


def test_missing_coordinates_are_accepted_as_triage_input():
    incident = DecisionInput(
        id="NO-COORDS",
        category=IncidentCategory.OTHER,
        status=IncidentStatus.PENDING,
        source_type=SourceType.SYNTHETIC,
        latitude=None,
        longitude=None,
        pedestrian_use=40,
    )
    assert evaluate_safety_rules(incident).route == Route.TRIAGE
