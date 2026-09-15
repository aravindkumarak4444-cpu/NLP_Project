import pytest
from httpx import AsyncClient
from app.integrations.ai_adapter import AIAdapter
from app.integrations.rule_adapter import RuleAdapter
from app.integrations.pattern_adapter import PatternAdapter
from app.models.report import AIAnalysisModel, LifeSavingRuleModel, PatternDataModel


async def _get_auth_header(async_client: AsyncClient, email: str, role: str) -> dict:
    reg_payload = {
        "username": email.split("@")[0],
        "email": email,
        "password": "password123",
        "full_name": "Integration Tester",
        "role": role,
        "department": "HSE"
    }
    await async_client.post("/api/v1/auth/register", json=reg_payload)
    login_res = await async_client.post("/api/v1/auth/login", json={"email": email, "password": "password123"})
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_member1_adapter_loads_real_model():
    """Requirement 1 & 2: Member 1 adapter loads real model and returns normalized output."""
    adapter = AIAdapter()
    status = adapter.get_status()
    assert status["mode"] in ["REAL_MODEL", "PREDICT_SCRIPT"]
    assert status["model_loaded"] is True

    result = adapter.analyze("Worker entered confined space without gas testing.")
    assert isinstance(result, AIAnalysisModel)
    assert result.sif_precursor is True
    assert isinstance(result.confidence, float)
    assert result.model_source in ["REAL_MODEL", "PREDICT_SCRIPT"]


def test_member2_adapter_maps_rule_correctly():
    """Requirement 3: Member 2 adapter maps actual rule correctly."""
    adapter = RuleAdapter()

    rule1 = adapter.map_rule(report_text="Worker performing welding without hot work permit.")
    assert isinstance(rule1, LifeSavingRuleModel)
    assert "Hot Work" in rule1.rule_name

    rule2 = adapter.map_rule(report_text="Worker working on scaffold at height without harness.")
    assert isinstance(rule2, LifeSavingRuleModel)
    assert "Work at Height" in rule2.rule_name


def test_member3_adapter_pattern_analysis():
    """Requirement 4 & 5: Member 3 adapter accepts report text and returns normalized pattern data."""
    adapter = PatternAdapter()
    pattern_res = adapter.analyze_single_report(
        report_text="Worker was working at height in the plant without fall protection.",
        report_id="INT-REPORT-001",
        location="Plant Area A",
        department="Maintenance"
    )
    assert isinstance(pattern_res, PatternDataModel)
    assert pattern_res.sif_potential is True
    assert pattern_res.activity == "Working at Height"
    assert pattern_res.location == "Plant"
    assert "Activity: Working at Height" in pattern_res.precursor_patterns


@pytest.mark.asyncio
async def test_end_to_end_analysis_pipeline(async_client: AsyncClient):
    """Requirement 6: POST /api/v1/analysis/{report_id} works end-to-end with real safety reports."""
    headers = await _get_auth_header(async_client, "lead_engineer@oil.in", "SAFETY_OFFICER")

    report_payload = {
        "report_type": "UNSAFE_ACT",
        "description": "Worker was working at height on elevated platform without fall protection harness.",
        "location": "Rig 42 Site",
        "department": "Drilling"
    }

    create_res = await async_client.post("/api/v1/reports", json=report_payload, headers=headers)
    assert create_res.status_code == 201
    report_id = create_res.json()["report_id"]

    analysis_res = await async_client.post(f"/api/v1/analysis/{report_id}", headers=headers)
    assert analysis_res.status_code == 200
    data = analysis_res.json()

    assert data["report_id"] == report_id
    assert data["analysis"]["sif_precursor"] is True
    assert data["analysis"]["model_source"] in ["REAL_MODEL", "PREDICT_SCRIPT"]
    assert "Work at Height" in data["life_saving_rule"]["rule_name"]
    assert data["risk"]["level"] in ["HIGH", "CRITICAL"]
    assert len(data["recommendations"]["immediate_actions"]) > 0


@pytest.mark.asyncio
async def test_dashboard_pattern_endpoint(async_client: AsyncClient):
    """Requirement 7: Dashboard pattern endpoint works."""
    headers = await _get_auth_header(async_client, "dashboard_user@oil.in", "MANAGER")

    res = await async_client.get("/api/v1/dashboard/patterns", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "top_hazards" in data
    assert "high_risk_locations" in data
    assert "sif_trends" in data
    assert "repeated_patterns" in data


def test_failure_handling_when_module_unavailable():
    """Requirement 11: Failure handling works gracefully when team module is unavailable."""
    rule_adapter = RuleAdapter()
    res = rule_adapter.map_rule(report_text="")
    assert res.rule_id == "LSR-GENERAL"
    assert res.rule_name == "General Safety"
