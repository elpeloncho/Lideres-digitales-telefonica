from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import get_store, report_store_error
from app.repositories.json_store import JsonStore, StoreError
from app.schemas.api import IncidentView
from app.services.incident_service import list_decisions

router = APIRouter(tags=["alerts"])


@router.get("/alerts", response_model=list[IncidentView])
def get_alerts(store: Annotated[JsonStore, Depends(get_store)]) -> list[IncidentView]:
    try:
        return [
            IncidentView.from_decision(decision)
            for decision in list_decisions(store, include_closed=False)
            if decision.priority.final_priority is not None
            if decision.safety.urgent_review
            or decision.priority.final_priority.value == "high"
        ]
    except StoreError as exc:
        report_store_error(exc)
