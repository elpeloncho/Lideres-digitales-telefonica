from pydantic import BaseModel, ConfigDict, Field, model_validator


class EngineConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    config_version: str = "2026-10-13-default"
    weight_pedestrian_use: float = Field(default=0.40, ge=0, le=1)
    weight_age: float = Field(default=0.20, ge=0, le=1)
    weight_sensitive_location: float = Field(default=0.40, ge=0, le=1)
    age_reference_hours: float = Field(default=30, gt=0)
    high_threshold: float = Field(default=75, ge=0, le=100)
    medium_threshold: float = Field(default=55, ge=0, le=100)
    sensitive_location_threshold: float = Field(default=90, ge=0, le=100)

    @model_validator(mode="after")
    def validate_configuration(self) -> "EngineConfig":
        weights = (
            self.weight_pedestrian_use,
            self.weight_age,
            self.weight_sensitive_location,
        )
        if abs(sum(weights) - 1.0) > 1e-9:
            raise ValueError(f"Los pesos deben sumar 1 (suman {sum(weights)})")
        if self.medium_threshold >= self.high_threshold:
            raise ValueError("medium_threshold debe ser menor que high_threshold")
        return self


DEFAULT_CONFIG = EngineConfig()
