from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.feedback import FeedbackModel


class FeedbackRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["feedback_dataset"]

    async def add_feedback(self, fb: FeedbackModel) -> FeedbackModel:
        await self.collection.insert_one(fb.model_dump())
        return fb

    async def list_feedback(self, status_filter: Optional[str] = None, limit: int = 50) -> List[FeedbackModel]:
        query = {}
        if status_filter:
            query["status"] = status_filter
        cursor = self.collection.find(query).sort("reviewed_at", -1).limit(limit)
        return [FeedbackModel(**doc) async for doc in cursor]

    async def update_status(self, feedback_id: str, new_status: str) -> bool:
        res = await self.collection.update_one({"feedback_id": feedback_id}, {"$set": {"status": new_status}})
        return res.modified_count > 0
