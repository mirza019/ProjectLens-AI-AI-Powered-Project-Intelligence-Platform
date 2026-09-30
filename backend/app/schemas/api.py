from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional

class QueryRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)
    project_id: Optional[str] = None
    contract_id: Optional[str] = None
class Source(BaseModel):
    id: str; title: str; section: Optional[str] = None; page: Optional[int] = None; contract_id: Optional[str] = None
class AIResponse(BaseModel):
    summary: str; key_findings: list[str]; recommended_attention: list[str]; source_ids: list[str]; sources: list[Source]; confidence: float; pipeline: str; review_status: str = "Draft"; run_id: Optional[str] = None
class FeedbackCreate(BaseModel):
    ai_run_id: str; helpful: bool; comment: Optional[str] = Field(default=None, max_length=1000)
class LoginRequest(BaseModel):
    email: str; password: str = Field(min_length=6,max_length=128)
class UseCaseCreate(BaseModel):
    title: str; business_problem: str; current_process: str; owner: str
    users: str = "Project teams"; frequency: str = "Monthly"; available_data: str = ""; data_sensitivity: str = "Internal"; manual_effort_hours: float = 0; expected_outcome: str = ""
class UseCaseReview(BaseModel):
    decision: str
    comments: str = Field(min_length=3, max_length=2000)
class UseCaseStageChange(BaseModel):
    status: str
    comments: str = Field(min_length=3, max_length=2000)
