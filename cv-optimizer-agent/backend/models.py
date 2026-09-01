from pydantic import BaseModel
from typing import List

class TierOneItem(BaseModel):
    title: str
    detail: str
    fix: str

class TierTwoItem(BaseModel):
    title: str
    detail: str

class ATSIssue(BaseModel):
    issue: str
    severity: str

class CVReviewResponse(BaseModel):
    filename: str
    language: str
    overall_score: int
    tier_1: List[dict]
    tier_2: List[dict]
    tier_3: List[str]
    summary: str
    ready_for_counseling: bool
    ats_score: int
    ats_issues: List[dict]
    recommendation: str