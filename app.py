import os
import logging
from typing import Optional
import asyncio
from io import BytesIO
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import json

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode

# Import local modules
import config  # This will configure logging and load environment
from scraper import WTGScraper
from utils import extract_wtg_links, format_game_message_html, validate_wtg_url
from models import WTGData

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize scraper
scraper = WTGScraper()


class HealthCheckHandler(BaseHTTPRequestHandler):
    """Simple HTTP handler for health checks"""
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"status": "healthy", "service": "wtg-telegram-bot"}
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Suppress default HTTP server logging
        pass


class WTGBot:
    """Main Telegram bot class for WTG link processing"""
    
    def __init__(self, token: str):
        self.token = token
        self.application = Application.builder().token(token).build()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup bot command and message handlers"""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        
        # Message handlers
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = """🎮 <b>WTG Bot</b> - Game Review Parser

Hello! I can parse links from wtg.com.ua and show you game information with comments.

Just send me a WTG comment link like:
<code>https://wtg.com.ua/game/game-name/comment/comment-id</code>

I'll extract:
• Game title and score
• Comment details
• Game image
• Link to original post

Type /help for more information."""
        
        await update.message.reply_text(welcome_message, parse_mode=ParseMode.HTML)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_message = """🔧 <b>How to use WTG Bot:</b>

<b>Supported URLs:</b>
• <code>https://wtg.com.ua/game/*/comment/*</code>

<b>What I extract:</b>
• 🎮 Game title
• ⭐ Game score/rating  
• 👤 Comment author & date
• 💬 Comment text
• 🖼️ Game cover image
• 🔗 Link to original post

<b>Commands:</b>
• /start - Welcome message
• /help - This help message

Just paste a WTG comment link and I'll do the rest!"""
        
        await update.message.reply_text(help_message, parse_mode=ParseMode.HTML)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming messages and check for WTG links"""
        message_text = update.message.text
        
        # Extract WTG links from message
        wtg_links = extract_wtg_links(message_text)
        
        if not wtg_links:
            # No WTG links found, ignore the message
            return
        
        logger.info(f"Processing {len(wtg_links)} WTG links from user {update.effective_user.id}")
        
        # Process each link (limit to 3 to avoid spam)
        for link in wtg_links[:3]:
            await self.process_wtg_link(update, link)
    
    async def process_wtg_link(self, update: Update, url: str):
        """Process a single WTG link and send response"""
        try:
            # Validate URL
            if not validate_wtg_url(url):
                await update.message.reply_text(
                    f"❌ Invalid WTG URL format: {url}\n\n"
                    "Please use format: https://wtg.com.ua/game/*/comment/*"
                )
                return
            
            # Send "processing" message
            processing_msg = await update.message.reply_text(
                "🔄 Processing WTG link...",
                parse_mode=ParseMode.HTML
            )
            
            # Scrape the page
            wtg_data = await self._scrape_wtg_page(url)
            
            if not wtg_data:
                await processing_msg.edit_text(
                    f"❌ Failed to extract data from: {url}\n\n"
                    "The page might be unavailable or the format has changed."
                )
                return
            
            # Format and send the response
            await self._send_game_info(update, wtg_data, processing_msg)
            
        except Exception as e:
            logger.error(f"Error processing WTG link {url}: {e}")
            await update.message.reply_text(
                f"❌ An error occurred while processing: {url}\n\n"
                "Please try again later."
            )
    
    async def _scrape_wtg_page(self, url: str) -> Optional[WTGData]:
        """Scrape WTG page in a separate thread to avoid blocking"""
        loop = asyncio.get_event_loop()
        
        def scrape():
            return scraper.scrape_game_page(url)
        
        try:
            wtg_data = await loop.run_in_executor(None, scrape)
            return wtg_data
        except Exception as e:
            logger.error(f"Error in async scraping: {e}")
            return None
    
    async def _send_game_info(self, update: Update, wtg_data: WTGData, processing_msg):
        """Send formatted game information with image if available"""
        try:
            # Format the message
            message_text = format_game_message_html(wtg_data)
            
            # Log the formatted HTML message
            logger.info(f"Formatted HTML message:\n{message_text}")
            
            # Try to send with image if available
            if wtg_data.game.image_url:
                image_data = await self._download_image(wtg_data.game.image_url)
                
                if image_data:
                    try:
                        # Send photo with caption
                        await update.message.reply_photo(
                            photo=BytesIO(image_data),
                            caption=message_text,
                            parse_mode=ParseMode.HTML
                        )
                        
                        # Delete processing message
                        await processing_msg.delete()
                        return
                        
                    except Exception as e:
                        logger.error(f"Error sending photo: {e}")
            
            # Fallback: send text message only
            await processing_msg.edit_text(
                message_text,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=False
            )
            
        except Exception as e:
            logger.error(f"Error sending game info: {e}")
            await processing_msg.edit_text(
                f"❌ Error formatting response for: {wtg_data.original_url}"
            )
    
    async def _download_image(self, image_url: str) -> Optional[bytes]:
        """Download image asynchronously"""
        loop = asyncio.get_event_loop()
        
        def download():
            return scraper.download_image(image_url)
        
        try:
            image_data = await loop.run_in_executor(None, download)
            return image_data
        except Exception as e:
            logger.error(f"Error downloading image async: {e}")
            return None
    
    def run_webhook(self, webhook_url: str, port: int):
        """Run bot with webhook (for production)"""
        logger.info(f"Starting bot with webhook: {webhook_url}")
        
        # Start health check server on a different port
        health_port = port + 1
        health_server = HTTPServer(("0.0.0.0", health_port), HealthCheckHandler)
        health_thread = threading.Thread(target=health_server.serve_forever, daemon=True)
        health_thread.start()
        logger.info(f"Health check server started on port {health_port}")
        
        self.application.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path="/webhook",
            webhook_url=f"{webhook_url}/webhook"
        )
    
    def run_polling(self, port: int = 10000):
        """Run bot with polling (for development and simple deployments)"""
        logger.info("Starting bot with long polling...")
        logger.info(f"Starting health check server on port {port}")
        logger.info("Press Ctrl+C to stop the bot")
        
        # Start health check server in a separate thread for Render.com compatibility
        health_server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
        health_thread = threading.Thread(target=health_server.serve_forever, daemon=True)
        health_thread.start()
        logger.info(f"Health check server started at http://0.0.0.0:{port}/health")
        
        try:
            # Use simple polling - the Application handles all the configuration internally
            self.application.run_polling(
                drop_pending_updates=True  # Drop updates that came while bot was offline
            )
        except KeyboardInterrupt:
            logger.info("Received interrupt signal, shutting down gracefully...")
            health_server.shutdown()
        except Exception as e:
            logger.error(f"Error in polling mode: {e}")
            health_server.shutdown()
            raise


def main():
    """Main function to run the bot"""
    # Get environment variables
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    webhook_url = os.getenv("WEBHOOK_URL")
    port = int(os.getenv("PORT", 10000))
    
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN environment variable is required")
        return
    
    # Initialize bot
    bot = WTGBot(token)
    
    # Prefer polling mode unless webhook URL is explicitly set
    if webhook_url and webhook_url != "https://your-app.onrender.com":
        logger.info("Webhook URL detected, running in webhook mode")
        bot.run_webhook(webhook_url, port)
    else:
        logger.info("Running in polling mode (recommended for development)")
        logger.info("To use webhook mode, set WEBHOOK_URL environment variable")
        bot.run_polling(port)


if __name__ == "__main__":
    main()
