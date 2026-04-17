# 🚀 QAlytics - Complete Getting Started Guide

**Last Updated:** April 18, 2026  
**Status:** ✅ Production Ready

---

## 📊 What is QAlytics?

QAlytics is a **professional QA test management platform** that helps teams:

- Organize and execute automated tests
- Track test results and metrics
- Generate comprehensive test reports
- Monitor test execution in real-time
- Analyze test trends and failures

**Built with:** FastAPI (backend), Vanilla JS (frontend), SQLite (database)

---

## 🎯 Quick Start (Choose Your Path)

### **Path 1: Docker (Recommended - 1 minute)** ⭐⭐⭐

```bash
cd /mnt/d/Shreya/qalytics-project
docker-compose up -d
```

**Then open:**

- 🎨 Frontend: <http://localhost:3000>
- 🔌 API: <http://localhost:8000>
- 📚 API Docs: <http://localhost:8000/docs>

**Stop:** `docker-compose down`

---

### **Path 2: Local Development (5 minutes)**

```bash
# 1. Activate virtual environment
cd /mnt/d/Shreya/qalytics-project
source .venv/bin/activate

# 2. Start backend (Terminal 1)
uvicorn backend.main:app --reload --port 8000

# 3. Start frontend (Terminal 2)
python3 -m http.server 3000 --directory frontend

# 4. Seed dummy data (Terminal 3)
python3 -m backend.seed

# 5. Run tests (Terminal 3)
pytest automation/ -v
```

**Then open:**

- Frontend: <http://localhost:3000>
- API: <http://localhost:8000>
- API Docs: <http://localhost:8000/docs>

---

### **Path 3: Just Run Tests**

```bash
cd /mnt/d/Shreya/qalytics-project
source .venv/bin/activate

# Make sure API is running on port 8000 first!
pytest automation/integration/test_api.py -v
```

---

## 🔐 Login Credentials

**Default Admin User:**

- Username: `admin`
- Password: `admin`

(Configured in `.env` file)

---

## 🎨 Frontend Features

### **Dashboard**

- View all test suites
- See test execution history
- Monitor pass/fail rates
- Access real-time WebSocket streams

### **Test Management**

- Create/edit test suites
- Add test cases with priorities
- Tag tests for organization
- Track test status (active/inactive)

### **Analytics**

- Pass/fail trends
- Top failing tests
- Flaky test detection
- Environment comparison

### **Reports**

- Allure HTML reports
- Test execution details
- Performance metrics
- Error messages

---

## 🔌 API Features

### **Authentication**

```bash
# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'

# Get current user
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/auth/me
```

### **Test Suites**

```bash
# List suites (with pagination!)
curl http://localhost:8000/api/suites?limit=10&offset=0

# Create suite
curl -X POST http://localhost:8000/api/suites \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{
    "name":"Smoke Tests",
    "description":"Critical path validation",
    "is_active":true
  }'
```

### **Test Cases**

```bash
# List cases with filtering
curl "http://localhost:8000/api/cases?priority=high&status=active"

# Create test case
curl -X POST http://localhost:8000/api/cases \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{
    "suite_id":1,
    "title":"Login test",
    "priority":"critical",
    "status":"active"
  }'
```

### **Test Runs**

```bash
# List runs
curl http://localhost:8000/api/runs

# Create run
curl -X POST http://localhost:8000/api/runs \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{
    "name":"Nightly Smoke Run",
    "environment":"staging",
    "marker":"smoke"
  }'
```

### **Analytics**

```bash
# Get summary
curl http://localhost:8000/api/analytics/summary

# Get top failures
curl http://localhost:8000/api/analytics/top-failures

# Get flaky tests
curl http://localhost:8000/api/analytics/flaky-tests
```

**📚 Full API documentation:** Visit <http://localhost:8000/docs>

---

## 📁 Project Structure

```
qalytics-project/
│
├── backend/                          # FastAPI backend
│   ├── routes/                       # Organized endpoints
│   │   ├── auth.py                   # Authentication
│   │   ├── suites.py                 # Suite management
│   │   ├── cases.py                  # Test cases
│   │   ├── runs.py                   # Test execution
│   │   ├── analytics.py              # Analytics
│   │   ├── reports.py                # Report access
│   │   └── websocket.py              # Live streaming
│   ├── main.py                       # App setup
│   ├── models.py                     # Database models
│   ├── schemas.py                    # Data validation
│   ├── auth.py                       # Auth logic
│   ├── database.py                   # DB setup
│   ├── config.py                     # Configuration
│   ├── logging_utils.py              # Structured logging
│   ├── pagination.py                 # Pagination helpers
│   └── seed.py                       # Test data
│
├── frontend/                         # Web UI
│   ├── index.html                    # HTML structure
│   ├── styles.css                    # Design & layout
│   ├── script.js                     # Logic & interactivity
│   └── index_old.html                # Backup
│
├── automation/                       # Tests
│   ├── smoke/                        # Smoke tests
│   │   └── test_sample.py
│   └── integration/                  # Integration tests
│       └── test_api.py               # 50+ API tests
│
├── .github/
│   └── workflows/
│       └── ci-cd.yml                 # GitHub Actions
│
├── Dockerfile                        # Docker image
├── docker-compose.yml                # Multi-service setup
├── .env                              # Configuration
├── .gitignore                        # Git exclusions
└── requirements.txt                  # Python packages
```

