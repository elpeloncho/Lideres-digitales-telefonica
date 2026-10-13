from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.config import settings
from app.engine.config import DEFAULT_CONFIG
from app.engine.models import (
    DecisionResult,
    IncidentCategory,
    IncidentStatus,
    Priority,
    SourceType,
    VerificationStatus,
)


def to_camel(value: str) -> str:
    first, *rest = value.split("_")
    return first + "".join(part.capitalize() for part in rest)


class APIModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class FactorView(APIModel):
    value: float | None
    weight: float | None
    contribution: float | None


class FactorsView(APIModel):
    pedestrian_use: FactorView
    age: FactorView
    sensitive_location: FactorView


class IncidentView(APIModel):
    id: str
    title: str
    description: str
    category: IncidentCategory
    latitude: float | None
    longitude: float | None
    district: str | None
    neighborhood: str | None
    status: IncidentStatus
    verification: VerificationStatus | None
    assignee: str | None
    source_type: SourceType
    source_name: str
    is_simulated: bool
    priority: Priority | None
    score: float | None
    factors: FactorsView
    action: str
    age_hours: float | None
    urgent: bool
    rules: list[str]
    missing_factors: list[str]
    rationale: list[str]
    created_at: datetime | None

    @classmethod
    def from_decision(cls, decision: DecisionResult) -> "IncidentView":
        inputs = decision.inputs
        weights = decision.priority.weights
        contributions = decision.priority.contributions

        def factor(name: str, value: float | None) -> FactorView:
            return FactorView(
                value=value,
                weight=weights.get(name),
                contribution=contributions.get(name),
            )

        return cls(
            id=decision.incident_id,
            title=inputs.title,
            description=inputs.description,
            category=inputs.category,
            latitude=inputs.latitude,
            longitude=inputs.longitude,
            district=inputs.district,
            neighborhood=inputs.neighborhood,
            status=inputs.status,
            verification=inputs.verification,
            assignee=inputs.assignee,
            source_type=inputs.source_type,
            source_name=inputs.source_name,
            is_simulated=decision.is_simulated,
            priority=decision.priority.final_priority,
            score=decision.priority.score,
            factors=FactorsView(
                pedestrian_use=factor("pedestrian_use", inputs.pedestrian_use),
                age=factor("age", _age_score(decision)),
                sensitive_location=factor(
                    "sensitive_location", inputs.sensitive_location
                ),
            ),
            action=decision.recommendation.action.value,
            age_hours=inputs.age_hours,
            urgent=decision.safety.urgent_review,
            rules=[rule.id for rule in decision.safety.triggered_rules],
            missing_factors=list(decision.priority.missing_factors),
            rationale=list(decision.recommendation.rationale),
            created_at=inputs.created_at,
        )


def _age_score(decision: DecisionResult) -> float | None:
    age_hours = decision.inputs.age_hours
    if age_hours is None:
        return None
    return min(age_hours / DEFAULT_CONFIG.age_reference_hours, 1) * 100


class IncidentSort(StrEnum):
    QUEUE = "queue"
    SCORE_DESC = "score_desc"
    AGE_DESC = "age_desc"
    CREATED_DESC = "created_desc"


class IncidentListResponse(APIModel):
    items: list[IncidentView]
    total: int
    limit: int
    offset: int


class ResidentReportCreate(APIModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    category: IncidentCategory
    description: str = Field(min_length=10, max_length=500)
    latitude: float = Field(ge=settings.lat_min, le=settings.lat_max)
    longitude: float = Field(ge=settings.lon_min, le=settings.lon_max)


class WorkflowActionRequest(APIModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    action: Literal["accept", "reject", "assign", "resolve", "reopen"]
    actor: Literal["technician_demo", "operations_demo"]
    assignee: str | None = Field(default=None, min_length=2, max_length=80)
    note: str | None = Field(default=None, max_length=300)

    @model_validator(mode="after")
    def validate_action_fields(self):
        if self.action == "assign" and not self.assignee:
            raise ValueError("La acción assign requiere assignee.")
        if self.action != "assign" and self.assignee is not None:
            raise ValueError("assignee solo se admite con la acción assign.")
        return self


class DecisionResponse(APIModel):
    incident: IncidentView
    decision: DecisionResult


class DataSourceView(APIModel):
    source_type: SourceType
    count: int
    simulated: bool


class EngineMetadata(APIModel):
    engine_version: str
    config_version: str
    weights: dict[str, float]
    age_reference_hours: float
    thresholds: dict[str, float]
    safety_rules: list[dict[str, str]]
    status: str
