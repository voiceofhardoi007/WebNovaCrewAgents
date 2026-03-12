from fastapi.testclient import TestClient

import main


client = TestClient(main.app)


def setup_function() -> None:
    main.company_state = None


def test_bootstrap_and_dashboard_flow() -> None:
    bootstrap = client.post(
        "/company/bootstrap",
        json={"company_name": "Web Nova Crew", "mission": "Autonomous web innovation"},
    )
    assert bootstrap.status_code == 200
    data = bootstrap.json()
    assert data["name"] == "Web Nova Crew"
    assert len(data["agents"]) >= 7

    create_task = client.post(
        "/tasks/create",
        json={
            "title": "Launch AI marketing landing page",
            "description": "Generate design and deploy page",
            "priority": 1,
            "requested_by": "client-success",
            "deliverables": ["wireframe", "copy", "deployed-url"],
        },
    )
    assert create_task.status_code == 200

    cycle_1 = client.post("/run-cycle")
    assert cycle_1.status_code == 200

    cycle_2 = client.post("/run-cycle")
    assert cycle_2.status_code == 200

    cycle_3 = client.post("/run-cycle")
    assert cycle_3.status_code == 200
    assert len(cycle_3.json()["completed"]) >= 1

    dashboard = client.get("/dashboard")
    assert dashboard.status_code == 200
    metrics = dashboard.json()
    assert metrics["tasks_completed"] >= 1
    assert metrics["agent_count"] >= 7


def test_status_requires_bootstrap() -> None:
    response = client.get("/company/status")
    assert response.status_code == 400
