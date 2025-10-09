#!/bin/bash

echo "🚀 Starting Safe Deployment..."

# 1. Backup current database
echo "📦 Creating database backup..."
cp Restaurant/database.db Restaurant/database_backup_$(date +%Y%m%d_%H%M%S).db
echo "✅ Database backed up"

# 2. Test local changes
echo "🧪 Testing local changes..."
cd Restaurant
python -c "
import sys
try:
    from main import app
    from models import create_tables, get_db
    from crud import init_sample_data
    
    # Test database connection
    create_tables()
    db = next(get_db())
    db.close()
    print('✅ Database connection OK')
    
    # Test imports
    from analytics_service import get_analytics_for_period
    print('✅ Analytics service OK')
    
    print('✅ All tests passed')
except Exception as e:
    print(f'❌ Test failed: {e}')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Local tests failed. Deployment aborted."
    exit 1
fi

echo "✅ Local tests passed"

# 3. Deploy to production (assuming Heroku)
echo "🌐 Deploying to production..."

# Add all changes
git add .

# Commit changes
git commit -m "Deploy: Split bill upgrade flow, menu fixes, CSV export improvements, 15-day trial"

# Push to production
git push heroku main

if [ $? -eq 0 ]; then
    echo "✅ Deployment successful!"
    echo ""
    echo "🎉 Changes deployed:"
    echo "   • Split bill upgrade flow (same as analytics)"
    echo "   • Menu items stay visible when inactive"
    echo "   • CSV export with proper Order IDs"
    echo "   • 15-day trial period"
    echo "   • Professional plan features updated"
    echo ""
    echo "🔗 Check your live site to verify changes"
else
    echo "❌ Deployment failed!"
    echo "💡 Database backup available at: Restaurant/database_backup_*.db"
    exit 1
fi