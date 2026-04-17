#!/usr/bin/env pwsh
<#
.SYNOPSIS
  QAlytics Project Environment Setup Script
  
.DESCRIPTION
  Sets up a fresh Python virtual environment and installs dependencies.
  This script recreates the .venv directory and installs all required packages.
  
.EXAMPLE
  .\setup-env.ps1
#>

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║    QAlytics Environment Setup                             ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check if Python is available
Write-Host "1️⃣  Checking Python installation..." -ForegroundColor Yellow
$python = & where python.exe 2>$null
if (-not $python) {
    Write-Host "   ❌ Python not found. Please install Python 3.9+." -ForegroundColor Red
    exit 1
}
$pythonVersion = & python --version 2>&1
Write-Host "   ✓ $pythonVersion" -ForegroundColor Green
Write-Host ""

# Step 2: Remove old venv if it exists
Write-Host "2️⃣  Cleaning old virtual environment..." -ForegroundColor Yellow
if (Test-Path .\.venv) {
    Write-Host "   Removing existing .venv..." -ForegroundColor Cyan
    Remove-Item -Recurse -Force .\.venv
    Start-Sleep -Milliseconds 500
}
Write-Host "   ✓ Ready to create new environment" -ForegroundColor Green
Write-Host ""

# Step 3: Create new virtual environment
Write-Host "3️⃣  Creating new virtual environment..." -ForegroundColor Yellow
& python -m venv .venv
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✓ Virtual environment created" -ForegroundColor Green
}
else {
    Write-Host "   ❌ Failed to create virtual environment" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 4: Activate virtual environment and upgrade pip
Write-Host "4️⃣  Activating environment and upgrading pip..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1
& python -m pip install --upgrade pip setuptools wheel -q
Write-Host "   ✓ Pip upgraded" -ForegroundColor Green
Write-Host ""

# Step 5: Install dependencies
Write-Host "5️⃣  Installing dependencies from requirements.txt..." -ForegroundColor Yellow
if (Test-Path .\backend\requirements.txt) {
    & pip install -r backend/requirements.txt -q
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✓ Dependencies installed successfully" -ForegroundColor Green
    }
    else {
        Write-Host "   ⚠️  Some dependencies may have failed to install" -ForegroundColor Yellow
    }
}
else {
    Write-Host "   ⚠️  requirements.txt not found" -ForegroundColor Yellow
}
Write-Host ""

# Step 6: Verify installation
Write-Host "6️⃣  Verifying installation..." -ForegroundColor Yellow
$packages = @("fastapi", "uvicorn", "sqlalchemy", "pytest", "pytest-asyncio")
$allOk = $true
foreach ($pkg in $packages) {
    $check = & python -c "import $($pkg.Replace('-','_'))" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✓ $pkg" -ForegroundColor Green
    }
    else {
        Write-Host "   ⚠️  $pkg - not found" -ForegroundColor Yellow
        $allOk = $false
    }
}
Write-Host ""

if ($allOk) {
    Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║ ✅  Environment setup complete!                           ║" -ForegroundColor Green
    Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Start FastAPI: uvicorn backend.main:app --reload" -ForegroundColor Gray
    Write-Host "  2. Run tests:     pytest automation/ -v" -ForegroundColor Gray
    Write-Host "  3. Serve frontend: python -m http.server 3000 --directory frontend" -ForegroundColor Gray
}
else {
    Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Yellow
    Write-Host "║ ⚠️  Environment setup with warnings                        ║" -ForegroundColor Yellow
    Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Some packages are missing. Try:" -ForegroundColor Cyan
    Write-Host "  pip install -r backend/requirements.txt" -ForegroundColor Gray
}
