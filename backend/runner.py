"""
runner.py — Async pytest subprocess runner with live stdout streaming.

Usage (from main.py WebSocket handler):
    async for line, line_type in run_suite(run_id, db, suite_name, marker, env):
        await ws.send_json({"line": line, "type": line_type})
"""
import asyncio
import os
import re
import shutil
import time
from datetime import datetime
from typing import AsyncGenerator, Tuple

from sqlalchemy.orm import Session

from backend import models

# Root of the project (one level above backend/)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AUTOMATION_DIR = os.path.join(BASE_DIR, "automation")
ALLURE_RESULTS_DIR = os.path.join(BASE_DIR, "reports", "allure-results")
ALLURE_REPORT_DIR = os.path.join(BASE_DIR, "reports", "allure-report")
RESULT_LINE_RE = re.compile(
    r"^(?P<node_id>\S+)\s+(?P<status>PASSED|FAILED|SKIPPED|ERROR)(?:\s+\[\s*\d+%\])?$"
)


def classify_line(line: str) -> str:
    """Return a CSS class token for each output line type."""
    l = line.strip()
    if l.startswith("PASSED") or "passed" in l and "failed" not in l:
        return "pass"
    if l.startswith("FAILED") or "failed" in l:
        return "fail"
    if l.startswith("SKIPPED") or l.startswith("WARNING") or "warning" in l.lower():
        return "warn"
    if l.startswith("$") or l.startswith("//") or l.startswith("─") or l.startswith("="):
        return "dim"
    if "Collecting" in l or "allure" in l.lower() or "report" in l.lower():
        return "info"
    return "info"


def _sync_run_counts(run: models.TestRun, db: Session) -> None:
    run.passed = sum(1 for r in run.results if r.status == "passed")
    run.failed = sum(1 for r in run.results if r.status == "failed")
    run.skipped = sum(1 for r in run.results if r.status == "skipped")
    run.errors = sum(1 for r in run.results if r.status == "error")
    run.total = run.passed + run.failed + run.skipped + run.errors
    db.commit()


async def run_suite(
    run_id: int,
    db: Session,
    suite_name: str,
    marker: str,
    env: str,
) -> AsyncGenerator[Tuple[str, str], None]:
    """
    Async generator that:
      1. Updates TestRun status → running
      2. Launches pytest via asyncio subprocess
      3. Streams stdout lines with classify_line()
      4. Parses PASSED/FAILED/SKIPPED counts live
      5. Runs allure generate on exit
      6. Updates TestRun with final stats
    """
    run = db.get(models.TestRun, run_id)
    if not run:
        yield "Run not found", "fail"
        return

    # ── Set status → running ────────────────────────────────────────────────
    for result in list(run.results):
        db.delete(result)
    run.status = "running"
    run.passed = 0
    run.failed = 0
    run.skipped = 0
    run.errors = 0
    run.total = 0
    db.commit()

    start_time = time.monotonic()

    # ── Build pytest command ─────────────────────────────────────────────────
    cmd = [
        "python", "-m", "pytest",
        AUTOMATION_DIR,
        f"--alluredir={ALLURE_RESULTS_DIR}",
        "-v", "--tb=short", "--no-header",
    ]
    if marker:
        cmd += ["-m", marker]

    yield f"// Run #{run_id}: {run.name}", "dim"
    yield f"// Suite: {suite_name}  Env: {env}", "dim"
    yield "$ " + " ".join(cmd), "dim"

    # ── Launch subprocess ────────────────────────────────────────────────────
    case_lookup = {
        case.node_id: case.id
        for case in db.query(models.TestCase).filter(models.TestCase.node_id.isnot(None)).all()
    }
    seen_results: set[str] = set()

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=BASE_DIR,
            env={**os.environ, "QA_ENV": env},
        )

        async for raw in proc.stdout:
            line = raw.decode("utf-8", errors="replace").rstrip("\n")
            lt = classify_line(line)
            yield line, lt

            s = line.strip()
            match = RESULT_LINE_RE.match(s)
            if match:
                node_id = match.group("node_id")
                result_status = match.group("status").lower()
                result_key = f"{node_id}:{result_status}"
                if result_key not in seen_results:
                    seen_results.add(result_key)
                    db.add(models.TestResult(
                        run_id=run.id,
                        test_case_id=case_lookup.get(node_id),
                        node_id=node_id,
                        status=result_status,
                    ))
                    db.flush()
                    _sync_run_counts(run, db)

        await proc.wait()
        exit_code = proc.returncode

    except Exception as exc:
        yield f"Runner error: {exc}", "fail"
        run.status = "aborted"
        run.finished_at = datetime.utcnow()
        run.duration_seconds = time.monotonic() - start_time
        db.commit()
        return

    # ── Allure generate ──────────────────────────────────────────────────────
    allure_bin = shutil.which("allure")
    if allure_bin:
        yield "Generating Allure report…", "info"
        allure_proc = await asyncio.create_subprocess_exec(
            allure_bin, "generate", ALLURE_RESULTS_DIR,
            "-o", ALLURE_REPORT_DIR, "--clean",
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        await allure_proc.wait()
        yield f"✓ Report → http://localhost:8000/reports/allure-report/index.html", "pass"
        run.allure_path = ALLURE_REPORT_DIR
    else:
        yield "⚠ allure CLI not found — skipping report generation", "warn"

    # ── Finalise run ─────────────────────────────────────────────────────────
    duration = time.monotonic() - start_time
    _sync_run_counts(run, db)
    run.status = "failed" if (run.failed > 0 or run.errors > 0 or exit_code != 0) else "completed"
    run.finished_at = datetime.utcnow()
    run.duration_seconds = round(duration, 2)
    db.commit()

    yield f"─── Finished in {duration:.2f}s ───", "dim"
