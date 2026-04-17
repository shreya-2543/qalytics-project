"""
Reports endpoints
"""
from fastapi import APIRouter, Depends

from backend.auth import get_current_user

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/allure-url")
def allure_report_url(_=Depends(get_current_user)):
    return {"url": "http://localhost:8000/reports/allure-report/index.html"}
