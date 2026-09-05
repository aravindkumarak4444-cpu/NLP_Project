from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import DESCENDING, ASCENDING
from app.models.report import ReportModel, ReportStatus, SIFRiskLevel, ReportType


class ReportRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["reports"]

    async def create_report(self, report: ReportModel) -> ReportModel:
        doc = report.model_dump()
        await self.collection.insert_one(doc)
        return report

    async def find_by_id(self, report_id: str) -> Optional[ReportModel]:
        doc = await self.collection.find_one({"report_id": report_id})
        if doc:
            return ReportModel(**doc)
        return None

    async def update_report(self, report_id: str, update_dict: Dict[str, Any]) -> Optional[ReportModel]:
        doc = await self.collection.find_one_and_update(
            {"report_id": report_id},
            {"$set": update_dict},
            return_document=True
        )
        if doc:
            return ReportModel(**doc)
        return None

    async def delete_report(self, report_id: str) -> bool:
        result = await self.collection.delete_one({"report_id": report_id})
        return result.deleted_count > 0

    async def list_reports(
        self,
        page: int = 1,
        limit: int = 20,
        status: Optional[ReportStatus] = None,
        report_type: Optional[ReportType] = None,
        risk_level: Optional[SIFRiskLevel] = None,
        sif_precursor: Optional[bool] = None,
        department: Optional[str] = None,
        location: Optional[str] = None,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> Tuple[List[ReportModel], int]:
        query: Dict[str, Any] = {}

        if status:
            query["status"] = status.value
        if report_type:
            query["report_type"] = report_type.value
        if risk_level:
            query["risk.level"] = risk_level.value
        if sif_precursor is not None:
            query["analysis.sif_precursor"] = sif_precursor
        if department:
            query["department"] = {"$regex": department, "$options": "i"}
        if location:
            query["location"] = {"$regex": location, "$options": "i"}
        if search:
            query["$or"] = [
                {"description": {"$regex": search, "$options": "i"}},
                {"location": {"$regex": search, "$options": "i"}},
                {"department": {"$regex": search, "$options": "i"}},
                {"report_id": {"$regex": search, "$options": "i"}}
            ]

        total = await self.collection.count_documents(query)

        sort_dir = DESCENDING if sort_order.lower() == "desc" else ASCENDING
        skip = (page - 1) * limit

        cursor = self.collection.find(query).sort(sort_by, sort_dir).skip(skip).limit(limit)
        items = [ReportModel(**doc) async for doc in cursor]

        return items, total

    async def get_all_reports_for_analytics(self) -> List[ReportModel]:
        cursor = self.collection.find({})
        return [ReportModel(**doc) async for doc in cursor]
