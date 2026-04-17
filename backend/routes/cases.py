"""
Test Case endpoints
"""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend import models, schemas
from backend.auth import get_current_user
from backend.database import get_db

router = APIRouter(prefix="/api/cases", tags=["cases"])


@router.get("", response_model=List[schemas.TestCaseResponse])
def list_cases(
    suite_id: Optional[int] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    q = db.query(models.TestCase)
    if suite_id:
        q = q.filter_by(suite_id=suite_id)
    if priority:
        q = q.filter_by(priority=priority)
    if status:
        q = q.filter_by(status=status)
    return q.order_by(models.TestCase.created_at).all()


@router.post("", response_model=schemas.TestCaseResponse, status_code=201)
def create_case(
    body: schemas.TestCaseCreate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    if not db.get(models.Suite, body.suite_id):
        raise HTTPException(404, "Suite not found")
    case = models.TestCase(**body.model_dump())
    db.add(case)
    db.commit()
    db.refresh(case)
    return case


@router.get("/{case_id}", response_model=schemas.TestCaseResponse)
def get_case(case_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    case = db.get(models.TestCase, case_id)
    if not case:
        raise HTTPException(404, "TestCase not found")
    return case


@router.patch("/{case_id}", response_model=schemas.TestCaseResponse)
def update_case(
    case_id: int,
    body: schemas.TestCaseUpdate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    case = db.get(models.TestCase, case_id)
    if not case:
        raise HTTPException(404, "TestCase not found")
    for k, v in body.model_dump(exclude_none=True).items():
        setattr(case, k, v)
    case.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(case)
    return case


@router.delete("/{case_id}", status_code=204)
def delete_case(case_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    case = db.get(models.TestCase, case_id)
    if not case:
        raise HTTPException(404, "TestCase not found")
    db.delete(case)
    db.commit()
