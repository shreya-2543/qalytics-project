"""
Routes package for QAlytics API
"""
from backend.routes import auth, suites, cases, runs, analytics, reports, websocket, chat

__all__ = ["auth", "suites", "cases", "runs", "analytics", "reports", "websocket", "chat"]
