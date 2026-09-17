import os
import sys
import logging

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

backend_dir = os.path.join(base_dir, "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.integrations.ai_adapter import AIAdapter
from app.services.risk_service import RiskService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("critical_cases_test")

cases = [
    ("A", "Worker entered a confined space without gas testing.", True, "UNSAFE_BEHAVIOR"),
    ("B", "Gas testing was completed before the worker entered the confined space.", False, "SAFE_COMPLIANCE"),
    ("C", "Worker did not enter the tank because gas testing failed.", False, "PREVENTED_EVENT"),
    ("D", "Worker worked at 14 meters without connecting the safety lanyard.", True, "UNSAFE_BEHAVIOR"),
    ("E", "Worker connected the safety lanyard before starting work at height.", False, "SAFE_COMPLIANCE"),
    ("F", "Crane lifted a suspended load while a worker stood underneath.", True, "UNSAFE_BEHAVIOR"),
    ("G", "The lifting area was barricaded and workers stayed outside the exclusion zone.", False, "SAFE_COMPLIANCE"),
    ("H", "Technician removed an electrical panel cover while energized.", True, "UNSAFE_BEHAVIOR"),
    ("I", "Technician isolated and verified zero energy before opening the panel.", False, "SAFE_COMPLIANCE"),
]

def test_critical_cases():
    adapter = AIAdapter()
    risk_service = RiskService()

    print("\n" + "=" * 80)
    print("      CRITICAL SAFETY CONTEXT TEST CASES EVALUATION (CASES A - I)      ")
    print("=" * 80)

    passed_count = 0
    for key, text, expected_sif, expected_ctx in cases:
        res = adapter.analyze(text)
        risk = risk_service.calculate_risk(res)

        sif_correct = (res.sif_precursor == expected_sif)
        ctx_correct = (res.context_type == expected_ctx) or (expected_ctx in res.context_type)
        is_pass = sif_correct and ctx_correct

        if is_pass:
            passed_count += 1
            status = "PASS"
        else:
            status = "FAIL"

        print(f"Case {key}: \"{text}\"")
        print(f"   SIF Precursor: {res.sif_precursor} (Expected: {expected_sif})")
        print(f"   Context Type: {res.context_type} (Expected: {expected_ctx})")
        print(f"   Risk Level  : {risk.level.value} | Confidence: {res.confidence}")
        print(f"   Adjustment  : {res.context_adjustment_reason}")
        print(f"   Result      : [{status}]")
        print("   " + "-" * 75)

    print(f"\nCRITICAL CASES SUMMARY: {passed_count}/{len(cases)} PASSED ({passed_count/len(cases)*100:.1f}%)")
    print("=" * 80 + "\n")
    return passed_count == len(cases)

if __name__ == "__main__":
    test_critical_cases()
