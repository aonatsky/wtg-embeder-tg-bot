#!/bin/bash

# GitHub Setup Script for WTG Telegram Bot
# Run this after creating the repository on GitHub

echo "🚀 Setting up GitHub repository..."

# Check if repository URL is provided
if [ -z "$1" ]; then
    echo "❌ Please provide your GitHub repository URL"
    echo "Usage: ./github_setup.sh https://github.com/YOUR_USERNAME/wtg-embeder-tg-bot.git"
    echo ""
    echo "Steps to create repository:"
    echo "1. Go to https://github.com"
    echo "2. Click '+' → 'New repository'"
    echo "3. Name: wtg-embeder-tg-bot"
    echo "4. Description: Telegram bot for parsing WTG.com.ua game comment links"
    echo "5. Public/Private (your choice)"
    echo "6. Don't initialize with README, .gitignore, or license"
    echo "7. Click 'Create repository'"
    echo "8. Copy the repository URL and run:"
    echo "   ./github_setup.sh <repository-url>"
    exit 1
fi

REPO_URL=$1

echo "📁 Adding remote origin: $REPO_URL"
git remote add origin "$REPO_URL"

echo "📤 Pushing to GitHub..."
git push -u origin main

echo "✅ Repository successfully pushed to GitHub!"
echo "🔗 Repository URL: $REPO_URL"
echo ""
echo "Next steps:"
echo "1. Update .env with your bot token"
echo "2. Deploy to Render.com using the provided instructions"
echo "3. Test the bot with WTG links"
