"""
seed.py — Idempotent database seeder.
Run from project root: python -m backend.seed
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime, timedelta
from backend.database import SessionLocal, engine, Base
from backend.models import User, Suite, TestCase, TestRun, TestResult
from backend.auth import hash_password

Base.metadata.create_all(bind=engine)

db = SessionLocal()

# ── Admin user ────────────────────────────────────────────────────────────────
if not db.query(User).filter_by(username="admin").first():
    db.add(User(
        username="admin",
        email="admin@qalytics.dev",
        hashed_password=hash_password("qa2024"),
        role="admin",
    ))
    print("[seed] Created user: admin")
else:
    print("[seed] User admin already exists — skipping")

db.commit()

# ── Suites ────────────────────────────────────────────────────────────────────
suite_defs = [
    {"name": "Smoke Tests",  "description": "Critical path validation",    "is_active": True},
    {"name": "Regression",   "description": "Full regression coverage",    "is_active": True},
    {"name": "API Tests",    "description": "REST endpoint validation",    "is_active": True},
    {"name": "UI E2E",       "description": "Pylenium end-to-end flows",   "is_active": False},
]

suite_map = {}
for sd in suite_defs:
    existing = db.query(Suite).filter_by(name=sd["name"]).first()
    if not existing:
        suite = Suite(**sd)
        db.add(suite)
        db.flush()
        suite_map[sd["name"]] = suite
        print(f"[seed] Created suite: {sd['name']}")
    else:
        suite_map[sd["name"]] = existing
        print(f"[seed] Suite '{sd['name']}' exists — skipping")

db.commit()

# ── Test Cases ────────────────────────────────────────────────────────────────
case_defs = [
    {"suite": "Smoke Tests",  "title": "Verify login with valid credentials",    "priority": "critical", "status": "active",   "tags": "smoke,login",    "node_id": "automation/smoke/test_auth.py::test_valid_login"},
    {"suite": "Smoke Tests",  "title": "Verify logout clears session cookie",    "priority": "high",     "status": "active",   "tags": "smoke,auth",     "node_id": "automation/smoke/test_auth.py::test_logout"},
    {"suite": "Regression",   "title": "Create new user via API endpoint",       "priority": "high",     "status": "active",   "tags": "api,users",      "node_id": "automation/regression/test_users.py::test_create_user"},
    {"suite": "API Tests",    "title": "GET /api/cases returns 200",             "priority": "medium",   "status": "active",   "tags": "api,cases",      "node_id": "automation/api/test_cases.py::test_get_cases"},
    {"suite": "API Tests",    "title": "POST /api/runs triggers execution",      "priority": "critical", "status": "active",   "tags": "api,runs,smoke", "node_id": "automation/api/test_runs.py::test_trigger_run"},
    {"suite": "Regression",   "title": "Dashboard loads under 2s on 3G",        "priority": "medium",   "status": "inactive", "tags": "perf",           "node_id": "automation/regression/test_perf.py::test_dashboard_load"},
    {"suite": "UI E2E",       "title": "Login form submits on Enter key",        "priority": "low",      "status": "active",   "tags": "ui,a11y",        "node_id": "automation/e2e/test_a11y.py::test_enter_submit"},
    {"suite": "Smoke Tests",  "title": "Reset password email sent successfully", "priority": "high",     "status": "active",   "tags": "smoke,email",    "node_id": "automation/smoke/test_auth.py::test_password_reset"},
    {"suite": "API Tests",    "title": "DELETE /api/cases/{id} returns 204",     "priority": "medium",   "status": "active",   "tags": "api,cases",      "node_id": "automation/api/test_cases.py::test_delete_case"},
    {"suite": "Regression",   "title": "Suite filter returns correct cases",     "priority": "medium",   "status": "active",   "tags": "regression,api", "node_id": "automation/regression/test_suites.py::test_suite_filter"},
]

case_map = {}
for cd in case_defs:
    suite = suite_map.get(cd["suite"])
    if not suite:
        continue
    existing = db.query(TestCase).filter_by(suite_id=suite.id, title=cd["title"]).first()
    if not existing:
        tc = TestCase(
            suite_id=suite.id,
            title=cd["title"],
            priority=cd["priority"],
            status=cd["status"],
            tags=cd["tags"],
            node_id=cd["node_id"],
        )
        db.add(tc)
        db.flush()
        case_map[cd["node_id"]] = tc
        print(f"[seed] Created case: {cd['title'][:50]}")
    else:
        case_map[cd["node_id"]] = existing
        print(f"[seed] Case exists — skipping: {cd['title'][:50]}")

db.commit()

# ── Test Runs ────────────────────────────────────────────────────────────────
run_defs = [
    {"name": "Initial Run #1",     "env": "staging",    "days_ago": 4, "passed": 7,  "failed": 2, "skipped": 1, "total": 10, "status": "completed"},
    {"name": "Smoke Quick Check",  "env": "dev",        "days_ago": 3, "passed": 8,  "failed": 0, "skipped": 0, "total": 8,  "status": "completed"},
    {"name": "Full Regression #3", "env": "production", "days_ago": 2, "passed": 36, "failed": 6, "skipped": 0, "total": 42, "status": "failed"},
    {"name": "API Regression #4",  "env": "staging",    "days_ago": 1, "passed": 15, "failed": 0, "skipped": 0, "total": 15, "status": "completed"},
    {"name": "Nightly Smoke #5",   "env": "staging",    "days_ago": 0, "passed": 11, "failed": 1, "skipped": 0, "total": 12, "status": "completed"},
]

for rd in run_defs:
    existing = db.query(TestRun).filter_by(name=rd["name"]).first()
    if existing:
        print(f"[seed] Run '{rd['name']}' exists — skipping")
        continue
    ts = datetime.utcnow() - timedelta(days=rd["days_ago"], hours=1)
    run = TestRun(
        name=rd["name"],
        environment=rd["env"],
        triggered_by="admin",
        status=rd["status"],
        passed=rd["passed"],
        failed=rd["failed"],
        skipped=rd["skipped"],
        errors=0,
        total=rd["total"],
        duration_seconds=round(rd["total"] * 0.8 + rd["failed"] * 1.5, 1),
        created_at=ts,
        finished_at=ts + timedelta(seconds=rd["total"] * 1.2),
    )
    db.add(run)
    db.flush()
    print(f"[seed] Created run: {rd['name']}")

    # Seed sample TestResult rows for each run
    node_ids = list(case_map.keys())[:min(rd["total"], len(case_map))]
    for i, node_id in enumerate(node_ids):
        if i < rd["passed"]:
            result_status = "passed"
        elif i < rd["passed"] + rd["failed"]:
            result_status = "failed"
        else:
            result_status = "skipped"
        tc = case_map.get(node_id)
        db.add(TestResult(
            run_id=run.id,
            test_case_id=tc.id if tc else None,
            node_id=node_id,
            status=result_status,
            duration=round(0.3 + i * 0.15, 2),
            error_message="AssertionError: expected result mismatch" if result_status == "failed" else None,
            created_at=ts,
        ))

db.commit()
db.close()
print("\n[seed] Done ✓")
