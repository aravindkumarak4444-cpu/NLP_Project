from typing import List
from fastapi import APIRouter, Depends
from app.schemas.rule import RuleResponse
from app.services.rule_service import RuleService
from app.integrations.rule_adapter import RuleAdapter
from app.database.connection import get_database
from app.database.repositories.rule_repository import RuleRepository
from app.auth.dependencies import get_current_user
from app.models.user import UserModel

router = APIRouter(prefix="/rules", tags=["Life-Saving Rules"])


def get_rule_service(db=Depends(get_database)) -> RuleService:
    repo = RuleRepository(db)
    adapter = RuleAdapter()
    return RuleService(repo, adapter)


@router.get("", response_model=List[RuleResponse], summary="List All Life-Saving Rules")
async def list_rules(
    current_user: UserModel = Depends(get_current_user),
    service: RuleService = Depends(get_rule_service)
):
    return await service.get_all_rules()
