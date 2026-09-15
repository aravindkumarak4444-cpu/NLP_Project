import pytest
import os
import tempfile
import joblib
from httpx import AsyncClient
from app.integrations.ai_adapter import (
    AIAdapter,
    RealMLModelAdapter,
    PredictScriptAdapter,
    FallbackAdapter,
    normalize_output
)


class TopLevelDummyModel:
    def predict(self, texts):
        return [{"sif_precursor": True, "confidence": 0.96, "hazard_category": "CONFINED_SPACE"}]


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
async def test_ai_analysis_pipeline(async_client: AsyncClient):
    headers = await _get_auth_header(async_client, "analyst@oil.in", "SAFETY_OFFICER")

    report_payload = {
        "report_type": "NEAR_MISS",
        "description": "Technician entered confined space vessel without gas testing. Oxygen levels were unknown.",
        "location": "Processing Plant B",
        "department": "Operations"
    }
    create_res = await async_client.post("/api/v1/reports", json=report_payload, headers=headers)
    report_id = create_res.json()["report_id"]

    analysis_res = await async_client.post(f"/api/v1/analysis/{report_id}", headers=headers)
    assert analysis_res.status_code == 200
    data = analysis_res.json()

    assert data["report_id"] == report_id
    assert "analysis" in data
    assert data["analysis"]["sif_precursor"] is True
    assert data["analysis"]["hazard_category"] == "CONFINED_SPACE"
    assert data["analysis"]["model_source"] in ["FALLBACK", "REAL_MODEL", "PREDICT_SCRIPT"]
    assert data["risk"]["level"] in ["HIGH", "CRITICAL"]
    assert data["life_saving_rule"]["rule_id"] == "LSR-01"
    assert len(data["recommendations"]["immediate_actions"]) > 0


@pytest.mark.asyncio
async def test_ai_status_endpoint(async_client: AsyncClient):
    res = await async_client.get("/api/v1/analysis/status")
    assert res.status_code == 200
    data = res.json()
    assert "mode" in data
    assert "model_loaded" in data
    assert data["mode"] in ["FALLBACK", "REAL_MODEL", "PREDICT_SCRIPT"]


def test_output_normalization():
    # 1. Test Boolean input
    res_bool = normalize_output(True, model_source="REAL_MODEL")
    assert res_bool.sif_precursor is True
    assert res_bool.model_source == "REAL_MODEL"

    # 2. Test Dict input
    raw_dict = {
        "sif_precursor": True,
        "confidence": 0.95,
        "hazard_category": "HOT_WORK",
        "severity": 4
    }
    res_dict = normalize_output(raw_dict, model_source="REAL_MODEL")
    assert res_dict.sif_precursor is True
    assert res_dict.confidence == 0.95
    assert res_dict.hazard_category == "HOT_WORK"
    assert res_dict.model_source == "REAL_MODEL"

    # 3. Test Tuple input (label, confidence)
    res_tuple = normalize_output(("SIF", 0.91), model_source="PREDICT_SCRIPT")
    assert res_tuple.sif_precursor is True
    assert res_tuple.confidence == 0.91
    assert res_tuple.model_source == "PREDICT_SCRIPT"

    # 4. Test String label input
    res_str = normalize_output("WORKING_AT_HEIGHT", model_source="PREDICT_SCRIPT")
    assert res_str.sif_precursor is True
    assert res_str.hazard_category == "WORKING_AT_HEIGHT"


def test_simulated_real_ml_model_adapter():
    """SIMULATION ONLY: Tests RealMLModelAdapter with a temporary mock model binary."""
    with tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        joblib.dump(TopLevelDummyModel(), tmp_path)
        adapter = RealMLModelAdapter(tmp_path, "ml/models/mock_model.pkl")
        assert adapter.get_info()["model_loaded"] is True
        assert adapter.get_info()["mode"] == "REAL_MODEL"

        res = adapter.analyze("Worker entered vessel without permit")
        assert res.sif_precursor is True
        assert res.confidence == 0.96
        assert res.model_source == "REAL_MODEL"
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def test_simulated_predict_script_adapter():
    """SIMULATION ONLY: Tests PredictScriptAdapter with a temporary mock predict.py module."""
    script_content = """
def predict(text):
    return {
        "sif_precursor": True,
        "confidence": 0.94,
        "hazard_category": "ELECTRICAL_SAFETY",
        "evidence": ["High voltage wire exposed"]
    }
"""
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as tmp:
        tmp.write(script_content)
        tmp_path = tmp.name

    try:
        adapter = PredictScriptAdapter(tmp_path, "ai_model/src/mock_predict.py")
        assert adapter.get_info()["model_loaded"] is True
        assert adapter.get_info()["mode"] == "PREDICT_SCRIPT"

        res = adapter.analyze("Live wire hanging in substation")
        assert res.sif_precursor is True
        assert res.confidence == 0.94
        assert res.hazard_category == "ELECTRICAL_SAFETY"
        assert res.model_source == "PREDICT_SCRIPT"
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def test_invalid_model_handling():
    """Tests error reporting when a corrupted model binary fails to load."""
    with tempfile.NamedTemporaryFile(suffix=".pkl", mode="w", delete=False) as tmp:
        tmp.write("corrupted non-pickle binary data")
        tmp_path = tmp.name

    try:
        adapter = RealMLModelAdapter(tmp_path, "ml/models/corrupted.pkl")
        info = adapter.get_info()
        assert info["model_loaded"] is False
        assert "REAL MODEL DETECTED BUT FAILED TO LOAD" in info["reason"]
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def test_safety_context_safe_compliance():
    adapter = AIAdapter()
    res = adapter.analyze("Worker completed gas testing before entering confined space and used required PPE.")
    assert res.sif_precursor is False
    assert res.context_type == "SAFE_COMPLIANCE"
    assert res.context_adjustment_reason is not None
    assert "Safety Context Adjustment" in res.context_adjustment_reason
    assert res.unsafe_act is None

    from app.services.risk_service import RiskService
    risk = RiskService().calculate_risk(res)
    assert risk.level.value == "LOW"


def test_safety_context_prevented_event():
    adapter = AIAdapter()
    res = adapter.analyze("Worker did not enter confined space because gas testing was not completed.")
    assert res.sif_precursor is False
    assert res.context_type == "PREVENTED_EVENT"
    assert res.context_adjustment_reason is not None
    assert "Prevented Event" in res.context_adjustment_reason
    assert res.unsafe_act is None

    from app.services.risk_service import RiskService
    risk = RiskService().calculate_risk(res)
    assert risk.level.value == "LOW"


def test_safety_context_unsafe_act():
    adapter = AIAdapter()
    res = adapter.analyze("Technician entered confined space vessel without gas testing.")
    assert res.sif_precursor is True
    assert res.context_type == "UNSAFE_BEHAVIOR"

    from app.services.risk_service import RiskService
    risk = RiskService().calculate_risk(res)
    assert risk.level.value in ["HIGH", "CRITICAL"]


def test_safety_context_near_miss():
    adapter = AIAdapter()
    res = adapter.analyze("Heavy load nearly fell while lifting with crane due to damaged sling.")
    assert res.sif_precursor is True
    assert res.context_type == "NEAR_MISS"

    from app.services.risk_service import RiskService
    risk = RiskService().calculate_risk(res)
    assert risk.level.value in ["HIGH", "CRITICAL"]

