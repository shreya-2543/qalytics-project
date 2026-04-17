"""
Analytics endpoints
"""
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, text
from sqlalchemy.orm import Session

from backend import models, schemas
from backend.auth import get_current_user
from backend.database import get_db

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/summary", response_model=schemas.AnalyticsSummary)
def analytics_summary(db: Session = Depends(get_db), _=Depends(get_current_user)):
    total_suites = db.query(func.count(models.Suite.id)).scalar() or 0
    active_suites = db.query(func.count(models.Suite.id)).filter_by(is_active=True).scalar() or 0
    total_cases = db.query(func.count(models.TestCase.id)).scalar() or 0
    active_cases = db.query(func.count(models.TestCase.id)).filter_by(status="active").scalar() or 0
    total_runs = db.query(func.count(models.TestRun.id)).scalar() or 0

    recent_runs = (
        db.query(models.TestRun)
        .filter(models.TestRun.status == "completed")
        .order_by(models.TestRun.created_at.desc())
        .limit(10)
        .all()
    )
    rates = [r.pass_rate for r in recent_runs]
    avg = round(sum(rates) / len(rates), 1) if rates else 0.0
    trend = list(reversed(rates[:5]))

    return schemas.AnalyticsSummary(
        total_suites=total_suites,
        active_suites=active_suites,
        total_cases=total_cases,
        active_cases=active_cases,
        total_runs=total_runs,
        avg_pass_rate=avg,
        pass_rate_trend=trend,
    )


@router.get("/flaky", response_model=List[schemas.FlakyTest])
def analytics_flaky(db: Session = Depends(get_db), _=Depends(get_current_user)):
    results = db.query(models.TestResult).all()
    # Aggregate by node_id
    agg: dict = {}
    for r in results:
        entry = agg.setdefault(r.node_id, {"passed": 0, "failed": 0, "test_case_id": r.test_case_id})
        if r.status == "passed":
            entry["passed"] += 1
        elif r.status in ("failed", "error"):
            entry["failed"] += 1

    flaky = []
    for node_id, stats in agg.items():
        if stats["passed"] > 0 and stats["failed"] > 0:
            total = stats["passed"] + stats["failed"]
            pct = round(stats["failed"] / total * 100, 1)
            title = None
            if stats["test_case_id"]:
                tc = db.get(models.TestCase, stats["test_case_id"])
                title = tc.title if tc else None
            flaky.append(schemas.FlakyTest(
                node_id=node_id, title=title,
                total_runs=total, passed=stats["passed"],
                failed=stats["failed"], flakiness_pct=pct,
            ))

    return sorted(flaky, key=lambda x: x.flakiness_pct, reverse=True)


@router.get("/top-failures")
def analytics_top_failures(limit: int = 5, db: Session = Depends(get_db), _=Depends(get_current_user)):
    rows = db.execute(
        text(
            "SELECT node_id, COUNT(*) as cnt FROM test_results "
            "WHERE status IN ('failed','error') "
            "GROUP BY node_id ORDER BY cnt DESC LIMIT :lim"
        ),
        {"lim": limit},
    ).fetchall()
    titles = {
        case.node_id: case.title
        for case in db.query(models.TestCase).filter(models.TestCase.node_id.isnot(None)).all()
    }
    return [{"node_id": r.node_id, "title": titles.get(r.node_id), "count": r.cnt} for r in rows]


@router.get("/trend")
def analytics_trend(last: int = Query(10, le=50), db: Session = Depends(get_db), _=Depends(get_current_user)):
    runs = (
        db.query(models.TestRun)
        .filter_by(status="completed")
        .order_by(models.TestRun.created_at.desc())
        .limit(last)
        .all()
    )
    return [{"id": r.id, "name": r.name, "pass_rate": r.pass_rate, "created_at": r.created_at} for r in reversed(runs)]
