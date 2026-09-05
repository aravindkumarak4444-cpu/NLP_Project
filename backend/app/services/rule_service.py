from typing import List, Optional
from app.database.repositories.rule_repository import RuleRepository
from app.schemas.rule import RuleResponse, RuleCreate
from app.integrations.rule_adapter import RuleAdapter


class RuleService:
    def __init__(self, rule_repo: RuleRepository, rule_adapter: RuleAdapter):
        self.rule_repo = rule_repo
        self.rule_adapter = rule_adapter

    async def get_all_rules(self) -> List[RuleResponse]:
        rules_in_db = await self.rule_repo.get_all_rules()
        if rules_in_db:
            return rules_in_db

        # Seed from rule adapter default rules if DB empty
        default_rules = []
        for cat, info in self.rule_adapter.rules_database.items():
            rule_create = RuleCreate(
                rule_id=info["rule_id"],
                rule_name=info["rule_name"],
                description=info["description"],
                hazard_categories=[cat],
                unsafe_acts=[],
                unsafe_conditions=[]
            )
            created = await self.rule_repo.create_rule(rule_create)
            default_rules.append(created)

        return default_rules

    async def get_rule_by_id(self, rule_id: str) -> Optional[RuleResponse]:
        return await self.rule_repo.find_by_id(rule_id)
