# Test Failure Fix Guide: test_admin_login

## Issue

The `test_admin_login` test is failing with a **401 Unauthorized** error, which means the login request is being rejected.

## Root Cause

This typically happens when:

1. The admin user hasn't been seeded in the database yet
2. The API was started before the database was initialized
3. The database file is corrupted or outdated

## Solution Steps

### Step 1: Run the diagnostic script

This script will check if the admin user exists and attempt to seed it if needed:

```powershell
# Windows PowerShell
python backend/../check-admin.py

# Or in WSL/Linux
python3 check-admin.py
```

The script will:

- ✅ Check if the admin user exists
- ✅ Verify the password is correct
- ✅ Seed the admin user if it doesn't exist
- ✅ Test the login locally

### Step 2: Restart the API

If the diagnostic script reports success, restart your API server:

```bash
# Terminal 1 - Stop the existing server (Ctrl+C)
# Then restart:
uvicorn backend.main:app --reload --port 8000
```

When the API starts, it automatically:

1. Creates all database tables (if they don't exist)
2. Seeds the bootstrap admin user (if configured in `.env` and enabled)

### Step 3: Run tests again

```bash
pytest automation/ -v
```

---

## Configuration Check

The admin credentials are read from `.env`:

```env
BOOTSTRAP_ADMIN_ENABLED=true
BOOTSTRAP_ADMIN_USERNAME=admin
BOOTSTRAP_ADMIN_PASSWORD=admin
BOOTSTRAP_ADMIN_EMAIL=admin@qalytics.dev
BOOTSTRAP_ADMIN_ROLE=admin
```

If these are not set or incorrect, the tests will fail. **Do not commit `.env` to git** — it contains secrets.

---

## Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| `401 Unauthorized` | Run diagnostic script, restart API, run tests again |
| `Connection refused` | Make sure API is running on port 8000 |
| `Database locked` | Delete `backend/qalytics.db` and restart API to start fresh |
| Credentials not loading | Check `.env` file exists and is readable |

---

## Manual Reset (if needed)

If you want to start fresh:

```powershell
# 1. Remove old database
Remove-Item backend/qalytics.db

# 2. Restart API (will create fresh DB and seed admin)
uvicorn backend.main:app --reload --port 8000

# 3. In another terminal, run tests
pytest automation/ -v
```

---

## Expected Test Output

After fixing, you should see:

```
automation/smoke/test_sample.py::test_api_health PASSED [ 33%]
automation/smoke/test_sample.py::test_admin_login PASSED [ 66%]
automation/smoke/test_sample.py::test_invalid_login_rejected SKIPPED [100%]

======================== 1 passed, 1 skipped in 0.XX s =========================
```

---

## Still Having Issues?

1. Check the API console for errors when it starts
2. Verify `.env` file has correct credentials
3. Run `check-admin.py` to see detailed diagnostics
4. Look at `backend/routes/auth.py` to understand the login flow
5. Check `backend/database.py` for database initialization code
