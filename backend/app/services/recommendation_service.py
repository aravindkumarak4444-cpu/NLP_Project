import logging
from typing import List, Optional
from app.models.report import RecommendationsModel, AIAnalysisModel, SIFRiskLevel

logger = logging.getLogger("sif_backend")


class RecommendationService:
    """
    Recommendation Engine generating tailored Immediate, Preventive, and Verification
    actions based on detected SIF hazard categories, unsafe acts, and risk level.
    """

    def generate_recommendations(
        self,
        ai_analysis: AIAnalysisModel,
        risk_level: SIFRiskLevel
    ) -> RecommendationsModel:
        immediate: List[str] = []
        preventive: List[str] = []
        verification: List[str] = []

        cat = ai_analysis.hazard_category.upper() if ai_analysis.hazard_category else "GENERAL"

        # Immediate Actions
        if risk_level in [SIFRiskLevel.CRITICAL, SIFRiskLevel.HIGH]:
            immediate.append("STOP WORK IMMEDIATELY in the affected area and secure the hazard zone.")
            immediate.append("Notify the Shift Safety Officer and Site Manager without delay.")
        else:
            immediate.append("Perform on-the-spot correction of the identified unsafe condition/act.")

        # Hazard-specific Actions
        if cat == "CONFINED_SPACE":
            immediate.append("Evacuate personnel from the vessel/confined space and isolate entry access.")
            preventive.append("Conduct multi-gas atmospheric testing (O2, H2S, LEL, CO) before re-entry.")
            preventive.append("Ensure continuous forced mechanical ventilation and deploy dedicated standby attendant.")
            verification.append("Verify Confined Space Entry Permit and gas test log calibration records.")

        elif cat == "WORKING_AT_HEIGHT":
            immediate.append("Restrict access below the elevated work platform.")
            preventive.append("Inspect 100% full-body harness, lanyards, and anchor points prior to climbing.")
            preventive.append("Install compliant toe-boards and top/mid-rails on all scaffolding structures.")
            verification.append("Inspect Scaffold Inspection Tag ('Green Tag') and height work permit compliance.")

        elif cat == "ELECTRICAL_SAFETY":
            immediate.append("Isolate power source at the circuit breaker / substation.")
            preventive.append("Apply physical Lockout/Tagout (LOTO) padlocks and test for zero energy state.")
            preventive.append("Ensure mandatory use of insulated PPE and rubber mats for electrical panels.")
            verification.append("Audit LOTO logbook and lock-box isolation certificate.")

        elif cat == "SUSPENDED_LOAD":
            immediate.append("Lower load safely or suspend hoisting operation; clear personnel from radius.")
            preventive.append("Inspect rigging slings, shackles, and crane safety latches for damage.")
            preventive.append("Establish physical barricades around the crane lifting swing zone.")
            verification.append("Verify Crane Third-Party Operator License and Lifting Plan calculations.")

        elif cat == "PRESSURE_SYSTEMS":
            immediate.append("Isolate pressure source valve and depressurize system safely.")
            preventive.append("Inspect pressure relief valves (PRVs) and calibrated pressure gauges.")
            verification.append("Audit hydro-test certificates and non-destructive testing (NDT) reports.")

        elif cat == "HOT_WORK":
            immediate.append("Extinguish hot work ignition source and post fire extinguisher standby.")
            preventive.append("Clear all combustible materials within a 35-foot (10m) radius or use fire blankets.")
            preventive.append("Maintain continuous gas monitoring and 30-minute post-work fire watch.")
            verification.append("Check Hot Work Permit and fire watch sign-off sheet.")

        else:
            preventive.append("Conduct Job Safety Analysis (JSA) refresh toolbox talk with the work crew.")
            verification.append("Area HSE Supervisor to perform spot safety walkthrough within 24 hours.")

        # Ensure non-empty defaults
        if not immediate:
            immediate.append("Document the hazard and communicate details to site safety representative.")
        if not preventive:
            preventive.append("Re-evaluate operational procedures during next pre-job safety meeting.")
        if not verification:
            verification.append("Safety Officer to review resolution status before job restart.")

        return RecommendationsModel(
            immediate_actions=immediate,
            preventive_actions=preventive,
            verification_actions=verification
        )
