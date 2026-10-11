"""Pydantic request/response contracts shared by all endpoints."""
from typing import Literal, Optional
from pydantic import BaseModel, Field


class EducationItem(BaseModel):
    degree: str
    field: Optional[str] = None
    institution: Optional[str] = None


class ParsedResume(BaseModel):
    skills: list[str]
    years_experience: float = Field(ge=0)
    current_role: Optional[str] = None
    education: list[EducationItem] = []
    extraction_method: Literal["regex", "hybrid"] = "regex"


class MatchRequest(BaseModel):
    skills: list[str] = Field(min_length=1)
    years_experience: float = Field(default=0, ge=0, le=60)
    industry: str = "Any"
    target_role: Optional[str] = None      # "dream role"; defaults to best match


class MissingSkill(BaseModel):
    skill: str
    demand_pct: float                      # % of listings for the role that require it
    priority: Literal["Critical", "Important", "Nice-to-have"]


class RoleMatch(BaseModel):
    role: str
    industry: str
    confidence_pct: float
    embedding_similarity: float            # raw cosine similarity (0-1)
    skill_coverage_pct: float
    matched_skills: list[str]
    missing_skills: list[str]


class SkillGap(BaseModel):
    target_role: str
    readiness_pct: float
    matched_skills: list[str]
    missing_skills: list[MissingSkill]


class MatchResponse(BaseModel):
    top_matches: list[RoleMatch]
    skill_gap: SkillGap
    jobs_searched: int


class RoadmapRequest(BaseModel):
    target_role: str
    missing_skills: list[str]
    current_skills: list[str] = []
    weekly_hours: int = Field(default=8, ge=1, le=60)


class Resource(BaseModel):
    title: str
    platform: str
    url: str


class WeekPlan(BaseModel):
    week: int
    theme: str
    skills: list[str]
    goals: list[str]
    resources: list[Resource]
    project: str


class RoadmapResponse(BaseModel):
    target_role: str
    weekly_hours: int
    weeks: list[WeekPlan]
    capstone_project: str
    generated_by: Literal["llm-chain", "template-fallback", "mixed"]