---

## 🧪 Testing

### **Run All Tests**

```bash
pytest automation/ -v
```

### **Run Specific Test Suite**

```bash
# Smoke tests only
pytest automation/smoke/ -v

# Integration tests only
pytest automation/integration/ -v

# Specific test class
pytest automation/integration/test_api.py::TestAuthEndpoints -v
```

### **Run with Coverage Report**

```bash
pytest automation/ --cov=backend --cov-report=html
# Open htmlcov/index.html in browser
```

### **Run with Performance Timing**

```bash
pytest automation/integration/test_api.py -v --durations=10
```

---

## 📊 Database

### **Schema**

```
users table:
  - id (PK)
  - username (unique)
  - email
  - hashed_password
  - role (admin/qa_engineer)

suites table:
  - id (PK)
  - name (unique)
  - description
  - is_active

test_cases table:
  - id (PK)
  - suite_id (FK)
  - title
  - priority (critical/high/medium/low)
  - status (active/inactive)
  - tags (comma-separated)

test_runs table:
  - id (PK)
  - name
  - status (pending/running/completed/failed)
  - passed/failed/skipped counts
  - environment
  - triggered_by
  - created_at
  - finished_at

test_results table:
  - id (PK)
  - run_id (FK)
  - test_case_id (FK)
  - status (passed/failed/skipped)
  - duration
  - error_message
```

### **Seed Dummy Data**

```bash
python -m backend.seed
```

This creates:

- 1 admin user
- 4 test suites
- 10 test cases
- 5 test runs with results

---

## 🔧 Configuration

### **Environment Variables** (`.env`)

```env
# Server
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=sqlite:///./backend/qalytics.db

# Admin User
BOOTSTRAP_ADMIN_ENABLED=true
BOOTSTRAP_ADMIN_USERNAME=admin
BOOTSTRAP_ADMIN_PASSWORD=admin
BOOTSTRAP_ADMIN_EMAIL=admin@qalytics.dev

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
```

### **Update Configuration**

```bash
# Edit .env
nano .env

# Restart API for changes to take effect
# (auto-reload with --reload flag)
```

---

## 🚀 New Features Added

### **Pagination**

```python
# GET /api/suites?limit=50&offset=0
# Returns: items, total, limit, offset, pages, current_page
```

### **Structured Logging**

- All requests logged as JSON
- Performance timing for each request
- Request/response tracking
- Error context preservation

### **Docker Support**

- One-command local setup: `docker-compose up -d`
- Multi-service orchestration
- Volume mapping for development
- Health checks

### **CI/CD Pipeline**

- Automatic tests on every push to GitHub
- Code quality checks
- Security scanning
- Docker image building

### **Integration Tests**

- 50+ comprehensive API tests
- Authentication coverage
- CRUD operation validation
- Error handling tests
- Performance tests
- Concurrent request tests

---

## 📈 Monitoring & Logging

### **View Logs**

```bash
# Docker
docker-compose logs -f backend

# Local (watch console where you ran uvicorn)
# Each request appears as JSON:
{
  "timestamp": "2026-04-18T10:30:45.123Z",
  "method": "POST",
  "path": "/api/suites",
  "status_code": 201,
  "duration_ms": 45.2,
  "user": "admin"
}
```

### **Check API Health**

```bash
curl http://localhost:8000/api/health
# Response: {"status":"ok","version":"1.0.0"}
```

### **View API Documentation**

```
http://localhost:8000/docs  # Interactive Swagger UI
http://localhost:8000/redoc # ReDoc documentation
```

---

## 🔄 Development Workflow

### **Make Backend Changes**

1. Edit file in `backend/routes/` or `backend/`
2. API automatically reloads (with `--reload` flag)
3. Test changes: `pytest automation/ -v`

### **Make Frontend Changes**

1. Edit file in `frontend/` (HTML, CSS, or JS)
2. Refresh browser (Ctrl+R or Cmd+R)
3. Changes appear immediately

