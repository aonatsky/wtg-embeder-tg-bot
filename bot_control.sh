#!/bin/bash

# WTG Bot Control Script

BOT_DIR="/Users/onatskyi/Projects/wtg-embeder-tg-bot"
PYTHON_PATH="$BOT_DIR/.venv/bin/python"
PID_FILE="$BOT_DIR/bot.pid"

case "$1" in
    start)
        echo "🚀 Starting WTG Telegram Bot..."
        cd "$BOT_DIR"
        
        # Check if bot is already running
        if [ -f "$PID_FILE" ] && kill -0 "$(cat $PID_FILE)" 2>/dev/null; then
            echo "❌ Bot is already running (PID: $(cat $PID_FILE))"
            exit 1
        fi
        
        # Start bot in background
        nohup "$PYTHON_PATH" app.py > bot.log 2>&1 &
        echo $! > "$PID_FILE"
        
        sleep 2
        
        # Check if bot started successfully
        if kill -0 "$(cat $PID_FILE)" 2>/dev/null; then
            echo "✅ Bot started successfully (PID: $(cat $PID_FILE))"
            echo "📝 Logs: tail -f $BOT_DIR/bot.log"
        else
            echo "❌ Failed to start bot"
            rm -f "$PID_FILE"
            exit 1
        fi
        ;;
        
    stop)
        echo "🛑 Stopping WTG Telegram Bot..."
        
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            if kill -0 "$PID" 2>/dev/null; then
                kill "$PID"
                echo "✅ Bot stopped (PID: $PID)"
            else
                echo "⚠️  Bot was not running"
            fi
            rm -f "$PID_FILE"
        else
            echo "⚠️  No PID file found, bot may not be running"
        fi
        ;;
        
    restart)
        $0 stop
        sleep 2
        $0 start
        ;;
        
    status)
        if [ -f "$PID_FILE" ] && kill -0 "$(cat $PID_FILE)" 2>/dev/null; then
            echo "✅ Bot is running (PID: $(cat $PID_FILE))"
            echo "📊 Memory usage: $(ps -o rss= -p $(cat $PID_FILE) | awk '{print $1/1024 " MB"}')"
        else
            echo "❌ Bot is not running"
            [ -f "$PID_FILE" ] && rm -f "$PID_FILE"
        fi
        ;;
        
    logs)
        echo "📝 Bot logs (press Ctrl+C to exit):"
        tail -f "$BOT_DIR/bot.log"
        ;;
        
    test)
        echo "🧪 Testing bot configuration..."
        cd "$BOT_DIR"
        "$PYTHON_PATH" test_bot.py
        ;;
        
    *)
        echo "WTG Telegram Bot Control Script"
        echo "Usage: $0 {start|stop|restart|status|logs|test}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the bot in background"
        echo "  stop    - Stop the bot"
        echo "  restart - Restart the bot"
        echo "  status  - Check bot status"
        echo "  logs    - Show live bot logs"
        echo "  test    - Run bot tests"
        exit 1
        ;;
esac
