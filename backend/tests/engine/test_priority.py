import pytest
from pydantic import ValidationError

from app.engine.config import EngineConfig
from app.engine.models import Priority
from app.engine.priority import calculate_priority, classify


def test_max_factors_give_100():
    result = calculate_priority(100, 30, 100)
    assert result.score == pytest.approx(100)
    assert result.score_priority == Priority.HIGH
    assert result.final_priority == Priority.HIGH
    assert result.complete is True


def test_age_beyond_reference_is_capped():
    assert calculate_priority(100, 300, 100).score == pytest.approx(100)


def test_min_factors_give_0():
    result = calculate_priority(0, 0, 0)
    assert result.score == pytest.approx(0)
    assert result.score_priority == Priority.LOW


def test_age_contribution_never_decreases():
    previous = -1.0
    for hours in range(0, 100, 5):
        current = calculate_priority(50, hours, 50).contributions["age"]
        assert current >= previous
        previous = current


def test_changing_weights_changes_score():
    default = calculate_priority(100, 0, 0).score
    config = EngineConfig(
        weight_pedestrian_use=0.6,
        weight_age=0.2,
        weight_sensitive_location=0.2,
    )
    changed = calculate_priority(100, 0, 0, config).score
    assert default == pytest.approx(40)
    assert changed == pytest.approx(60)


def test_changing_threshold_changes_priority():
    assert calculate_priority(75, 22.5, 75).score_priority == Priority.HIGH
    strict = EngineConfig(high_threshold=80)
    assert calculate_priority(75, 22.5, 75, strict).score_priority == Priority.MEDIUM


@pytest.mark.parametrize(
    "args",
    [
        (101, 10, 50),
        (-1, 10, 50),
        (50, 10, 101),
        (50, -5, 50),
        (float("nan"), 10, 50),
        (50, float("inf"), 50),
    ],
)
def test_out_of_range_values_are_rejected(args):
    with pytest.raises(ValueError):
        calculate_priority(*args)


def test_missing_factor_is_reported_and_weights_are_redistributed():
    result = calculate_priority(100, 30, None)
    assert result.complete is False
    assert result.score == pytest.approx(100)
    assert "sensitive_location" in result.missing_factors
    assert "sensitive_location" not in result.contributions
    assert result.weights == {"pedestrian_use": pytest.approx(2 / 3), "age": pytest.approx(1 / 3)}
    assert any("importancia del entorno" in warning for warning in result.warnings)


def test_no_factors_gives_no_score_or_score_priority():
    result = calculate_priority(None, None, None)
    assert result.score is None
    assert result.score_priority is None
    assert result.final_priority is None
    assert result.complete is False


def test_no_factors_still_obeys_safety_floor():
    result = calculate_priority(None, None, None, priority_floor=Priority.HIGH)
    assert result.score is None
    assert result.final_priority == Priority.HIGH


def test_classification_boundaries():
    config = EngineConfig()
    assert classify(75, config) == Priority.HIGH
    assert classify(74.99, config) == Priority.MEDIUM
    assert classify(55, config) == Priority.MEDIUM
    assert classify(54.99, config) == Priority.LOW


def test_weights_must_sum_to_one():
    with pytest.raises(ValidationError):
        EngineConfig(weight_age=0.5)


def test_thresholds_must_be_ordered():
    with pytest.raises(ValidationError):
        EngineConfig(high_threshold=50, medium_threshold=60)
