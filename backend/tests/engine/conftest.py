from datetime import UTC, datetime

import pytest

from app.engine.models import (
    DecisionInput,
    IncidentCategory,
    IncidentStatus,
    SourceType,
)


@pytest.fixture
def evaluated_at():
    return datetime(2026, 10, 13, 10, tzinfo=UTC)


@pytest.fixture
def incident():
    return DecisionInput(
        id="INC-001",
        title="Luminaria apagada",
        category=IncidentCategory.STREETLIGHT_FAILURE,
        status=IncidentStatus.PENDING,
        source_type=SourceType.SYNTHETIC,
        source_name="test",
        latitude=36.7213,
        longitude=-4.4214,
        age_hours=26,
        pedestrian_use=95,
        sensitive_location=92,
        context_provenance={
            "pedestrian_use": "synthetic",
            "sensitive_location": "synthetic",
        },
    )
