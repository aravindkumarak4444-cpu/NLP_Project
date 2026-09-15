from typing import List
from fastapi import APIRouter, Depends, status
from app.models.notification import NotificationModel
from app.models.user import UserModel, UserRole
from app.auth.dependencies import get_current_user
from app.database.connection import get_database
from app.database.repositories.notification_repository import NotificationRepository

router = APIRouter(prefix="/notifications", tags=["Notification Center"])


def get_notification_repo(db=Depends(get_database)) -> NotificationRepository:
    return NotificationRepository(db)


@router.get("", response_model=List[NotificationModel], summary="Get Notifications for Current User")
async def get_notifications(
    current_user: UserModel = Depends(get_current_user),
    repo: NotificationRepository = Depends(get_notification_repo)
):
    return await repo.get_user_notifications(user_id=current_user.user_id, role=current_user.role)


@router.patch("/{notification_id}/read", status_code=status.HTTP_200_OK, summary="Mark Notification as Read")
async def mark_read(
    notification_id: str,
    current_user: UserModel = Depends(get_current_user),
    repo: NotificationRepository = Depends(get_notification_repo)
):
    success = await repo.mark_as_read(notification_id)
    return {"notification_id": notification_id, "is_read": True, "success": success}
