import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import get_store, report_store_error
from app.engine.models import IncidentStatus, SourceType
from app.repositories.json_store import (
    IncidentNotFound,
    JsonStore,
    StoreError,
    WorkflowConflict,
)
from app.schemas.api import (
    DecisionResponse,
    IncidentListResponse,
    IncidentSort,
    IncidentView,
    ResidentReportCreate,
    WorkflowActionRequest,
)
from app.services.incident_service import (
    evaluate_incident,
    filter_decisions,
    list_decisions,
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["incidents"])


@router.post("/reports", response_model=IncidentView, status_code=status.HTTP_201_CREATED)
def create_resident_report(
    request: ResidentReportCreate,
    store: Annotated[JsonStore, Depends(get_store)],
) -> IncidentView:
    try:
        incident = store.create_report(
            category=request.category.value,
            description=request.description,
            latitude=request.latitude,
            longitude=request.longitude,
        )
        return IncidentView.from_decision(evaluate_incident(incident))
    except StoreError as exc:
        report_store_error(exc)


@router.patch(
    "/incidents/{incident_id}/workflow",
    response_model=IncidentView,
)
def update_incident_workflow(
    incident_id: str,
    request: WorkflowActionRequest,
    store: Annotated[JsonStore, Depends(get_store)],
) -> IncidentView:
    try:
        incident = store.apply_workflow_action(
            incident_id,
            action=request.action,
            actor=request.actor,
            assignee=request.assignee,
            note=request.note,
        )
        return IncidentView.from_decision(evaluate_incident(incident))
    except IncidentNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except WorkflowConflict as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except StoreError as exc:
        report_store_error(exc)


@router.get("/history")
def get_history(
    store: Annotated[JsonStore, Depends(get_store)],
) -> list[dict[str, object]]:
    try:
        return [
            {
                "sequence": event["sequence"],
                "eventId": event["event_id"],
                "eventType": event["event_type"],
                "incidentId": event["incident_id"],
                "actor": event["actor"],
                "occurredAt": event["occurred_at"],
                "details": event["details"],
            }
            for event in reversed(store.list_history())
        ]
    except StoreError as exc:
        report_store_error(exc)


@router.get("/incidents", response_model=IncidentListResponse)
def get_incidents(
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
        decisions = list_decisions(store)
        filtered = filter_decisions(
            decisions,
            status=status,
            priority=priority,
            source_type=source_type,
            urgent=urgent,
            sort=sort.value,
        )
        return IncidentListResponse(
            items=[
                IncidentView.from_decision(item)
                for item in filtered[offset : offset + limit]
            ],
            total=len(filtered),
            limit=limit,
            offset=offset,
        )
    except StoreError as exc:
        report_store_error(exc)


@router.get("/incidents/{incident_id}/decision", response_model=DecisionResponse)
def get_incident_decision(
    incident_id: str,
    store: Annotated[JsonStore, Depends(get_store)],
) -> DecisionResponse:
    try:
        incident = store.get_incident(incident_id)
        if incident is None:
            raise HTTPException(status_code=404, detail="Incidencia no encontrada.")
        decision = evaluate_incident(incident)
        return DecisionResponse(
            incident=IncidentView.from_decision(decision),
            decision=decision,
        )
    except StoreError as exc:
        report_store_error(exc)


@router.get("/incidents/{incident_id}", response_model=IncidentView)
def get_incident(
    incident_id: str,
    store: Annotated[JsonStore, Depends(get_store)],
) -> IncidentView:
    try:
        incident = store.get_incident(incident_id)
        if incident is None:
            raise HTTPException(status_code=404, detail="Incidencia no encontrada.")
        return IncidentView.from_decision(evaluate_incident(incident))
    except StoreError as exc:
        report_store_error(exc)
