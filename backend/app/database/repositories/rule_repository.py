from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.schemas.rule import RuleResponse, RuleCreate


class RuleRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["rules"]

    async def create_rule(self, rule: RuleCreate) -> RuleResponse:
        doc = rule.model_dump()
        await self.collection.insert_one(doc)
        return RuleResponse(**doc)

    async def find_by_id(self, rule_id: str) -> Optional[RuleResponse]:
        doc = await self.collection.find_one({"rule_id": rule_id})
        if doc:
            return RuleResponse(**doc)
        return None

    async def get_all_rules(self) -> List[RuleResponse]:
        cursor = self.collection.find({})
        return [RuleResponse(**doc) async for doc in cursor]
