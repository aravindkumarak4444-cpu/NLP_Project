from typing import List, Optional
from pydantic import BaseModel, Field


class RuleCreate(BaseModel):
    rule_id: str
    rule_name: str
    description: str
    hazard_categories: List[str] = Field(default_factory=list)
    unsafe_acts: List[str] = Field(default_factory=list)
    unsafe_conditions: List[str] = Field(default_factory=list)


class RuleResponse(BaseModel):
    rule_id: str
    rule_name: str
    description: str
    hazard_categories: List[str]
    unsafe_acts: List[str]
    unsafe_conditions: List[str]
