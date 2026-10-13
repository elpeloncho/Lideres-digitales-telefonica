def test_list_incidents_returns_flat_camel_case_engine_summary(api_client):
    response = api_client.get("/api/v1/incidents")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 8
    incident = next(item for item in body["items"] if item["id"] == "DEMO-001")
    assert incident["sourceType"] == "synthetic"
    assert incident["isSimulated"] is True
    assert incident["priority"] == "high"
    assert incident["rules"] == ["SR-02"]
    assert incident["factors"]["pedestrianUse"]["contribution"] == 38
    assert incident["district"] == "Centro"


def test_list_filter_and_pagination_work(api_client):
    response = api_client.get(
        "/api/v1/incidents",
        params={"status": "reported", "limit": 1, "offset": 0},
    )
    assert response.status_code == 200
    assert response.json()["total"] == 2
    assert len(response.json()["items"]) == 1
    assert response.json()["items"][0]["id"] in {"DEMO-003", "DEMO-006"}


def test_invalid_filter_is_rejected(api_client):
    response = api_client.get("/api/v1/incidents", params={"priority": "urgent"})
    assert response.status_code == 422


def test_detail_and_engine_snapshot(api_client):
    detail = api_client.get("/api/v1/incidents/DEMO-003")
    assert detail.status_code == 200
    assert detail.json()["action"] == "needs_triage"
    snapshot = api_client.get("/api/v1/incidents/DEMO-003/decision")
    assert snapshot.status_code == 200
    assert snapshot.json()["decision"]["engine_version"] == "0.2.0"


def test_unknown_incident_returns_404(api_client):
    assert api_client.get("/api/v1/incidents/not-found").status_code == 404


def test_queue_excludes_reports_requiring_triage_and_closed_incidents(api_client):
    response = api_client.get("/api/v1/queue")
    assert response.status_code == 200
    ids = {item["id"] for item in response.json()["items"]}
    assert "DEMO-003" not in ids
    assert "DEMO-001" in ids


def test_queue_compare_explains_decisive_criterion(api_client):
    response = api_client.get(
        "/api/v1/queue/compare", params={"a": "DEMO-002", "b": "DEMO-001"}
    )
    assert response.status_code == 200
    assert response.json()["criterion"] == "urgent_review"
    assert "revisión urgente" in response.json()["explanation"]


def test_missing_queue_compare_id_returns_404(api_client):
    response = api_client.get(
        "/api/v1/queue/compare", params={"a": "missing", "b": "DEMO-001"}
    )
    assert response.status_code == 404


def test_metadata_reports_data_sources_and_engine(api_client):
    sources = api_client.get("/api/v1/meta/data-sources")
    assert sources.status_code == 200
    assert sum(item["count"] for item in sources.json()) == 8
    engine = api_client.get("/api/v1/meta/engine")
    assert engine.status_code == 200
    assert engine.json()["engineVersion"] == "0.2.0"
    assert len(engine.json()["safetyRules"]) == 5


def test_alerts_only_include_active_high_or_urgent_incidents(api_client):
    response = api_client.get("/api/v1/alerts")
    assert response.status_code == 200
    assert {item["id"] for item in response.json()} == {
        "DEMO-001",
        "DEMO-002",
        "DEMO-005",
        "DEMO-007",
    }


def test_synthetic_report_can_be_created_and_then_validated(api_client):
    created = api_client.post(
        "/api/v1/reports",
        json={
            "category": "streetlight_failure",
            "description": "Luminaria apagada para la demo.",
            "latitude": 36.72,
            "longitude": -4.42,
        },
    )
    assert created.status_code == 201
    report = created.json()
    assert report["id"] == "RPT-0001"
    assert report["status"] == "reported"
    assert report["sourceType"] == "resident_report"
    assert report["isSimulated"] is True
    assert report["district"] == "Centro"

    validated = api_client.patch(
        f"/api/v1/incidents/{report['id']}/workflow",
        json={"action": "accept", "actor": "operations_demo"},
    )
    assert validated.status_code == 200
    assert validated.json()["status"] == "pending"
    assert validated.json()["verification"] == "verified"

    assigned = api_client.patch(
        f"/api/v1/incidents/{report['id']}/workflow",
        json={
            "action": "assign",
            "actor": "operations_demo",
            "assignee": "Lucía Díaz",
        },
    )
    assert assigned.status_code == 200
    assert assigned.json()["status"] == "assigned"
    assert assigned.json()["assignee"] == "Lucía Díaz"

    resolved = api_client.patch(
        f"/api/v1/incidents/{report['id']}/workflow",
        json={"action": "resolve", "actor": "technician_demo"},
    )
    assert resolved.status_code == 200
    assert resolved.json()["status"] == "resolved"

    events = api_client.get("/api/v1/history")
    assert events.status_code == 200
    assert [event["eventType"] for event in events.json()[:4]] == [
        "incident_resolve",
        "incident_assign",
        "incident_accept",
        "resident_report_created",
    ]


def test_report_rejects_coordinates_outside_demo_bounds(api_client):
    response = api_client.post(
        "/api/v1/reports",
        json={
            "category": "other",
            "description": "Este reporte está fuera del área de Málaga.",
            "latitude": 35.0,
            "longitude": -4.42,
        },
    )
    assert response.status_code == 422


def test_workflow_returns_conflict_for_invalid_transition(api_client):
    response = api_client.patch(
        "/api/v1/incidents/DEMO-001/workflow",
        json={"action": "resolve", "actor": "technician_demo"},
    )
    assert response.status_code == 409


def test_workflow_returns_not_found_for_unknown_incident(api_client):
    response = api_client.patch(
        "/api/v1/incidents/missing/workflow",
        json={"action": "accept", "actor": "operations_demo"},
    )
    assert response.status_code == 404
