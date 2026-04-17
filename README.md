# QAlytics - QA Test Management Platform

> FastAPI backend, real-time WebSocket test runner, SQLite persistence, Allure HTML reports, and a single-page dashboard.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Project Structure](#project-structure)
3. [Environment Variables](#environment-variables)
4. [API Reference](#api-reference)
5. [Running Tests](#running-tests)
6. [Allure Reports](#allure-reports)
7. [Authentication Setup](#authentication-setup)
8. [Development Notes](#development-notes)

---

## Quick Start

### Option 1: Automated Setup (Windows PowerShell)

```powershell
# Run the automated setup script
.\setup-env.ps1

# The script will:
# - Remove any old .venv
# - Create a fresh virtual environment
# - Install all dependencies
# - Verify the installation
```

### Option 2: Manual Setup

```bash
# 1. Go to the project root
cd "D:\Shreya\qalytics-project"

# 2. Create your environment file
copy .env.example .env        # Windows
# cp .env.example .env        # Linux

# 3. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate       # Windows
# source .venv/bin/activate   # Linux

# 4. Install backend dependencies
pip install -r backend/requirements.txt

# 5. Review and update the bootstrap admin credentials in .env

# 6. Seed the database
python -m backend.seed

# 7. Start the API
uvicorn backend.main:app --reload --port 8000

# 8. Open the frontend
python3 -m http.server 3000 --directory frontend
```

---

## Project Structure

```text
qalytics-project/
|-- backend/
|   |-- __init__.py
|   |-- config.py
|   |-- main.py
|   |-- database.py
|   |-- models.py
|   |-- schemas.py
|   |-- auth.py
|   |-- runner.py
|   |-- seed.py
|   |-- requirements.txt
|   `-- alembic/
|       |-- env.py
|       |-- script.py.mako
|       `-- versions/
|           `-- 001_initial_schema.py
|-- automation/
|   |-- conftest.py
|   `-- smoke/
|       `-- test_sample.py
|-- frontend/
|   `-- index.html
|-- reports/
|   |-- allure-results/
|   `-- allure-report/
|-- alembic.ini
|-- .env.example
|-- command.txt
|-- KNOWN_ISSUES.md
`-- README.md
```

---

## Environment Variables

Copy `.env.example` to `.env` and edit it before running the app.

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | JWT signing secret |
| `DATABASE_URL` | SQLAlchemy database URL |
| `QA_ENV` | Default test environment |
| `CORS_ALLOWED_ORIGINS` | Comma-separated frontend origins allowed to call the API |
| `BOOTSTRAP_ADMIN_ENABLED` | Whether to create the configured admin on startup |
| `BOOTSTRAP_ADMIN_USERNAME` | Bootstrap admin username |
| `BOOTSTRAP_ADMIN_PASSWORD` | Bootstrap admin password |
| `BOOTSTRAP_ADMIN_EMAIL` | Bootstrap admin email |
| `BOOTSTRAP_ADMIN_ROLE` | Bootstrap admin role |
| `ALLURE_BIN` | Optional path to the `allure` CLI |

---

## API Reference

Base URL: `http://localhost:8000`

Interactive docs: `http://localhost:8000/docs`

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/auth/login` | Obtain JWT token |
| GET | `/api/auth/me` | Current user info |
| GET | `/api/suites` | List all suites |
| POST | `/api/suites` | Create a suite |
| GET | `/api/suites/{id}` | Get suite by ID |
| PATCH | `/api/suites/{id}` | Update suite |
| DELETE | `/api/suites/{id}` | Delete suite |
| GET | `/api/cases` | List test cases |
| POST | `/api/cases` | Create test case |
| GET | `/api/cases/{id}` | Get case by ID |
| PATCH | `/api/cases/{id}` | Update test case |
| DELETE | `/api/cases/{id}` | Delete test case |
| GET | `/api/runs` | List test runs |
| POST | `/api/runs` | Create test run |
| GET | `/api/runs/{id}` | Get run by ID |
| GET | `/api/runs/{id}/results` | Get run results |
| GET | `/api/analytics/summary` | Dashboard summary |
| GET | `/api/analytics/flaky` | Flaky test analysis |
| GET | `/api/analytics/top-failures` | Top failing tests |
| GET | `/api/analytics/trend` | Pass rate trend |
| GET | `/api/reports/allure-url` | Allure report URL |
| WS | `/ws/runs/{id}/stream` | Authenticated live execution stream |

---

## Running Tests

```bash
# Run all automation tests
pytest automation/ -v --alluredir=reports/allure-results/

# Run only smoke tests
pytest automation/ -m smoke -v --alluredir=reports/allure-results/

# Generate the Allure report
pytest automation/ --alluredir=reports/allure-results/
allure generate reports/allure-results/ -o reports/allure-report/ --clean
```

---

## Allure Reports

Install the Allure CLI and open:

`http://localhost:8000/reports/allure-report/index.html`

---

## Authentication Setup

The app no longer relies on hardcoded demo credentials in code.

1. Copy `.env.example` to `.env`.
2. Set `BOOTSTRAP_ADMIN_USERNAME` and `BOOTSTRAP_ADMIN_PASSWORD`.
3. Start the API.
4. Sign in with those configured credentials.

---

## Development Notes

- Set `const MOCK = true;` in `frontend/index.html` to use frontend-only mock data.
- Run `alembic upgrade head` from the project root to apply migrations.
- Run `python -m backend.seed` instead of `python backend/seed.py`.
- Disconnecting the WebSocket cancels the subprocess-backed test run.
- `backend/config.py` loads values from `.env` automatically.
