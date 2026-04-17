"""
Test Run endpoints
"""
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend import models, schemas
from backend.auth import get_current_user
from backend.database import get_db
from fastapi import HTTPException

router = APIRouter(prefix="/api/runs", tags=["runs"])


@router.get("", response_model=List[schemas.TestRunResponse])
def list_runs(
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    return (
        db.query(models.TestRun)
        .order_by(models.TestRun.created_at.desc())
        .limit(limit)
        .all()
    )


@router.post("", response_model=schemas.TestRunResponse, status_code=201)
def create_run(
    body: schemas.TestRunCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Prepare data from request, excluding triggered_by to avoid duplication
    data = body.model_dump(exclude={'triggered_by'})
    
    # Add triggered_by with fallback to current user
    data['triggered_by'] = body.triggered_by or current_user.username
    data['status'] = "pending"
    
    run = models.TestRun(**data)
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


@router.get("/{run_id}", response_model=schemas.TestRunResponse)
def get_run(run_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    run = db.get(models.TestRun, run_id)
    if not run:
        raise HTTPException(404, "TestRun not found")
    return run


@router.get("/{run_id}/results", response_model=List[schemas.TestResultResponse])
def get_run_results(run_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    run = db.get(models.TestRun, run_id)
    if not run:
        raise HTTPException(404, "TestRun not found")
    return run.results
