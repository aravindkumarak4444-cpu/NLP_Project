from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.review import ReviewModel


class ReviewRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["reviews"]

    async def create_review(self, review: ReviewModel) -> ReviewModel:
        await self.collection.insert_one(review.model_dump())
        return review

    async def get_reviews_for_report(self, report_id: str) -> List[ReviewModel]:
        cursor = self.collection.find({"report_id": report_id}).sort("created_at", -1)
        return [ReviewModel(**doc) async for doc in cursor]

    async def list_recent_reviews(self, limit: int = 20) -> List[ReviewModel]:
        cursor = self.collection.find({}).sort("created_at", -1).limit(limit)
        return [ReviewModel(**doc) async for doc in cursor]
