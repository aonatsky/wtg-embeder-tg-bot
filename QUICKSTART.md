# Quick Start Guide - Polling Mode

## 🚀 Get Your Bot Running in 5 Minutes

### 1. Bot Token Setup
1. Open Telegram and message [@BotFather](https://t.me/botfather)
2. Send `/newbot` and follow the instructions
3. Copy your bot token (looks like: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)

### 2. Configure Bot
```bash
# Edit the token in .env file
nano .env

# Replace 'your_bot_token_here' with your actual token:
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
```

### 3. Run the Bot
```bash
# Install dependencies (if not done already)
make install

# Start the bot
make run
```

You should see:
```
2025-06-27 14:53:05,036 - __main__ - INFO - Running in polling mode (recommended for development)
2025-06-27 14:53:05,036 - __main__ - INFO - To use webhook mode, set WEBHOOK_URL environment variable
2025-06-27 14:53:05,036 - __main__ - INFO - Starting bot with long polling...
2025-06-27 14:53:05,036 - __main__ - INFO - Press Ctrl+C to stop the bot
```

### 4. Test Your Bot
1. Find your bot on Telegram (search for the username you gave it)
2. Send `/start` to your bot
3. Send a WTG link like: `https://wtg.com.ua/game/lost-in-random-the-eternal-die/comment/06672ce6-96ce-471c-aea2-6ec3cd30cde8`
4. Watch the magic happen! 🎮

## 🛠️ Bot Control Commands

```bash
# Run in foreground (good for testing)
make run

# Run in background
make start

# Check status
make status

# View logs
make logs

# Stop bot
make stop

# Run tests
make test
```

## 📱 Testing Links

Try these WTG links to test your bot:

```
https://wtg.com.ua/game/lost-in-random-the-eternal-die/comment/06672ce6-96ce-471c-aea2-6ec3cd30cde8
```

## 🔧 Troubleshooting

**Bot not responding?**
- Check if bot token is correct in `.env`
- Make sure bot is running: `make status`
- Check logs: `make logs`

**"Import telegram could not be resolved"?**
- Run: `make install`

**Permission denied on scripts?**
- Run: `chmod +x bot_control.sh deploy.sh`

## 🚀 Deploy to Production

When ready to deploy to Render.com:
1. Push code to GitHub
2. Create Render web service
3. Set `TELEGRAM_BOT_TOKEN` environment variable
4. Deploy!

The bot will automatically use polling mode - no webhook setup needed!

---

That's it! Your WTG Telegram bot is now ready to parse game links and show awesome game information. 🎮✨
