from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.audit import AuditLogModel


class AuditRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["audit_logs"]

    async def log_event(self, log: AuditLogModel) -> AuditLogModel:
        await self.collection.insert_one(log.model_dump())
        return log

    async def list_logs(self, limit: int = 50) -> List[AuditLogModel]:
        cursor = self.collection.find({}).sort("timestamp", -1).limit(limit)
        return [AuditLogModel(**doc) async for doc in cursor]
