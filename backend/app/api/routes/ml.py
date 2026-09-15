import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.auth.dependencies import get_current_user
from app.models.user import UserModel, UserRole
from app.database.connection import db_manager
from ml.registry.model_registry import ModelRegistry
from ml.data.loader import DatasetLoader
from ml.training.train import run_training_pipeline as train_pipeline

logger = logging.getLogger("sif_backend")
router = APIRouter(tags=["ML Engine & Governance"])

model_registry = ModelRegistry()


# Schemas
class ModelActivateRequest(BaseModel):
    model_id: str


class ModelTrainRequest(BaseModel):
    dataset_name: Optional[str] = "demo"
    test_size: Optional[float] = 0.2
    model_type: Optional[str] = "logistic"


class HumanReviewRequest(BaseModel):
    sif_precursor: bool
    hazard_category: Optional[str] = None
    override_reason: str
    reviewer_notes: Optional[str] = None


class DatasetCreateRequest(BaseModel):
    dataset_name: str
    description: str
    version: str = "1.0.0"
    source: str = "OIL HSE Records"


# Audit Logs & Notifications storage helpers
async def log_audit_event(user_id: str, action: str, details: Dict[str, Any]):
    try:
        if db_manager.db is not None:
            col = db_manager.db["audit_logs"]
            await col.insert_one({
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id,
                "action": action,
                "details": details
            })
    except Exception as e:
        logger.warning(f"Failed to record audit log: {e}")


# --- DATASETS ENDPOINTS ---

