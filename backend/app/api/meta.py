from collections import Counter
from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import get_store, report_store_error
from app.engine.config import DEFAULT_CONFIG
from app.engine.decide import ENGINE_VERSION
from app.repositories.json_store import JsonStore, StoreError
from app.schemas.api import DataSourceView, EngineMetadata

router = APIRouter(prefix="/meta", tags=["metadata"])


@router.get("/data-sources", response_model=list[DataSourceView])
def get_data_sources(
    store: Annotated[JsonStore, Depends(get_store)],
) -> list[DataSourceView]:
    try:
        counts = Counter(item.source_type for item in store.list_incidents())
    except StoreError as exc:
        report_store_error(exc)
    return [
        DataSourceView(
            source_type=source_type,
            count=count,
            simulated=source_type.value in {"synthetic", "resident_report"},
        )
        for source_type, count in sorted(counts.items(), key=lambda item: item[0].value)
    ]


@router.get("/engine", response_model=EngineMetadata)
def get_engine_metadata() -> EngineMetadata:
    return EngineMetadata(
        engine_version=ENGINE_VERSION,
        config_version=DEFAULT_CONFIG.config_version,
        weights={
            "pedestrian_use": DEFAULT_CONFIG.weight_pedestrian_use,
            "age": DEFAULT_CONFIG.weight_age,
            "sensitive_location": DEFAULT_CONFIG.weight_sensitive_location,
        },
        age_reference_hours=DEFAULT_CONFIG.age_reference_hours,
        thresholds={
            "high": DEFAULT_CONFIG.high_threshold,
            "medium": DEFAULT_CONFIG.medium_threshold,
            "sensitive_location": DEFAULT_CONFIG.sensitive_location_threshold,
        },
        safety_rules=[
            {"id": f"SR-{index:02}", "status": "experimental"}
            for index in range(1, 6)
        ],
        status="experimental",
    )
