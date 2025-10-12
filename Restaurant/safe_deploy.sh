#!/bin/bash

echo "🚀 Starting safe Heroku deployment..."

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: main.py not found. Please run from Restaurant directory."
    exit 1
fi

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    echo "❌ Error: Heroku CLI not installed"
    exit 1
fi

# Get current git status
echo "📋 Checking git status..."
git status

# Add all changes
echo "📦 Adding changes to git..."
git add .

# Commit changes
echo "💾 Committing changes..."
git commit -m "Add hotel support and improved UX - $(date)"

# Push to Heroku (safe deployment)
echo "🚀 Deploying to Heroku..."
git push heroku main

echo "✅ Deployment complete!"
echo "🌐 Check your app at: https://your-app-name.herokuapp.com"