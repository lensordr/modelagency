#!/bin/bash
# Restaurant Environment Activation Script

echo "🍽️  Activating Restaurant Environment..."
source restaurant_env/bin/activate
cd venv/Restaurant

echo "✅ Environment activated!"
echo "📁 Current directory: $(pwd)"
echo "🐍 Python version: $(python --version)"
echo ""
echo "Available commands:"
echo "  python main.py          - Start the main application"
echo "  python setup.py         - Run setup"
echo "  python quick_test.py    - Run quick tests"
echo ""
echo "To deactivate: type 'deactivate'"