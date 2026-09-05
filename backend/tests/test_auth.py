import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user(async_client: AsyncClient):
    payload = {
        "username": "worker_john",
        "email": "john@oil.in",
        "password": "securepassword123",
        "full_name": "John Doe",
        "role": "WORKER",
        "department": "Drilling Operations"
    }

    res = await async_client.post("/api/v1/auth/register", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["username"] == "worker_john"
    assert data["email"] == "john@oil.in"
    assert "user_id" in data
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_login_user(async_client: AsyncClient):
    # Register first
    payload = {
        "username": "safety_officer_sam",
        "email": "sam@oil.in",
        "password": "officerpassword123",
        "full_name": "Sam Safety",
        "role": "SAFETY_OFFICER",
        "department": "HSE Department"
    }
    await async_client.post("/api/v1/auth/register", json=payload)

    # Login
    login_payload = {
        "email": "sam@oil.in",
        "password": "officerpassword123"
    }
    res = await async_client.post("/api/v1/auth/login", json=login_payload)
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_get_current_user_me(async_client: AsyncClient):
    # Register & Login
    reg_payload = {
        "username": "manager_mike",
        "email": "mike@oil.in",
        "password": "managerpassword123",
        "full_name": "Mike Manager",
        "role": "MANAGER",
        "department": "Production"
    }
    await async_client.post("/api/v1/auth/register", json=reg_payload)

    login_res = await async_client.post("/api/v1/auth/login", json={"email": "mike@oil.in", "password": "managerpassword123"})
    token = login_res.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    me_res = await async_client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["email"] == "mike@oil.in"
    assert me_data["role"] == "MANAGER"


@pytest.mark.asyncio
async def test_unauthenticated_request(async_client: AsyncClient):
    res = await async_client.post("/api/v1/reports", json={})
    assert res.status_code == 401
    data = res.json()
    assert data["success"] is False
    assert data["error"]["code"] == "UNAUTHORIZED"
    assert data["error"]["message"] == "Invalid or expired authentication token."


@pytest.mark.asyncio
async def test_token_decoding_with_bearer_prefix():
    from app.auth.jwt import create_access_token, decode_access_token
    token = create_access_token({"sub": "USR-123", "role": "WORKER"})
    
    # Normal decoding
    data1 = decode_access_token(token)
    assert data1 is not None
    assert data1.user_id == "USR-123"

    # Decoding when Bearer prefix is attached
    data2 = decode_access_token(f"Bearer {token}")
    assert data2 is not None
    assert data2.user_id == "USR-123"


@pytest.mark.asyncio
async def test_token_subject_reading_variations():
    from app.auth.jwt import create_access_token, decode_access_token

    # Numeric sub
    token1 = create_access_token({"sub": 99999, "role": "WORKER"})
    res1 = decode_access_token(token1)
    assert res1 is not None
    assert res1.user_id == "99999"

    # Fallback claim key 'user_id'
    token2 = create_access_token({"user_id": "USR-888", "role": "SAFETY_OFFICER"})
    res2 = decode_access_token(token2)
    assert res2 is not None
    assert res2.user_id == "USR-888"

    # Quoted token strings
    res3 = decode_access_token(f'"{token1}"')
    assert res3 is not None
    assert res3.user_id == "99999"


@pytest.mark.asyncio
async def test_token_clock_skew_leeway():
    import jwt
    from datetime import datetime, timedelta, timezone
    from app.config import settings
    from app.auth.jwt import decode_access_token

    # Token issued 5 seconds in future (simulating sub-second clock drift)
    future_iat = datetime.now(timezone.utc) + timedelta(seconds=5)
    exp = future_iat + timedelta(minutes=480)
    payload = {"sub": "USR-999", "role": "WORKER", "iat": future_iat, "exp": exp}
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded.user_id == "USR-999"


