"""
WebSocket endpoint for live test runner
"""
import asyncio

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from backend import models
from backend.auth import verify_token
from backend.database import get_db
from backend.runner import run_suite

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/runs/{run_id}/stream")
async def websocket_run_stream(websocket: WebSocket, run_id: int):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008, reason="Missing auth token")
        return

    try:
        verify_token(token)
    except HTTPException:
        await websocket.close(code=1008, reason="Invalid auth token")
        return

    await websocket.accept()
    db = next(get_db())

    run = db.get(models.TestRun, run_id)
    if not run:
        await websocket.send_json({"error": "Run not found"})
        await websocket.close()
        return

    suite = db.get(models.Suite, run.suite_id) if run.suite_id else None
    suite_name = suite.name if suite else "All Suites"

    task = asyncio.create_task(
        _run_and_stream(websocket, run_id, suite_name, run.marker or "", run.environment)
    )
    try:
        await task
    except WebSocketDisconnect:
        task.cancel()
    except Exception as exc:
        await websocket.send_json({"error": str(exc)})
    finally:
        db.close()


async def _run_and_stream(websocket: WebSocket, run_id: int, suite_name: str, marker: str, env: str):
    db = next(get_db())
    try:
        async for line, line_type in run_suite(run_id, db, suite_name, marker, env):
            await websocket.send_json({"line": line, "type": line_type})
        run = db.get(models.TestRun, run_id)
        if run:
            await websocket.send_json({
                "done": True,
                "run": {
                    "id": run.id, "status": run.status,
                    "passed": run.passed, "failed": run.failed,
                    "skipped": run.skipped, "total": run.total,
                    "pass_rate": run.pass_rate,
                    "duration_seconds": run.duration_seconds,
                },
            })
    finally:
        db.close()
        await websocket.close()
