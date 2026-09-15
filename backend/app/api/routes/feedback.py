from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel
from app.models.feedback import FeedbackModel
from app.models.user import UserModel, UserRole
from app.auth.dependencies import require_roles
from app.database.connection import get_database
from app.database.repositories.feedback_repository import FeedbackRepository

router = APIRouter(prefix="/feedback", tags=["Candidate Feedback Dataset"])


def get_feedback_repo(db=Depends(get_database)) -> FeedbackRepository:
    return FeedbackRepository(db)


class FeedbackStatusUpdate(BaseModel):
    status: str  # APPROVED_FOR_TRAINING, REJECTED, PENDING_TRAINING


@router.get("", response_model=List[FeedbackModel], summary="List Candidate Feedback Dataset Samples")
async def list_feedback_samples(
    status_filter: Optional[str] = Query(None, description="Filter by status (PENDING_TRAINING, APPROVED_FOR_TRAINING, REJECTED)"),
    current_user: UserModel = Depends(require_roles([UserRole.SAFETY_OFFICER, UserRole.MANAGER, UserRole.ADMIN])),
    repo: FeedbackRepository = Depends(get_feedback_repo)
):
    return await repo.list_feedback(status_filter=status_filter)


@router.patch("/{feedback_id}/status", status_code=status.HTTP_200_OK, summary="Approve/Reject Candidate Feedback Sample")
async def update_feedback_status(
    feedback_id: str,
    update_in: FeedbackStatusUpdate,
    current_user: UserModel = Depends(require_roles([UserRole.ADMIN, UserRole.SAFETY_OFFICER])),
    repo: FeedbackRepository = Depends(get_feedback_repo)
):
    success = await repo.update_status(feedback_id, update_in.status)
    return {"feedback_id": feedback_id, "status": update_in.status, "success": success}
