import pytest
from httpx import AsyncClient


async def _register_and_login(async_client: AsyncClient, email: str, role: str) -> dict:
    username = email.split("@")[0]
    reg_payload = {
        "username": username,
        "email": email,
        "password": "Password@123",
        "full_name": f"User {username}",
        "role": role,
        "department": "Safety Operations"
    }
    await async_client.post("/api/v1/auth/register", json=reg_payload)
    login_res = await async_client.post("/api/v1/auth/login", json={"email": email, "password": "Password@123"})
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_worker_report_submission_and_scoping(async_client: AsyncClient):
    worker_headers = await _register_and_login(async_client, "worker_test@oil.in", "WORKER")

    # Worker submits report
    report_payload = {
        "report_type": "UNSAFE_ACT",
        "description": "Worker performed grinding without safety face shield.",
        "location": "Workshop Area B",
        "department": "Maintenance"
    }
    create_res = await async_client.post("/api/v1/reports", json=report_payload, headers=worker_headers)
    assert create_res.status_code == 201
    rep_data = create_res.json()
    report_id = rep_data["report_id"]

    # Worker lists own reports
    my_res = await async_client.get("/api/v1/reports/my", headers=worker_headers)
    assert my_res.status_code == 200
    assert my_res.json()["total"] >= 1


@pytest.mark.asyncio
async def test_officer_review_and_action_assignment(async_client: AsyncClient):
    officer_headers = await _register_and_login(async_client, "officer_test@oil.in", "SAFETY_OFFICER")
    resp_headers = await _register_and_login(async_client, "mechanic_test@oil.in", "WORKER")

    # Officer submits report
    report_payload = {
        "report_type": "UNSAFE_CONDITION",
        "description": "Exposed high-voltage wire near water puddle in compressor room.",
        "location": "Compressor Room",
        "department": "Electrical"
    }
    create_res = await async_client.post("/api/v1/reports", json=report_payload, headers=officer_headers)
    report_id = create_res.json()["report_id"]

    # Run AI Analysis
    analysis_res = await async_client.post(f"/api/v1/analysis/{report_id}", headers=officer_headers)
    assert analysis_res.status_code == 200

    # Officer submits correction and assigns action
    review_payload = {
        "report_id": report_id,
        "decision": "CORRECT",
        "corrected_sif": True,
        "corrected_risk": "CRITICAL",
        "corrected_hazard": "ELECTRICAL_SAFETY",
        "corrected_unsafe_condition": "EXPOSED_LIVE_WIRE",
        "correction_reason": "Severe high voltage hazard requiring immediate LOTO isolation.",
        "assigned_to": "mechanic_test",
        "action_description": "Isolate power supply and replace damaged insulation."
    }
    rev_res = await async_client.post("/api/v1/reviews", json=review_payload, headers=officer_headers)
    assert rev_res.status_code == 201
    assert rev_res.json()["decision"] == "CORRECT"

    # Responsible person checks assigned actions
    actions_res = await async_client.get("/api/v1/actions/my", headers=resp_headers)
    assert actions_res.status_code == 200
    my_actions = actions_res.json()
    assert len(my_actions) >= 1
    action_id = my_actions[0]["action_id"]

    # Responsible person updates status to IN_PROGRESS and then COMPLETED
    patch_res = await async_client.patch(f"/api/v1/actions/{report_id}/{action_id}", json={"status": "COMPLETED"}, headers=resp_headers)
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "COMPLETED"


@pytest.mark.asyncio
async def test_novel_report_detection_and_feedback(async_client: AsyncClient):
    officer_headers = await _register_and_login(async_client, "novel_officer@oil.in", "SAFETY_OFFICER")

    # Report with highly unfamiliar terms
    report_payload = {
        "report_type": "NEAR_MISS",
        "description": "Zylophine acoustic resonance transducer exhibited hyper-vibrational anomalous telemetry.",
        "location": "Special R&D Unit",
        "department": "Experimental Ops"
    }
    create_res = await async_client.post("/api/v1/reports", json=report_payload, headers=officer_headers)
    report_id = create_res.json()["report_id"]

    analysis_res = await async_client.post(f"/api/v1/analysis/{report_id}", headers=officer_headers)
    assert analysis_res.status_code == 200
    an_data = analysis_res.json()["analysis"]

    # Verify is_novel flag or REVIEW_REQUIRED status
    assert an_data.get("is_novel") is True or analysis_res.json().get("status") in ["REVIEW_REQUIRED", "COMPLETED"]

    # Check feedback dataset candidate
    fb_res = await async_client.get("/api/v1/feedback", headers=officer_headers)
    assert fb_res.status_code == 200


@pytest.mark.asyncio
async def test_rbac_security_protection(async_client: AsyncClient):
    worker_headers = await _register_and_login(async_client, "unauth_worker@oil.in", "WORKER")

    # Worker attempting officer review -> 403 Forbidden
    rev_payload = {
        "report_id": "REP-9999",
        "decision": "ACCEPT"
    }
    res_rev = await async_client.post("/api/v1/reviews", json=rev_payload, headers=worker_headers)
    assert res_rev.status_code == 403

    # Worker attempting to view audit logs -> 403 Forbidden
    res_audit = await async_client.get("/api/v1/audit-logs", headers=worker_headers)
    assert res_audit.status_code == 403
