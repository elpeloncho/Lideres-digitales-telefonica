from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependencies import get_store, report_store_error
from app.engine.models import IncidentStatus, SourceType
from app.repositories.json_store import JsonStore, StoreError
from app.schemas.api import IncidentListResponse, IncidentSort, IncidentView
from app.services.incident_service import (
    compare_incidents,
    filter_decisions,
    queue_decisions,
)

router = APIRouter(tags=["queue"])


@router.get("/queue", response_model=IncidentListResponse)
def get_queue(
    store: Annotated[JsonStore, Depends(get_store)],
    status: IncidentStatus | None = None,
    priority: str | None = Query(default=None, pattern="^(high|medium|low)$"),
    source_type: SourceType | None = None,
    urgent: bool | None = None,
    limit: int = Query(default=100, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    sort: IncidentSort = IncidentSort.QUEUE,
) -> IncidentListResponse:
    try:
        decisions = filter_decisions(
            queue_decisions(store),
            status=status,
            priority=priority,
            source_type=source_type,
            urgent=urgent,
            sort=sort.value,
        )
        return IncidentListResponse(
            items=[
                IncidentView.from_decision(item)
                for item in decisions[offset : offset + limit]
            ],
            total=len(decisions),
            limit=limit,
            offset=offset,
        )
    except StoreError as exc:
        report_store_error(exc)


@router.get("/queue/compare")
def compare_queue_items(
    store: Annotated[JsonStore, Depends(get_store)],
    a: str = Query(min_length=1),
    b: str = Query(min_length=1),
):
    try:
        result = compare_incidents(store, a, b)
        if result is None:
            raise HTTPException(status_code=404, detail="Una o ambas incidencias no existen.")
        return result
    except StoreError as exc:
        report_store_error(exc)
