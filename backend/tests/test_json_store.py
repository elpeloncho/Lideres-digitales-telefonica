import json
from pathlib import Path

import pytest

from app.repositories.json_store import (
    IncidentNotFound,
    JsonStore,
    StoreError,
    WorkflowConflict,
)


@pytest.fixture
def store(tmp_path: Path):
    root = Path(__file__).parents[2]
    return JsonStore(tmp_path / "store", root / "data" / "synthetic" / "seed.json")


def test_first_read_initializes_persistent_seed_and_history(store):
    incidents = store.list_incidents()
    assert len(incidents) == 3
    assert store.incidents_path.is_file()
    assert store.history_path.is_file()
    assert len(store.list_history()) == 3
    assert json.loads(store.incidents_path.read_text())["revision"] == 3


def test_restart_reads_same_seeded_incidents(store):
    first = [incident.model_dump(mode="json") for incident in store.list_incidents()]
    restarted = JsonStore(store.store_dir, store.seed_file)
    second = [incident.model_dump(mode="json") for incident in restarted.list_incidents()]
    assert second == first


def test_corrupt_json_is_reported_without_being_overwritten(store):
    store.store_dir.mkdir(parents=True)
    store.incidents_path.write_text("{broken", encoding="utf-8")
    with pytest.raises(StoreError, match="no se sobrescribieron"):
        store.list_incidents()
    assert store.incidents_path.read_text(encoding="utf-8") == "{broken"


def test_inconsistent_history_and_revision_are_reported(store):
    store.list_incidents()
    store.history_path.write_text("", encoding="utf-8")
    with pytest.raises(StoreError, match="no son coherentes"):
        store.list_incidents()


def test_incomplete_store_is_not_silently_reseeded(store):
    store.store_dir.mkdir(parents=True)
    store.history_path.write_text("{broken\n", encoding="utf-8")
    with pytest.raises(StoreError, match="incompleto"):
        store.list_incidents()
    assert store.history_path.read_text(encoding="utf-8") == "{broken\n"


def test_report_and_workflow_actions_are_persisted_and_audited(store):
    report = store.create_report(
        category="streetlight_failure",
        description="Luminaria apagada para prueba sintética.",
        latitude=36.72,
        longitude=-4.42,
    )
    assert report.id == "RPT-0001"
    assert report.status.value == "reported"
    assert report.is_simulated

    validated = store.apply_workflow_action(
        report.id,
        action="accept",
        actor="operations_demo",
    )
    assigned = store.apply_workflow_action(
        report.id,
        action="assign",
        actor="operations_demo",
        assignee="Lucía Díaz",
    )
    resolved = store.apply_workflow_action(
        report.id,
        action="resolve",
        actor="technician_demo",
    )

    assert validated.verification.value == "verified"
    assert assigned.assignee == "Lucía Díaz"
    assert resolved.status.value == "resolved"
    assert [event["event_type"] for event in store.list_history()[-4:]] == [
        "resident_report_created",
        "incident_accept",
        "incident_assign",
        "incident_resolve",
    ]
    restarted = JsonStore(store.store_dir, store.seed_file)
    assert restarted.get_incident(report.id).status.value == "resolved"
    assert len(restarted.list_history()) == 7


def test_workflow_rejects_invalid_transitions(store):
    with pytest.raises(WorkflowConflict, match="no está permitida"):
        store.apply_workflow_action(
            "DEMO-001",
            action="resolve",
            actor="technician_demo",
        )


def test_workflow_reports_missing_incident(store):
    with pytest.raises(IncidentNotFound):
        store.apply_workflow_action(
            "missing",
            action="accept",
            actor="operations_demo",
        )
