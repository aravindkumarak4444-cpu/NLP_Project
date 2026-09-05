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
async def test_dashboard_summary(async_client: AsyncClient):
    headers = await _get_auth_header(async_client, "dash_user@oil.in", "MANAGER")

    res = await async_client.get("/api/v1/dashboard/summary", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "total_reports" in data
    assert "sif_precursor_count" in data
    assert "risk_breakdown" in data
    assert "actions" in data


@pytest.mark.asyncio
async def test_dashboard_patterns(async_client: AsyncClient):
    headers = await _get_auth_header(async_client, "dash_patterns@oil.in", "MANAGER")

    res = await async_client.get("/api/v1/dashboard/patterns", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "top_hazards" in data
    assert "sif_trends" in data
