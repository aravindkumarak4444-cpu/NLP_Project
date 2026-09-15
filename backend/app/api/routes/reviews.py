from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from app.models.report import ReportStatus, SIFRiskLevel, ActionItemModel, ActionStatus
from app.models.user import UserModel, UserRole
from app.models.review import ReviewModel
from app.models.feedback import FeedbackModel
from app.models.audit import AuditLogModel
from app.models.notification import NotificationModel
from app.auth.dependencies import require_roles, get_current_user
from app.database.connection import get_database
from app.database.repositories.report_repository import ReportRepository
from app.database.repositories.review_repository import ReviewRepository
from app.database.repositories.feedback_repository import FeedbackRepository
from app.database.repositories.audit_repository import AuditRepository
from app.database.repositories.notification_repository import NotificationRepository
from app.database.repositories.user_repository import UserRepository
from app.utils.ids import generate_action_id
from app.utils.timestamps import utc_now
from app.middleware.error_handler import APIException

router = APIRouter(prefix="/reviews", tags=["Safety Officer Reviews"])


class ReviewCreateRequest(BaseModel):
    report_id: str
    decision: str  # ACCEPT, REJECT, CORRECT
    corrected_sif: Optional[bool] = None
    corrected_risk: Optional[SIFRiskLevel] = None
    corrected_hazard: Optional[str] = None
    corrected_unsafe_act: Optional[str] = None
    corrected_unsafe_condition: Optional[str] = None
    correction_reason: Optional[str] = None
    assigned_to: Optional[str] = None  # Username or user_id of responsible person
    action_description: Optional[str] = None
    due_date: Optional[datetime] = None


