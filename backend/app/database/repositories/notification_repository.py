from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.notification import NotificationModel
from app.models.user import UserRole


class NotificationRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["notifications"]

    async def create_notification(self, notif: NotificationModel) -> NotificationModel:
        await self.collection.insert_one(notif.model_dump())
        return notif

    async def get_user_notifications(self, user_id: str, role: UserRole, limit: int = 20) -> List[NotificationModel]:
        query = {
            "$or": [
                {"recipient_user_id": user_id},
                {"recipient_role": role.value}
            ]
        }
        cursor = self.collection.find(query).sort("created_at", -1).limit(limit)
        return [NotificationModel(**doc) async for doc in cursor]

    async def mark_as_read(self, notification_id: str) -> bool:
        res = await self.collection.update_one({"notification_id": notification_id}, {"$set": {"is_read": True}})
        return res.modified_count > 0
