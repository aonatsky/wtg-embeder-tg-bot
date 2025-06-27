#!/usr/bin/env python3
"""
Bot Control Script - Easy way to start/stop the WTG Telegram Bot
"""

import os
import sys
import signal
import subprocess
import time
from pathlib import Path

# Project paths
PROJECT_DIR = Path(__file__).parent
VENV_PYTHON = PROJECT_DIR / ".venv" / "bin" / "python"
BOT_SCRIPT = PROJECT_DIR / "app.py"
PID_FILE = PROJECT_DIR / "bot.pid"

def start_bot():
    """Start the bot in the background"""
    if is_bot_running():
        print("❌ Bot is already running!")
        return False
    
    print("🚀 Starting WTG Telegram Bot...")
    
    # Start bot process
    try:
        process = subprocess.Popen(
            [str(VENV_PYTHON), str(BOT_SCRIPT)],
            cwd=PROJECT_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid  # Create new process group
        )
        
        # Save PID
        with open(PID_FILE, 'w') as f:
            f.write(str(process.pid))
        
        # Wait a moment to see if it starts successfully
        time.sleep(2)
        
        if process.poll() is None:
            print("✅ Bot started successfully!")
            print(f"📋 PID: {process.pid}")
            print("📝 Use 'python bot_control.py stop' to stop the bot")
            print("📊 Use 'python bot_control.py status' to check status")
            return True
        else:
            stdout, stderr = process.communicate()
            print("❌ Bot failed to start!")
            print(f"Error: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        return False

def stop_bot():
    """Stop the bot"""
    if not is_bot_running():
        print("❌ Bot is not running!")
        return False
    
    try:
        pid = get_bot_pid()
        if pid:
            print(f"🛑 Stopping bot (PID: {pid})...")
            os.killpg(os.getpgid(pid), signal.SIGTERM)
            
            # Wait for process to stop
            for _ in range(10):
                if not is_process_running(pid):
                    break
                time.sleep(0.5)
            
            # Force kill if still running
            if is_process_running(pid):
                print("⚠️  Force killing bot...")
                os.killpg(os.getpgid(pid), signal.SIGKILL)
            
            # Clean up PID file
            if PID_FILE.exists():
                PID_FILE.unlink()
            
            print("✅ Bot stopped successfully!")
            return True
        
    except Exception as e:
        print(f"❌ Error stopping bot: {e}")
        return False

def status_bot():
    """Check bot status"""
    if is_bot_running():
        pid = get_bot_pid()
        print(f"✅ Bot is running (PID: {pid})")
        
        # Try to get some process info
        try:
            import psutil
            process = psutil.Process(pid)
            print(f"📊 CPU: {process.cpu_percent():.1f}%")
            print(f"💾 Memory: {process.memory_info().rss / 1024 / 1024:.1f} MB")
            print(f"⏱️  Started: {process.create_time()}")
        except ImportError:
            print("📊 Install psutil for detailed process info")
        except Exception:
            pass
            
        return True
    else:
        print("❌ Bot is not running")
        return False

def is_bot_running():
    """Check if bot is currently running"""
    pid = get_bot_pid()
    return pid and is_process_running(pid)

def get_bot_pid():
    """Get bot PID from file"""
    try:
        if PID_FILE.exists():
            with open(PID_FILE, 'r') as f:
                return int(f.read().strip())
    except:
        pass
    return None

def is_process_running(pid):
    """Check if process with given PID is running"""
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False

def logs_bot():
    """Show recent bot logs"""
    log_file = PROJECT_DIR / "bot.log"
    if log_file.exists():
        print("📝 Recent bot logs:")
        print("-" * 50)
        try:
            # Show last 20 lines
            with open(log_file, 'r') as f:
                lines = f.readlines()
                for line in lines[-20:]:
                    print(line.rstrip())
        except Exception as e:
            print(f"Error reading logs: {e}")
    else:
        print("📝 No log file found")

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("🤖 WTG Telegram Bot Control")
        print("=" * 30)
        print("Usage:")
        print("  python bot_control.py start   - Start the bot")
        print("  python bot_control.py stop    - Stop the bot")
        print("  python bot_control.py status  - Check status")
        print("  python bot_control.py restart - Restart the bot")
        print("  python bot_control.py logs    - Show recent logs")
        return
    
    command = sys.argv[1].lower()
    
    if command == "start":
        start_bot()
    elif command == "stop":
        stop_bot()
    elif command == "status":
        status_bot()
    elif command == "restart":
        print("🔄 Restarting bot...")
        stop_bot()
        time.sleep(1)
        start_bot()
    elif command == "logs":
        logs_bot()
    else:
        print(f"❌ Unknown command: {command}")
        print("Use: start, stop, status, restart, or logs")

if __name__ == "__main__":
    main()