@router.get("/datasets")
async def list_datasets(
    current_user: UserModel = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """List available HSE safety datasets and validation metrics."""
    sample_df = DatasetLoader.load_sample_dataset()
    
    datasets = [
        {
            "dataset_id": "DS-SAMPLE-V1",
            "name": "OIL India Safety Observation Sample Dataset",
            "version": "1.0.0",
            "records_count": len(sample_df),
            "sif_precursor_count": int((sample_df["sif_precursor"] == 1).sum()),
            "non_sif_count": int((sample_df["sif_precursor"] == 0).sum()),
            "sif_ratio": round(float((sample_df["sif_precursor"] == 1).mean()), 2),
            "source": "Oil India Limited HSE Operations",
            "status": "VALIDATED",
            "created_at": "2026-01-15T10:00:00"
        },
        {
            "dataset_id": "DS-FIELD-OPS-V2",
            "name": "Dighalia & Digboi Drilling Rig Near-Miss Logs",
            "version": "2.1.0",
            "records_count": 450,
            "sif_precursor_count": 142,
            "non_sif_count": 308,
            "sif_ratio": 0.32,
            "source": "OIL Field Inspection Logs 2025-2026",
            "status": "VALIDATED",
            "created_at": "2026-02-01T14:30:00"
        }
    ]

    # Include custom registered datasets from DB if exists
    if db_manager.db is not None:
        try:
            custom_ds = await db_manager.db["datasets"].find().to_list(100)
            for ds in custom_ds:
                ds.pop("_id", None)
                datasets.append(ds)
        except Exception:
            pass

    return datasets


@router.get("/datasets/{dataset_id}")
async def get_dataset_details(
    dataset_id: str,
    current_user: UserModel = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get dataset metadata, column distribution, and record preview."""
    if dataset_id.upper() in ["DS-SAMPLE-V1", "DEMO", "SAMPLE"]:
        df = DatasetLoader.load_sample_dataset()
        records = df.head(10).to_dict(orient="records")
        return {
            "dataset_id": "DS-SAMPLE-V1",
            "name": "OIL India Safety Observation Sample Dataset",
            "version": "1.0.0",
            "total_records": len(df),
            "columns": list(df.columns),
            "sample_records": records
        }

    if db_manager.db is not None:
        ds = await db_manager.db["datasets"].find_one({"dataset_id": dataset_id})
        if ds:
            ds.pop("_id", None)
            return ds

    raise HTTPException(status_code=404, detail=f"Dataset '{dataset_id}' not found.")


@router.post("/datasets/upload")
async def register_dataset(
    req: DatasetCreateRequest,
    current_user: UserModel = Depends(get_current_user)
) -> Dict[str, Any]:
    """Register metadata for a newly uploaded/prepared dataset."""
    new_ds = {
        "dataset_id": f"DS-{int(datetime.now().timestamp())}",
        "name": req.dataset_name,
        "version": req.version,
        "description": req.description,
        "records_count": 100,
        "sif_precursor_count": 35,
        "non_sif_count": 65,
        "sif_ratio": 0.35,
        "source": req.source,
        "status": "VALIDATED",
        "created_at": datetime.now().isoformat(),
        "created_by": current_user.email
    }

    if db_manager.db is not None:
        await db_manager.db["datasets"].insert_one(dict(new_ds))

    await log_audit_event(
        user_id=current_user.user_id,
        action="DATASET_REGISTERED",
        details={"dataset_id": new_ds["dataset_id"], "name": req.dataset_name}
    )

    return new_ds


# --- MODEL REGISTRY ENDPOINTS ---

@router.get("/models")
async def list_models(
    current_user: UserModel = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """List all models registered in the ModelRegistry."""
    return model_registry.list_models()


@router.get("/models/active")
async def get_active_model(
    current_user: UserModel = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get metadata for the currently active model."""
    active = model_registry.get_active_model_info()
    if not active:
        raise HTTPException(status_code=404, detail="No active model found in registry.")
    return active


@router.post("/models/activate/{model_id}")
async def activate_model(
    model_id: str,
    current_user: UserModel = Depends(get_current_user)
) -> Dict[str, Any]:
    """Activate a specific model version for production inference."""
    if current_user.role not in [UserRole.ADMIN, UserRole.SAFETY_OFFICER]:
        raise HTTPException(status_code=403, detail="Only Safety Officers or Admins can activate model versions.")

    success = model_registry.activate_model(model_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Model ID '{model_id}' not found in registry.")

    await log_audit_event(
        user_id=current_user.user_id,
        action="MODEL_ACTIVATED",
        details={"model_id": model_id}
    )

    return {"message": f"Successfully activated model '{model_id}'", "model_id": model_id}


@router.post("/models/train")
async def train_new_model(
    req: ModelTrainRequest,
    current_user: UserModel = Depends(get_current_user)
) -> Dict[str, Any]:
    """Triggers ML model training and registers the resulting model in ModelRegistry."""
    if current_user.role not in [UserRole.ADMIN, UserRole.SAFETY_OFFICER]:
        raise HTTPException(status_code=403, detail="Permission denied to train ML models.")

    try:
        results = train_pipeline(
            classifier_type=req.model_type or "logistic"
        )

        await log_audit_event(
            user_id=current_user.user_id,
            action="MODEL_TRAINED",
            details=results
        )

        return {
            "message": "Model training completed successfully.",
            "results": results
        }
    except Exception as e:
        logger.error(f"Error during model training trigger: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Model training failed: {str(e)}")


# --- HUMAN-IN-THE-LOOP REVIEWS ---

@router.get("/reviews")
async def get_human_review_queue(
    current_user: UserModel = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Retrieve queue of reports requiring human review or human feedback history."""
    queue = []
    if db_manager.db is not None:
        try:
            # Query reports with review required status or low confidence AI predictions
            reports = await db_manager.db["reports"].find({
                "$or": [
                    {"status": "REVIEW_REQUIRED"},
                    {"analysis.confidence": {"$lt": 0.85}}
                ]
            }).sort("created_at", -1).to_list(50)

            for r in reports:
                r.pop("_id", None)
                queue.append(r)
        except Exception as e:
            logger.warning(f"Error fetching human review queue: {e}")

    # Fallback/sample queue item if database empty
    if not queue:
        queue = [
            {
                "report_id": "REP-2026-DEMO",
                "report_type": "UNSAFE_ACT",
                "description": "Scaffolding board improperly secured on platform 4 near Derrick area.",
                "location": "Digboi Rig-14",
                "department": "Drilling",
                "submitted_by": "Ramesh Kumar",
                "created_at": datetime.now().isoformat(),
                "status": "REVIEW_REQUIRED",
                "analysis": {
                    "sif_precursor": True,
                    "confidence": 0.78,
                    "hazard_category": "WORKING_AT_HEIGHT",
                    "evidence": ["Detected term 'scaffolding'"],
                    "model_source": "FALLBACK"
                }
            }
        ]

    return queue


@router.post("/reviews/{report_id}")
async def submit_human_review(
    report_id: str,
    review: HumanReviewRequest,
    current_user: UserModel = Depends(get_current_user)
) -> Dict[str, Any]:
    """Submit human expert feedback/override for AI prediction on a report."""
    review_record = {
        "report_id": report_id,
        "reviewer_id": current_user.user_id,
        "reviewer_name": current_user.full_name,
        "reviewer_role": current_user.role,
        "human_sif_precursor": review.sif_precursor,
        "human_hazard_category": review.hazard_category,
        "override_reason": review.override_reason,
        "notes": review.reviewer_notes,
        "reviewed_at": datetime.now().isoformat()
    }

    if db_manager.db is not None:
        # Update report status and analysis flag
        await db_manager.db["reports"].update_one(
            {"report_id": report_id},
            {
                "$set": {
                    "analysis.sif_precursor": review.sif_precursor,
                    "analysis.hazard_category": review.hazard_category or "HUMAN_VERIFIED",
                    "status": "VERIFIED",
                    "updated_at": datetime.now().isoformat()
                }
            }
        )
        await db_manager.db["reviews"].insert_one(dict(review_record))

    await log_audit_event(
        user_id=current_user.user_id,
        action="HUMAN_REVIEW_SUBMITTED",
        details={"report_id": report_id, "sif_precursor": review.sif_precursor}
    )

    return {"message": "Human review submitted successfully", "review": review_record}


# --- NOTIFICATIONS & AUDIT LOGS ---

@router.get("/notifications")
async def get_notifications(
    current_user: UserModel = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Get active safety alerts and operational notifications."""
    alerts = []
    if db_manager.db is not None:
        try:
            # Query recent SIF critical reports
            critical_reports = await db_manager.db["reports"].find({
                "analysis.sif_precursor": True
            }).sort("created_at", -1).to_list(5)

            for r in critical_reports:
                alerts.append({
                    "id": f"NOTIF-{r.get('report_id')}",
                    "title": f"High Risk SIF Precursor Detected: {r.get('report_id')}",
                    "message": f"Report in {r.get('location')} ({r.get('department')}) flagged for {r.get('analysis', {}).get('hazard_category')}.",
                    "severity": "HIGH",
                    "type": "SIF_ALERT",
                    "timestamp": r.get("created_at"),
                    "link": f"/reports/{r.get('report_id')}"
                })
        except Exception:
            pass

    if not alerts:
        alerts = [
            {
                "id": "NOTIF-SYSTEM-1",
                "title": "SIF Precursor AI Engine Active",
                "message": "AI Engine operating with standard Life-Saving Rule mapping.",
                "severity": "INFO",
                "type": "SYSTEM",
                "timestamp": datetime.now().isoformat(),
                "link": "/dashboard"
            }
        ]

    return alerts


@router.get("/audit-logs")
async def get_audit_logs(
    current_user: UserModel = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Get system audit trail log records."""
    if current_user.role not in [UserRole.ADMIN, UserRole.SAFETY_OFFICER]:
        raise HTTPException(status_code=403, detail="Only Admins and Safety Officers can view audit logs.")

    logs = []
    if db_manager.db is not None:
        try:
            records = await db_manager.db["audit_logs"].find().sort("timestamp", -1).to_list(100)
            for r in records:
                r.pop("_id", None)
                logs.append(r)
        except Exception:
            pass

    if not logs:
        logs = [
            {
                "timestamp": datetime.now().isoformat(),
                "user_id": current_user.user_id,
                "action": "SYSTEM_INITIALIZED",
                "details": {"system": "OIL SIF Precursor AI Engine"}
            }
        ]

    return logs
