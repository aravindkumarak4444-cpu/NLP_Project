from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.user import UserModel


class UserRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["users"]

    async def create_user(self, user: UserModel) -> UserModel:
        user_dict = user.model_dump()
        await self.collection.insert_one(user_dict)
        return user

    async def find_by_email(self, email: str) -> Optional[UserModel]:
        data = await self.collection.find_one({"email": email.lower()})
        if data:
            return UserModel(**data)
        return None

    async def find_by_username(self, username: str) -> Optional[UserModel]:
        data = await self.collection.find_one({"username": username.lower()})
        if data:
            return UserModel(**data)
        return None

    async def find_by_id(self, user_id: str) -> Optional[UserModel]:
        data = await self.collection.find_one({"user_id": user_id})
        if data:
            return UserModel(**data)
        return None

    async def update_user(self, user_id: str, update_data: Dict[str, Any]) -> Optional[UserModel]:
        result = await self.collection.find_one_and_update(
            {"user_id": user_id},
            {"$set": update_data},
            return_document=True
        )
        if result:
            return UserModel(**result)
        return None
