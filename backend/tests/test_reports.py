import pytest
from httpx import AsyncClient


async def _get_auth_header(async_client: AsyncClient, email: str, role: str) -> dict:
    reg_payload = {
        "username": email.split("@")[0],
        "email": email,
        "password": "password123",
        "full_name": "Test User",
        "role": role,
        "department": "HSE"
    }
    await async_client.post("/api/v1/auth/register", json=reg_payload)
    login_res = await async_client.post("/api/v1/auth/login", json={"email": email, "password": "password123"})
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_create_and_get_report(async_client: AsyncClient):
    headers = await _get_auth_header(async_client, "reporter@oil.in", "WORKER")

    report_payload = {
        "report_type": "NEAR_MISS",
        "description": "Worker entered confined space vessel without performing mandatory oxygen and gas test.",
        "location": "Rig No. 4, Digboi Field",
        "department": "Drilling Operations"
    }

    create_res = await async_client.post("/api/v1/reports", json=report_payload, headers=headers)
    assert create_res.status_code == 201
    rep_data = create_res.json()
    assert rep_data["report_type"] == "NEAR_MISS"
    assert rep_data["status"] == "SUBMITTED"
    report_id = rep_data["report_id"]

    get_res = await async_client.get(f"/api/v1/reports/{report_id}", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["report_id"] == report_id


@pytest.mark.asyncio
async def test_list_reports_pagination(async_client: AsyncClient):
    headers = await _get_auth_header(async_client, "lister@oil.in", "WORKER")

    list_res = await async_client.get("/api/v1/reports?page=1&limit=10", headers=headers)
    assert list_res.status_code == 200
    data = list_res.json()
    assert "items" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_invalid_status_transition(async_client: AsyncClient):
    headers = await _get_auth_header(async_client, "officer_valid@oil.in", "SAFETY_OFFICER")

    report_payload = {
        "report_type": "UNSAFE_ACT",
        "description": "Scaffolding work at 5 meters height without safety belt.",
        "location": "Tank Farm 2",
        "department": "Maintenance"
    }
    create_res = await async_client.post("/api/v1/reports", json=report_payload, headers=headers)
    report_id = create_res.json()["report_id"]

    # Try invalid transition from SUBMITTED directly to VERIFIED
    status_payload = {"status": "VERIFIED"}
    patch_res = await async_client.patch(f"/api/v1/reports/{report_id}/status", json=status_payload, headers=headers)
    assert patch_res.status_code == 400
    assert patch_res.json()["error"]["code"] == "INVALID_STATUS_TRANSITION"
