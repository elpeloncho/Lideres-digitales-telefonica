from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Priority(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class IncidentCategory(StrEnum):
    STREETLIGHT_FAILURE = "streetlight_failure"
    STREETLIGHT_FLICKERING = "streetlight_flickering"
    DAMAGED_POLE = "damaged_pole"
    ELECTRICAL_HAZARD = "electrical_hazard"
    OTHER = "other"


class IncidentStatus(StrEnum):
    REPORTED = "reported"
    PENDING = "pending"
    ASSIGNED = "assigned"
    RESOLVED = "resolved"
    REJECTED = "rejected"


class SourceType(StrEnum):
    MUNICIPAL_OPEN_DATA = "municipal_open_data"
    DERIVED = "derived"
    SYNTHETIC = "synthetic"
    RESIDENT_REPORT = "resident_report"


class VerificationStatus(StrEnum):
    UNVERIFIED = "unverified"
    VERIFIED = "verified"
    REJECTED = "rejected"
    NOT_APPLICABLE = "not_applicable"


class DataProvenance(StrEnum):
    SYNTHETIC = "synthetic"
    DERIVED = "derived"
    MUNICIPAL = "municipal"
    TECHNICIAN = "technician"
    UNKNOWN = "unknown"


class LightingState(StrEnum):
    ON = "on"
    OFF = "off"
    UNKNOWN = "unknown"


class Route(StrEnum):
    QUEUE = "queue"
    TRIAGE = "triage"


class RecommendationAction(StrEnum):
    INSPECT_URGENTLY = "inspect_urgently"
    NEEDS_TRIAGE = "needs_triage"
    VERIFY_ON_SITE = "verify_on_site"
    REPAIR_PRIORITY = "repair_priority"
    REPAIR_SCHEDULED = "repair_scheduled"


class LightingStatus(BaseModel):
    model_config = ConfigDict(frozen=True)

    state: LightingState = LightingState.UNKNOWN
    source: str = "null_provider"
    provenance: DataProvenance = DataProvenance.UNKNOWN


class DecisionInput(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str = Field(min_length=1)
    title: str = ""
    description: str = ""
    category: IncidentCategory
    status: IncidentStatus
    source_type: SourceType
    source_name: str = ""
    is_synthetic: bool = False
    verification: VerificationStatus | None = None
    assignee: str | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    district: str | None = None
    neighborhood: str | None = None
    created_at: datetime | None = None
    age_hours: float | None = Field(default=None, ge=0)
    pedestrian_use: float | None = Field(default=None, ge=0, le=100)
    sensitive_location: float | None = Field(default=None, ge=0, le=100)
    context_provenance: dict[str, DataProvenance] = Field(default_factory=dict)
    lighting_status: LightingStatus = Field(default_factory=LightingStatus)

    @field_validator("context_provenance")
    @classmethod
    def sort_context_provenance(
        cls, value: dict[str, DataProvenance]
    ) -> dict[str, DataProvenance]:
        return dict(sorted(value.items()))

    @property
    def has_valid_coordinates(self) -> bool:
        return self.latitude is not None and self.longitude is not None

    @property
    def is_simulated(self) -> bool:
        return (
            self.source_type == SourceType.SYNTHETIC
            or self.is_synthetic
            or DataProvenance.SYNTHETIC in self.context_provenance.values()
            or self.lighting_status.provenance == DataProvenance.SYNTHETIC
        )


class SafetyEffect(BaseModel):
    model_config = ConfigDict(frozen=True)

    priority_floor: Priority | None = None
    urgent_review: bool = False
    route: Route | None = None
    proposed_action: RecommendationAction | None = None


class TriggeredRule(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    reason: str
    effect: SafetyEffect


class SafetyResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    triggered_rules: tuple[TriggeredRule, ...]
    priority_floor: Priority | None = None
    urgent_review: bool = False
    route: Route = Route.QUEUE
    data_conflict: bool = False
    conflicts: tuple[str, ...] = ()


class PriorityResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    score: float | None
    score_priority: Priority | None
    final_priority: Priority | None
    complete: bool
    missing_factors: tuple[str, ...]
    weights: dict[str, float]
    contributions: dict[str, float]
    warnings: tuple[str, ...]


QueueKey = tuple[bool, int, float | None, float | None, str]


class Recommendation(BaseModel):
    model_config = ConfigDict(frozen=True)

    action: RecommendationAction
    rationale: tuple[str, ...]
    queue_key: QueueKey


class DecisionResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    incident_id: str
    engine_version: str
    config_version: str
    evaluated_at: datetime
    is_simulated: bool
    is_estimate: bool = True
    inputs: DecisionInput
    safety: SafetyResult
    priority: PriorityResult
    recommendation: Recommendation
    explanation: tuple[str, ...]
    resource_plan: None = None


class QueueComparison(BaseModel):
    model_config = ConfigDict(frozen=True)

    criterion: str
    incident_a: str
    value_a: str
    incident_b: str
    value_b: str
    explanation: str