### **Make Database Schema Changes**

1. Update `backend/models.py`
2. Generate migration: `alembic revision --autogenerate -m "description"`
3. Apply migration: `alembic upgrade head`
4. Restart API

---

## 🐛 Troubleshooting

### **Docker won't start**

```bash
# Check if ports are in use
lsof -i :8000  # Check port 8000
lsof -i :3000  # Check port 3000

# Kill process if needed
kill -9 <PID>

# Rebuild without cache
docker-compose up -d --build
```

### **Tests fail with "Connection refused"**

```bash
# Make sure API is running
curl http://localhost:8000/api/health

# Restart API
docker-compose restart backend
# Or press Ctrl+C and restart manually
```

### **Admin login fails (401)**

```bash
# Check .env file has correct credentials
cat .env | grep BOOTSTRAP_ADMIN

# Verify user is in database
python3 check-admin.py

# Seed new user if needed
rm backend/qalytics.db  # Delete database
# Restart API (will create fresh DB with admin user)
```

### **Database is locked**

```bash
# Stop all processes
docker-compose down

# Or kill Python processes
pkill -f uvicorn
pkill -f "python3 -m http.server"

# Remove lock file if it exists
rm backend/qalytics.db-*

# Restart
docker-compose up -d
```

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `README.md` | Overview |
| `QUICK_REFERENCE.md` | One-page cheat sheet |
| `DEPLOYMENT_GUIDE.md` | Production deployment |
| `ARCHITECTURE.md` | System design |
| `IMPROVEMENTS_ROADMAP.md` | Future features |
| `IMPROVEMENTS_IMPLEMENTED.md` | What was added |
| `FINAL_SUMMARY.md` | Project summary |
| **You are here** | Getting Started |

---

## 🎯 Next Steps

**Choose your next action:**

### **If you want to contribute code:**

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make changes
3. Run tests: `pytest automation/ -v`
4. Push and create Pull Request
5. CI/CD pipeline runs automatically

### **If you want to deploy to production:**

1. Read `DEPLOYMENT_GUIDE.md`
2. Choose platform (AWS/Heroku/Kubernetes)
3. Follow step-by-step instructions

### **If you want to understand the code:**

1. Read `ARCHITECTURE.md`
2. Look at `backend/routes/` for endpoint examples
3. Check `automation/integration/test_api.py` for API usage examples

### **If you want to add a new feature:**

1. Check `IMPROVEMENTS_ROADMAP.md` for ideas
2. Create new endpoint in `backend/routes/`
3. Add tests in `automation/integration/`
4. Update API documentation (auto-generated in `/docs`)

---

## 💡 Pro Tips

### **Tip 1: Use API Documentation**

Instead of curl, use Swagger UI at <http://localhost:8000/docs>

- Click endpoint to see details
- Try requests interactively
- See response examples

### **Tip 2: Add Debug Logging**

```python
from backend.logging_utils import log_info

log_info("create_suite", "Suite created successfully", 
         context={"suite_id": 123, "name": "Smoke Tests"})
```

### **Tip 3: Pagination for Large Datasets**

```bash
# Get 50 items starting from position 100
curl "http://localhost:8000/api/suites?limit=50&offset=100"
```

### **Tip 4: Filter by Status/Priority**

```bash
# Get only active, high-priority test cases
curl "http://localhost:8000/api/cases?status=active&priority=high"
```

---

## 📞 Getting Help

| Issue | Solution |
|-------|----------|
| API won't start | Check logs: `docker-compose logs -f backend` |
| Tests fail | Make sure API is running on port 8000 |
| Frontend not loading | Check frontend server running on port 3000 |
| Database error | Delete `backend/qalytics.db` and restart |
| Auth issues | Run `python3 check-admin.py` to diagnose |

---

## ✅ Quick Checklist

- [ ] Clone/download project
- [ ] Install Docker (for easy setup)
- [ ] Run `docker-compose up -d`
- [ ] Open <http://localhost:3000> in browser
- [ ] Login with admin/admin
- [ ] Run `pytest automation/ -v`
- [ ] Read `QUICK_REFERENCE.md`
- [ ] Check <http://localhost:8000/docs> for API
- [ ] Read relevant documentation

---

## 🎉 You're All Set

Your QAlytics instance is now running with:

- ✅ Production-ready backend
- ✅ Professional frontend
- ✅ 50+ integration tests
- ✅ Structured logging
- ✅ Docker support
- ✅ CI/CD pipeline
- ✅ Comprehensive documentation

**Happy testing!** 🚀

---

**Need more help? Check the other documentation files or raise an issue!**