@router.post("", response_model=ReviewModel, status_code=status.HTTP_201_CREATED, summary="Submit Safety Officer Review Decision")
async def submit_review(
    req: ReviewCreateRequest,
    current_user: UserModel = Depends(require_roles([UserRole.SAFETY_OFFICER, UserRole.MANAGER, UserRole.ADMIN])),
    db=Depends(get_database)
):
    report_repo = ReportRepository(db)
    review_repo = ReviewRepository(db)
    feedback_repo = FeedbackRepository(db)
    audit_repo = AuditRepository(db)
    notif_repo = NotificationRepository(db)
    user_repo = UserRepository(db)

    report = await report_repo.find_by_id(req.report_id)
    if not report:
        raise APIException(
            code="REPORT_NOT_FOUND",
            message=f"Safety report with ID '{req.report_id}' was not found.",
            status_code=status.HTTP_404_NOT_FOUND
        )

    now = utc_now()
    review_id = f"REV-{int(now.timestamp())}"

    raw_pred = report.analysis.raw_prediction if report.analysis else None
    raw_conf = report.analysis.raw_confidence if report.analysis else None

    review = ReviewModel(
        review_id=review_id,
        report_id=req.report_id,
        officer_id=current_user.user_id,
        officer_name=current_user.full_name or current_user.username,
        decision=req.decision.upper(),
        raw_prediction=raw_pred,
        raw_confidence=raw_conf,
        corrected_sif=req.corrected_sif,
        corrected_risk=req.corrected_risk,
        corrected_hazard=req.corrected_hazard,
        corrected_unsafe_act=req.corrected_unsafe_act,
        corrected_unsafe_condition=req.corrected_unsafe_condition,
        correction_reason=req.correction_reason,
        created_at=now
    )

    saved_review = await review_repo.create_review(review)

    # Determine final SIF and risk values
    final_sif = req.corrected_sif if req.corrected_sif is not None else (report.analysis.sif_precursor if report.analysis else False)
    final_risk = req.corrected_risk if req.corrected_risk else (report.risk.level if report.risk else SIFRiskLevel.LOW)

    # Update Report Analysis & Risk without overwriting raw_prediction / raw_confidence
    update_data = {
        "status": ReportStatus.ACTION_ASSIGNED if req.assigned_to else ReportStatus.RESOLVED,
        "updated_at": now
    }

    if report.analysis:
        analysis_dict = report.analysis.model_dump()
        analysis_dict["sif_precursor"] = final_sif
        if req.corrected_hazard:
            analysis_dict["hazard_category"] = req.corrected_hazard
        if req.corrected_unsafe_act:
            analysis_dict["unsafe_act"] = req.corrected_unsafe_act
        if req.corrected_unsafe_condition:
            analysis_dict["unsafe_condition"] = req.corrected_unsafe_condition
        update_data["analysis"] = analysis_dict

    if report.risk:
        risk_dict = report.risk.model_dump()
        risk_dict["level"] = final_risk.value if hasattr(final_risk, "value") else str(final_risk)
        update_data["risk"] = risk_dict

    # Assign action if requested
    if req.assigned_to and req.action_description:
        resp_user = await user_repo.find_by_username(req.assigned_to) or await user_repo.find_by_id(req.assigned_to) or await user_repo.find_by_email(req.assigned_to)
        assigned_name = resp_user.full_name if resp_user else req.assigned_to
        assigned_id = resp_user.user_id if resp_user else req.assigned_to

        action_item = ActionItemModel(
            action_id=generate_action_id(),
            description=req.action_description,
            assigned_to=assigned_name,
            status=ActionStatus.PENDING,
            due_date=req.due_date,
            created_at=now
        )
        actions_list = [a.model_dump() for a in (report.actions or [])]
        actions_list.append(action_item.model_dump())
        update_data["actions"] = actions_list

        # Notify responsible person
        if resp_user:
            await notif_repo.create_notification(NotificationModel(
                notification_id=f"NOTIF-{int(now.timestamp())}",
                recipient_user_id=resp_user.user_id,
                title="New Corrective Action Assigned",
                message=f"You have been assigned a corrective action for report {report.report_id}: {req.action_description}",
                report_id=report.report_id,
                created_at=now
            ))

    await report_repo.update_report(req.report_id, update_data)

    # Save Candidate Sample to Feedback Dataset
    fb = FeedbackModel(
        feedback_id=f"FB-{int(now.timestamp())}",
        report_id=report.report_id,
        report_text=report.description,
        original_ai_prediction=raw_pred,
        original_confidence=raw_conf,
        familiarity_score=report.analysis.training_familiarity if report.analysis else 1.0,
        safety_context=report.analysis.context_type if report.analysis else "UNKNOWN",
        officer_final_label=final_sif,
        final_risk=final_risk,
        hazard_category=req.corrected_hazard or (report.analysis.hazard_category if report.analysis else None),
        unsafe_act=req.corrected_unsafe_act or (report.analysis.unsafe_act if report.analysis else None),
        unsafe_condition=req.corrected_unsafe_condition or (report.analysis.unsafe_condition if report.analysis else None),
        review_reason=req.correction_reason or f"Officer decision: {req.decision}",
        reviewed_by=current_user.full_name or current_user.username,
        reviewed_at=now,
        status="PENDING_TRAINING"
    )
    await feedback_repo.add_feedback(fb)

    # Audit Logging
    await audit_repo.log_event(AuditLogModel(
        log_id=f"AUD-{int(now.timestamp())}",
        event=f"REVIEW_{req.decision.upper()}",
        user_id=current_user.user_id,
        user_name=current_user.full_name or current_user.username,
        user_role=current_user.role,
        report_id=report.report_id,
        details={
            "decision": req.decision,
            "final_sif": final_sif,
            "final_risk": str(final_risk),
            "assigned_to": req.assigned_to
        },
        timestamp=now
    ))

    return saved_review


@router.get("", response_model=List[ReviewModel], summary="List Recent Reviews")
async def list_reviews(
    current_user: UserModel = Depends(require_roles([UserRole.SAFETY_OFFICER, UserRole.MANAGER, UserRole.ADMIN])),
    db=Depends(get_database)
):
    review_repo = ReviewRepository(db)
    return await review_repo.list_recent_reviews(limit=50)
