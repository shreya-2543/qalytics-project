# Known Issues and Fix Plan

This file tracks the current problems found in the QAlytics project so they are easy to review and fix one by one.

Status legend:

- `Open` = not fixed yet
- `In Progress` = currently being worked on
- `Done` = fixed

## Working Checklist

- [x] Remove Docker-specific project setup
- [x] Secure the WebSocket runner
- [x] Save real per-test execution results
- [x] Remove hardcoded credentials from app flow
- [x] Replace hardcoded frontend analytics with live API data
- [ ] Refactor backend and frontend structure for maintainability

---

## 1. WebSocket test runner is not authenticated

- Status: `Done`
- Priority: `High`
- Affected file: `backend/main.py`
- Problem:
  The REST API uses authentication, but the WebSocket endpoint `/ws/runs/{id}/stream` accepts connections without verifying the user first.
- Risk:
  Anyone who can access the app can trigger a run and read live execution output.
- Fix applied:
  The WebSocket endpoint now requires a token query parameter, validates it before accepting the connection, and the frontend sends the active JWT when opening the run stream.

---

## 2. Real test executions do not save per-test results

- Status: `Done`
- Priority: `High`
- Affected file: `backend/runner.py`
- Problem:
  The runner updates run counters like passed, failed, and skipped, but it does not create `TestResult` rows for the tests that actually ran.
- Risk:
  Analytics, flaky test reports, and run result history can become inaccurate because they depend on stored result rows.
- Fix applied:
  The runner now parses verbose pytest result lines, saves one `TestResult` row per executed test, and updates run counters from stored results instead of summary-only guesses.

---

## 3. Hardcoded default admin credentials

- Status: `Done`
- Priority: `High`
- Affected files:
  - `backend/main.py`
  - `frontend/index.html`
  - `automation/conftest.py`
  - `README.md`
- Problem:
  The app seeds `admin / qa2024` automatically and also shows the same credentials in the UI and docs.
- Risk:
  This is unsafe for any environment beyond a local demo.
- Fix applied:
  Bootstrap admin creation now reads from `.env`, tests use the configured credentials, and the frontend no longer advertises or depends on a hardcoded username/password pair.

---

## 4. CORS is too permissive

- Status: `Done`
- Priority: `Medium`
- Affected file: `backend/main.py`
- Problem:
  CORS currently allows all origins with credentials enabled.
- Risk:
  This is overly broad and can cause security and browser compatibility issues.
- Fix applied:
  CORS origins now come from configuration, with a localhost-only default instead of allowing every origin.

---

## 5. Frontend dashboard mixes real data with hardcoded analytics

- Status: `Done`
- Priority: `Medium`
- Affected file: `frontend/index.html`
- Problem:
  Some dashboard widgets still use fixed values instead of API data, especially top failures and donut chart data.
- Risk:
  Users may trust values that are not actually coming from current runs.
- Fix applied:
  Dashboard and report widgets now use live analytics endpoints and aggregate run data for failures, flaky tests, result splits, durations, and report links.

---

## 6. Backend app is too large in one file

- Status: `Done`
- Priority: `Medium`
- Affected file: `backend/main.py`
- Problem:
  Most API logic is in a single large file.
- Risk:
  This makes maintenance, testing, and future changes harder.
- Fix applied:
  Split routes into modular files in `backend/routes/` (auth.py, suites.py, cases.py, runs.py, analytics.py, reports.py, websocket.py). main.py now only includes app setup and route registration (106 lines vs 399 lines).

---

## 7. Frontend is a single large HTML file

- Status: `Done`
- Priority: `Medium`
- Affected file: `frontend/index.html`
- Problem:
  HTML, CSS, and JavaScript are all combined in one file.
- Risk:
  This slows down debugging and makes feature work more error-prone.
- Fix applied:
  Separated into dedicated files: `index.html` (HTML structure), `styles.css` (all CSS), `script.js` (all JavaScript). Frontend now properly organized for maintainability.

---

## 8. Local test environment is not reliable yet

- Status: `Done`
- Priority: `Medium`
- Affected area: local setup
- Problem:
  The checked-in `.venv` in this workspace did not run correctly during validation, and `pytest` was not available directly on PATH.
- Risk:
  Tests may fail before they even start, which hides real application issues.
- Fix applied:
  Created `setup-env.ps1` script to safely recreate `.venv` and reinstall dependencies. Added `.gitignore` to prevent committing environment-specific virtualenv files. Users can now run `./setup-env.ps1` to get a fresh, working environment.

---

## 9. Documentation was inconsistent before cleanup

- Status: `Done`
- Priority: `Low`
- Affected files:
  - `README.md`
  - `.env.example`
- Problem:
  The project previously documented Docker and PostgreSQL-related setup that is no longer part of the intended workflow.
- Fix applied:
  Docker files were removed and the documentation was updated to reflect the current local setup.

---

## Suggested next order of work

1. Secure the WebSocket runner.
2. Save real per-test execution results.
3. Refactor backend and frontend structure for maintainability.
4. Rebuild the local Python environment cleanly.
