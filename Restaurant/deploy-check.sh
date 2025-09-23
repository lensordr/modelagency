#!/bin/bash

echo "🔍 Pre-deployment checks..."

# Check Python syntax
echo "Checking Python syntax..."
python -m py_compile main.py
if [ $? -ne 0 ]; then
    echo "❌ DEPLOYMENT BLOCKED: Python syntax errors in main.py"
    exit 1
fi

# Check for required imports
echo "Checking imports..."
python -c "
try:
    from models import Restaurant, User, Table
    from auth import authenticate_user, create_access_token
    from crud import init_sample_data
    print('✅ All imports OK')
except ImportError as e:
    print(f'❌ DEPLOYMENT BLOCKED: Import error - {e}')
    exit(1)
"

# Check file completeness
echo "Checking file integrity..."
if ! tail -1 main.py | grep -q "uvicorn.run"; then
    echo "❌ DEPLOYMENT BLOCKED: main.py appears incomplete"
    exit 1
fi

# Check for common issues
echo "Checking for common issues..."
if grep -q "print(f\"DEBUG:" main.py; then
    echo "⚠️  WARNING: Debug print statements found - consider removing for production"
fi

if grep -q "TODO\|FIXME\|XXX" main.py; then
    echo "⚠️  WARNING: TODO/FIXME comments found"
fi

echo "✅ All checks passed! Safe to deploy."