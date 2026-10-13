from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.config import settings


class IncidentStatus(StrEnum):
    REPORTED = "reported"    # reporte de vecino pendiente de triaje
    PENDING = "pending"
    ASSIGNED = "assigned"
    RESOLVED = "resolved"
    REJECTED = "rejected"


class SourceType(StrEnum):
    MUNICIPAL_OPEN_DATA = "municipal_open_data"
    DERIVED = "derived"
    SYNTHETIC = "synthetic"
    RESIDENT_REPORT = "resident_report"


class Category(StrEnum):
    STREETLIGHT_FAILURE = "streetlight_failure"
    STREETLIGHT_FLICKERING = "streetlight_flickering"
    DAMAGED_POLE = "damaged_pole"
    ELECTRICAL_HAZARD = "electrical_hazard"
    OTHER = "other"


class Context(BaseModel):
    # None = dato ausente. No se convierte en 0 de forma silenciosa.
    pedestrian_use: float | None = Field(default=None, ge=0, le=100)
    sensitive_location: float | None = Field(default=None, ge=0, le=100)


class _Located(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)

    @model_validator(mode="after")
    def _inside_demo_area(self):
        if not (
            settings.lat_min <= self.latitude <= settings.lat_max
            and settings.lon_min <= self.longitude <= settings.lon_max
        ):
            raise ValueError("Coordenadas fuera del ámbito de Málaga definido para la demo")
        return self


class Incident(_Located):
    id: str
    title: str
    category: Category
    description: str
    status: IncidentStatus
    source_type: SourceType
    source_name: str
    observed_at: datetime | None = None
    created_at: datetime
    age_hours: float | None = Field(default=None, ge=0)
    context: Context = Field(default_factory=Context)


class ResidentReportCreate(_Located):
    """Entrada del formulario de residentes. Sin datos personales; texto no confiable."""

    model_config = ConfigDict(str_strip_whitespace=True)

    category: Category
    description: str = Field(min_length=10, max_length=500)