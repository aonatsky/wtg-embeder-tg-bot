#!/bin/bash

# WTG Telegram Bot Deployment Script

set -e

echo "🚀 WTG Telegram Bot Deployment"
echo "================================"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from template..."
    cp .env.example .env
    echo "📝 Please edit .env file with your bot token before running."
    exit 1
fi

# Source environment variables
source .env

# Check if bot token is set
if [ -z "$TELEGRAM_BOT_TOKEN" ] || [ "$TELEGRAM_BOT_TOKEN" = "your_bot_token_here" ]; then
    echo "❌ Please set TELEGRAM_BOT_TOKEN in .env file"
    exit 1
fi

echo "✅ Environment configuration looks good"

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run tests
echo "🧪 Running tests..."
python test_bot.py

if [ $? -eq 0 ]; then
    echo "✅ Tests passed!"
else
    echo "⚠️  Tests completed with warnings"
fi

# Check if webhook URL is set (production mode)
if [ ! -z "$WEBHOOK_URL" ] && [ "$WEBHOOK_URL" != "https://your-app.onrender.com" ]; then
    echo "🌐 Production mode detected"
    echo "🔧 Setting up webhook..."
    
    # Set webhook
    curl -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/setWebhook" \
         -d "url=$WEBHOOK_URL/webhook" \
         -s | python -m json.tool
    
    echo "🚀 Starting bot in webhook mode..."
    python app.py
else
    echo "🏠 Development mode detected"
    echo "🚀 Starting bot in polling mode..."
    python app.py
fi
