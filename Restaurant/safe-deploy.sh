#!/bin/bash

echo "🚀 Safe Deployment Script"
echo "========================"

# Run pre-deployment checks
./deploy-check.sh
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ DEPLOYMENT ABORTED: Pre-checks failed!"
    echo "Fix the issues above before deploying."
    exit 1
fi

echo ""
echo "🔄 Proceeding with deployment..."

# Add and commit changes
git add .
git commit -m "${1:-Safe deployment with pre-checks}"

# Deploy to Heroku
git push origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Deployment successful!"
    echo "🌐 App URL: https://tablelink-platform-4b30f385a07d.herokuapp.com/"
else
    echo ""
    echo "❌ Deployment failed!"
    exit 1
fi