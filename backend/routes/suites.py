"""
Test Suite endpoints
"""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend import models, schemas
from backend.auth import get_current_user
from backend.database import get_db
from backend.pagination import paginate, PaginatedResponse

router = APIRouter(prefix="/api/suites", tags=["suites"])


@router.get("", response_model=List[schemas.SuiteResponse])
def list_suites(
    active_only: bool = False,
    limit: int = Query(50, ge=1, le=1000, description="Items per page"),
    offset: int = Query(0, ge=0, description="Items to skip"),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """List test suites with pagination support"""
    q = db.query(models.Suite)
    if active_only:
        q = q.filter_by(is_active=True)
    
    # Get total before pagination
    total = q.count()
    
    # Apply pagination
    suites = paginate(q.order_by(models.Suite.created_at), limit, offset).all()
    
    return [schemas.SuiteResponse.from_orm_with_count(s) for s in suites]


@router.post("", response_model=schemas.SuiteResponse, status_code=201)
def create_suite(
    body: schemas.SuiteCreate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    if db.query(models.Suite).filter_by(name=body.name).first():
        raise HTTPException(status_code=409, detail="Suite name already exists")
    suite = models.Suite(**body.model_dump())
    db.add(suite)
    db.commit()
    db.refresh(suite)
    return schemas.SuiteResponse.from_orm_with_count(suite)


@router.get("/{suite_id}", response_model=schemas.SuiteResponse)
def get_suite(suite_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    suite = db.get(models.Suite, suite_id)
    if not suite:
        raise HTTPException(404, "Suite not found")
    return schemas.SuiteResponse.from_orm_with_count(suite)


@router.patch("/{suite_id}", response_model=schemas.SuiteResponse)
def update_suite(
    suite_id: int,
    body: schemas.SuiteUpdate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    suite = db.get(models.Suite, suite_id)
    if not suite:
        raise HTTPException(404, "Suite not found")
    for k, v in body.model_dump(exclude_none=True).items():
        setattr(suite, k, v)
    suite.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(suite)
    return schemas.SuiteResponse.from_orm_with_count(suite)


@router.delete("/{suite_id}", status_code=204)
def delete_suite(suite_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    suite = db.get(models.Suite, suite_id)
    if not suite:
        raise HTTPException(404, "Suite not found")
    db.delete(suite)
    db.commit()
