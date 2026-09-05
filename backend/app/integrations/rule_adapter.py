import logging
from typing import Optional, Dict, Any
from app.models.report import LifeSavingRuleModel

logger = logging.getLogger("sif_backend")


class RuleAdapter:
    """
    Adapter interface connecting backend to Member 2's Life-Saving Rules Mapping Engine.
    Maps detected hazard categories and unsafe acts/conditions to standard Life-Saving Rules.
    """

    def __init__(self):
        # Database of standard Oil & Gas Life-Saving Rules (IOGP / OIL standards)
        self.rules_database: Dict[str, Dict[str, str]] = {
            "CONFINED_SPACE": {
                "rule_id": "LSR-01",
                "rule_name": "Confined Space Entry",
                "description": "Obtain authorization before entering a confined space and verify atmospheric gas testing."
            },
            "WORKING_AT_HEIGHT": {
                "rule_id": "LSR-02",
                "rule_name": "Work at Height",
                "description": "Protect yourself against falling when working at height (above 1.8m) using 100% fall protection."
            },
            "ELECTRICAL_SAFETY": {
                "rule_id": "LSR-03",
                "rule_name": "Energy Isolation (LOTO)",
                "description": "Verify isolation and zero energy state before work begins on electrical or mechanical systems."
            },
            "SUSPENDED_LOAD": {
                "rule_id": "LSR-04",
                "rule_name": "Safe Mechanical Lifting",
                "description": "Plan lifting operations and never position yourself under a suspended load."
            },
            "PRESSURE_SYSTEMS": {
                "rule_id": "LSR-05",
                "rule_name": "Pressurized Systems Safety",
                "description": "Inspect pressure relief equipment and never depressurize or break containment without proper authorization."
            },
            "HOT_WORK": {
                "rule_id": "LSR-06",
                "rule_name": "Hot Work Safety",
                "description": "Control flammable gas sources and obtain hot work permits prior to ignition activities."
            }
        }

    def map_rule(
        self,
        hazard_category: Optional[str],
        unsafe_act: Optional[str] = None,
        unsafe_condition: Optional[str] = None
    ) -> LifeSavingRuleModel:
        """
        Maps extracted analysis entities to official Life-Saving Rule.
        """
        if not hazard_category:
            return LifeSavingRuleModel(
                rule_id="LSR-00",
                rule_name="General Safety Standard",
                description="Follow standard operational safety policies."
            )

        cat_upper = hazard_category.upper()
        if cat_upper in self.rules_database:
            rule_info = self.rules_database[cat_upper]
            return LifeSavingRuleModel(
                rule_id=rule_info["rule_id"],
                rule_name=rule_info["rule_name"],
                description=rule_info["description"]
            )

        return LifeSavingRuleModel(
            rule_id="LSR-GENERAL",
            rule_name="Standard Operational Risk Controls",
            description="Ensure job safety analysis (JSA) is completed prior to work."
        )
