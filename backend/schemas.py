"""
schemas.py — Pydantic v2 request/response schemas
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


# ─────────────────────────────────────────────────────────────
# TOKEN / AUTH
# ─────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    role: str


# ─────────────────────────────────────────────────────────────
# USER
# ─────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=64)
    email: Optional[str] = None
    password: str = Field(..., min_length=4)
    role: str = "qa_engineer"


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: Optional[str]
    role: str
    is_active: bool
    created_at: datetime


# ─────────────────────────────────────────────────────────────
# SUITE
# ─────────────────────────────────────────────────────────────

class SuiteCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    description: Optional[str] = None
    is_active: bool = True


class SuiteUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class SuiteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    case_count: int = 0

    @classmethod
    def from_orm_with_count(cls, suite) -> "SuiteResponse":
        obj = cls.model_validate(suite)
        obj.case_count = len(suite.cases)
        return obj


# ─────────────────────────────────────────────────────────────
# TEST CASE
# ─────────────────────────────────────────────────────────────

class TestCaseCreate(BaseModel):
    suite_id: int
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    priority: str = Field("medium", pattern="^(critical|high|medium|low)$")
    status: str = Field("active", pattern="^(active|inactive|deprecated)$")
    tags: Optional[str] = None
    node_id: Optional[str] = None


class TestCaseUpdate(BaseModel):
    suite_id: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[str] = None
    node_id: Optional[str] = None


class TestCaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    suite_id: int
    title: str
    description: Optional[str]
    priority: str
    status: str
    tags: Optional[str]
    node_id: Optional[str]
    created_at: datetime
    updated_at: datetime


# ─────────────────────────────────────────────────────────────
# TEST RUN
# ─────────────────────────────────────────────────────────────

class TestRunCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    suite_id: Optional[int] = None
    environment: str = "staging"
    marker: Optional[str] = None
    triggered_by: Optional[str] = None


class TestRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    suite_id: Optional[int]
    environment: str
    marker: Optional[str]
    triggered_by: Optional[str]
    status: str
    total: int
    passed: int
    failed: int
    skipped: int
    errors: int
    duration_seconds: Optional[float]
    allure_path: Optional[str]
    created_at: datetime
    finished_at: Optional[datetime]
    pass_rate: float


# ─────────────────────────────────────────────────────────────
# TEST RESULT
# ─────────────────────────────────────────────────────────────

class TestResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    run_id: int
    test_case_id: Optional[int]
    node_id: str
    status: str
    duration: Optional[float]
    error_message: Optional[str]
    created_at: datetime


# ─────────────────────────────────────────────────────────────
# ANALYTICS
# ─────────────────────────────────────────────────────────────

class AnalyticsSummary(BaseModel):
    total_suites: int
    active_suites: int
    total_cases: int
    active_cases: int
    total_runs: int
    avg_pass_rate: float
    pass_rate_trend: List[float]


class FlakyTest(BaseModel):
    node_id: str
    title: Optional[str]
    total_runs: int
    passed: int
    failed: int
    flakiness_pct: float
