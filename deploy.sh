#!/bin/bash

echo "🚀 Elite Models Barcelona Deployment Script"
echo "==========================================="

# Check if logged into Heroku
echo "📋 Checking Heroku login status..."
if ! heroku auth:whoami > /dev/null 2>&1; then
    echo "❌ Not logged into Heroku. Please run: heroku login"
    exit 1
fi

echo "✅ Heroku login verified"

# Create Heroku app if it doesn't exist
echo "🏗️ Creating/checking Heroku app..."
heroku create elite-models-barcelona 2>/dev/null || echo "App may already exist"

# Set Heroku remote
echo "🔗 Setting Heroku remote..."
heroku git:remote -a elite-models-barcelona

# Deploy to Heroku
echo "🚀 Deploying to Heroku..."
git push heroku main

echo "✅ Deployment complete!"
echo "🌐 Your app should be available at: https://elite-models-barcelona.herokuapp.com"
echo "🔧 To view logs: heroku logs --tail"