"""
models.py — SQLAlchemy ORM models
"""
from datetime import datetime
from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey,
    Integer, String, Text
)
from sqlalchemy.orm import relationship
from backend.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, index=True, nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=True)
    hashed_password = Column(String(128), nullable=False)
    role = Column(String(32), default="qa_engineer", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<User id={self.id} username={self.username!r}>"


class Suite(Base):
    __tablename__ = "suites"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    cases = relationship("TestCase", back_populates="suite", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Suite id={self.id} name={self.name!r}>"


class TestCase(Base):
    __tablename__ = "test_cases"

    id = Column(Integer, primary_key=True, index=True)
    suite_id = Column(Integer, ForeignKey("suites.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(String(32), default="medium", nullable=False)   # critical/high/medium/low
    status = Column(String(32), default="active", nullable=False)      # active/inactive/deprecated
    tags = Column(String(255), nullable=True)                           # comma-separated
    node_id = Column(String(512), nullable=True)                        # pytest node id
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    suite = relationship("Suite", back_populates="cases")
    results = relationship("TestResult", back_populates="test_case", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<TestCase id={self.id} title={self.title!r}>"


class TestRun(Base):
    __tablename__ = "test_runs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    suite_id = Column(Integer, ForeignKey("suites.id"), nullable=True)
    environment = Column(String(64), default="staging", nullable=False)
    marker = Column(String(255), nullable=True)
    triggered_by = Column(String(64), nullable=True)
    status = Column(String(32), default="pending", nullable=False)     # pending/running/completed/failed/aborted
    total = Column(Integer, default=0)
    passed = Column(Integer, default=0)
    failed = Column(Integer, default=0)
    skipped = Column(Integer, default=0)
    errors = Column(Integer, default=0)
    duration_seconds = Column(Float, nullable=True)
    allure_path = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    finished_at = Column(DateTime, nullable=True)

    results = relationship("TestResult", back_populates="run", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<TestRun id={self.id} name={self.name!r} status={self.status!r}>"

    @property
    def pass_rate(self) -> float:
        if not self.total:
            return 0.0
        return round(self.passed / self.total * 100, 1)


class TestResult(Base):
    __tablename__ = "test_results"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("test_runs.id"), nullable=False)
    test_case_id = Column(Integer, ForeignKey("test_cases.id"), nullable=True)
    node_id = Column(String(512), nullable=False)
    status = Column(String(32), nullable=False)   # passed/failed/skipped/error
    duration = Column(Float, nullable=True)        # seconds
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    run = relationship("TestRun", back_populates="results")
    test_case = relationship("TestCase", back_populates="results")

    def __repr__(self):
        return f"<TestResult id={self.id} run_id={self.run_id} status={self.status!r}>"
