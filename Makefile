# WTG Telegram Bot Makefile

.PHONY: help install test run clean docker-build docker-run deploy

# Default target
help:
	@echo "WTG Telegram Bot - Available Commands:"
	@echo "======================================"
	@echo "make install    - Install dependencies"
	@echo "make test       - Run tests"
	@echo "make run        - Run bot locally (polling mode)"
	@echo "make start      - Start bot in background"
	@echo "make stop       - Stop background bot"
	@echo "make status     - Check bot status"
	@echo "make logs       - Show bot logs"
	@echo "make clean      - Clean cache files"
	@echo "make docker-build - Build Docker image"
	@echo "make docker-run - Run in Docker container"
	@echo "make deploy     - Deploy bot (auto-detects mode)"

# Install dependencies
install:
	pip install -r requirements.txt

# Run tests
test:
	python test_bot.py

# Run bot locally
run:
	@echo "🚀 Starting bot in polling mode..."
	python app.py

# Bot control commands
start:
	./bot_control.sh start

stop:
	./bot_control.sh stop

status:
	./bot_control.sh status

logs:
	./bot_control.sh logs

# Clean cache files
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -f *.log

# Docker commands
docker-build:
	docker build -t wtg-telegram-bot .

docker-run:
	docker run --env-file .env -p 10000:10000 wtg-telegram-bot

# Deployment
deploy:
	./deploy.sh

# Set webhook (requires TELEGRAM_BOT_TOKEN and WEBHOOK_URL in .env)
webhook:
	@if [ -f .env ]; then \
		source .env && \
		curl -X POST "https://api.telegram.org/bot$$TELEGRAM_BOT_TOKEN/setWebhook" \
		     -d "url=$$WEBHOOK_URL/webhook" | python -m json.tool; \
	else \
		echo "❌ .env file not found"; \
	fi

# Check bot status
status:
	@if [ -f .env ]; then \
		source .env && \
		curl "https://api.telegram.org/bot$$TELEGRAM_BOT_TOKEN/getMe" | python -m json.tool; \
	else \
		echo "❌ .env file not found"; \
	fi

# Development setup
setup: install
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "📝 Created .env file from template"; \
		echo "⚠️  Please edit .env with your bot token"; \
	fi
