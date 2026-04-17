#!/bin/bash
# Quick test verification script
# Run this after starting the API to verify all tests pass

cd /mnt/d/Shreya/qalytics-project

echo "================================"
echo "QAlytics Test Suite - Full Run"
echo "================================"
echo ""
echo "Make sure the API is running:"
echo "  uvicorn backend.main:app --reload --port 8000"
echo ""
echo "Running tests..."
echo ""

pytest automation/ -v --tb=short

echo ""
echo "================================"
echo "Test Summary"
echo "================================"
pytest automation/ -v --tb=line | tail -5
