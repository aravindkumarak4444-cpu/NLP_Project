import os
import sys
import logging
from typing import Optional, Dict, Any, List
from app.models.report import LifeSavingRuleModel

logger = logging.getLogger("sif_backend")

# Ensure rule_mapping directory is on sys.path
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
rule_mapping_dir = os.path.join(base_dir, "rule_mapping")
if os.path.exists(rule_mapping_dir) and rule_mapping_dir not in sys.path:
    sys.path.insert(0, rule_mapping_dir)

try:
    from mapper import get_life_saving_rules
    MEMBER2_MAPPER_AVAILABLE = True
except Exception as e:
    logger.warning(f"Could not import Member 2 get_life_saving_rules mapper: {str(e)}")
    MEMBER2_MAPPER_AVAILABLE = False


class RuleAdapter:
    """
    Adapter interface connecting backend to Member 2's Life-Saving Rules Mapping Engine.
    Passes report text and hazard details into Member 2's mapper function and normalizes output.
    """

    def __init__(self):
        # Database of Oil & Gas Life-Saving Rules mapped to Member 2 rules.json definitions
        self.rules_database: Dict[str, Dict[str, str]] = {
            "Confined Space": {
                "rule_id": "LSR-01",
                "rule_name": "Confined Space",
                "description": "Obtain authorization before entering a confined space and verify atmospheric gas testing."
            },
            "Work at Height": {
                "rule_id": "LSR-02",
                "rule_name": "Work at Height",
                "description": "Protect yourself against falling when working at height using 100% fall protection."
            },
            "Energy Isolation": {
                "rule_id": "LSR-03",
                "rule_name": "Energy Isolation",
                "description": "Verify isolation and zero energy state before work begins."
            },
            "Safe Mechanical Lifting": {
                "rule_id": "LSR-04",
                "rule_name": "Safe Mechanical Lifting",
                "description": "Plan lifting operations and never position yourself under a suspended load."
            },
            "Hot Work": {
                "rule_id": "LSR-05",
                "rule_name": "Hot Work",
                "description": "Control flammable gas sources and obtain hot work permit prior to ignition activities."
            },
            "Bypassing Safety Controls": {
                "rule_id": "LSR-06",
                "rule_name": "Bypassing Safety Controls",
                "description": "Obtain authorization before overriding or disabling safety controls."
            },
            "Driving": {
                "rule_id": "LSR-07",
                "rule_name": "Driving",
                "description": "Always wear seatbelts, adhere to speed limits, and do not use mobile phones while driving."
            },
            "Line of Fire": {
                "rule_id": "LSR-08",
                "rule_name": "Line of Fire",
                "description": "Keep yourself and others out of the line of fire of moving machinery or pressure."
            },
            "Work Authorisation": {
                "rule_id": "LSR-09",
                "rule_name": "Work Authorisation",
                "description": "Work with a valid work permit when required."
            }
        }

    def map_rule(
        self,
        report_text: str = "",
        hazard_category: Optional[str] = None,
        unsafe_act: Optional[str] = None,
        unsafe_condition: Optional[str] = None
    ) -> LifeSavingRuleModel:
        """
        Maps report text and hazard parameters to official Member 2 Life-Saving Rules.
        """
        combined_text = f"{report_text or ''} {hazard_category or ''} {unsafe_act or ''} {unsafe_condition or ''}".strip()

        rules_found: List[str] = []
        if MEMBER2_MAPPER_AVAILABLE and combined_text:
            try:
                rules_found = get_life_saving_rules(combined_text)
            except Exception as e:
                logger.error(f"Error executing Member 2 get_life_saving_rules: {str(e)}")

        if not rules_found or rules_found == ["General Safety"] or rules_found == ["None"]:
            return LifeSavingRuleModel(
                rule_id="LSR-GENERAL",
                rule_name="General Safety",
                description="Follow standard operational safety policies and job safety analysis."
            )

        primary_rule = rules_found[0]
        rule_name = ", ".join(rules_found)
        rule_id = f"LSR-{primary_rule.upper().replace(' ', '_')}"
        rule_desc = f"Mandatory Oil India Limited (OIL) Life-Saving Rule requirement: {rule_name}."

        for r_key, r_info in self.rules_database.items():
            if r_key.lower() == primary_rule.lower():
                rule_id = r_info["rule_id"]
                rule_desc = r_info["description"]
                break

        return LifeSavingRuleModel(
            rule_id=rule_id,
            rule_name=rule_name,
            description=rule_desc
        )
