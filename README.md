# WTG Telegram Bot

A Telegram bot that parses links from wtg.com.ua and displays game information including image, score, and comments.

## Features

- 🎮 Extracts game title and score
- 👤 Shows comment author and date
- 💬 Displays comment text
- 🖼️ Includes game cover image
- 🔗 Provides link to original post
- ⚡ Fast response with async processing
- 🛡️ Error handling and validation

## Supported URL Format

```
https://wtg.com.ua/game/*/comment/*
```

Example:
```
https://wtg.com.ua/game/lost-in-random-the-eternal-die/comment/06672ce6-96ce-471c-aea2-6ec3cd30cde8
```

## Setup

### 1. Local Development

1. Clone the repository:
```bash
git clone <repository-url>
cd wtg-embeder-tg-bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create environment file:
```bash
cp .env.example .env
```

4. Get a Telegram bot token:
   - Message @BotFather on Telegram
   - Create a new bot with `/newbot`
   - Copy the token to your `.env` file

5. Run the bot locally:
```bash
python app.py
```

### 2. Production Deployment on Render.com

**Option A: Polling Mode (Recommended - Simpler Setup)**

1. Fork this repository to your GitHub account

2. Create a new web service on Render.com:
   - Connect your GitHub repository
   - Choose the "Web Service" option
   - Set the following:
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `python app.py`

3. Add environment variables in Render dashboard:
   - `TELEGRAM_BOT_TOKEN`: Your bot token from BotFather
   - `PORT`: `10000`

4. Deploy the service - that's it! The bot will use polling mode automatically.

**Option B: Webhook Mode (Advanced)**

Follow Option A, then additionally:

3. Add webhook environment variable:
   - `WEBHOOK_URL`: Your Render app URL (e.g., `https://your-app.onrender.com`)

4. Set up webhook with Telegram:
```bash
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
     -d "url=https://your-app.onrender.com/webhook"
```

## Project Structure

```
wtg-embeder-tg-bot/
├── app.py                 # Main bot application
├── scraper.py            # WTG scraping logic
├── models.py             # Data models (GameInfo, Comment)
├── utils.py              # Helper functions
├── requirements.txt      # Dependencies
├── Dockerfile           # Container configuration
├── render.yaml          # Render deployment config
├── .env.example         # Environment template
└── README.md            # This file
```

## Usage

1. Start a chat with your bot on Telegram
2. Send `/start` to see the welcome message
3. Send any message containing a WTG comment URL
4. The bot will automatically detect and process the link
5. Receive formatted game information with image

## Example Output

```
🎮 Lost in Random: The Eternal Die
⭐ Score: 79/100
👤 Comment by: username - 15.06.2024

💬 This is an amazing game with great graphics and storyline. 
The dice mechanics are really innovative and fun to play with.

🔗 View original post

[Game Cover Image]
```

## Bot Commands

- `/start` - Welcome message and instructions
- `/help` - Help and usage information

## Error Handling

The bot gracefully handles:
- Invalid URLs
- Network timeouts
- Missing page elements
- Image download failures
- Telegram API errors

## Development

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/
```

### Local Development with Polling
The bot runs in polling mode by default. To switch to webhook mode, set `WEBHOOK_URL` in your `.env` file.

**Polling Mode (Default):**
- Easier setup and debugging
- Works behind firewalls and NAT
- Bot actively requests updates from Telegram
- Recommended for development and simple deployments

**Webhook Mode:**
- More efficient for high-traffic bots
- Requires public HTTPS endpoint
- Telegram pushes updates to your server
- Recommended for production with high load

### Docker Development
```bash
# Build image
docker build -t wtg-bot .

# Run container
docker run --env-file .env -p 10000:10000 wtg-bot
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Security

- Bot token should be kept secure
- All URLs are validated before scraping
- Text content is sanitized for Telegram
- Rate limiting is implemented for scraping

## Troubleshooting

### Common Issues

1. **Bot not responding**: Check if token is correct and webhook is set up properly
2. **Image not loading**: WTG might have changed their image structure
3. **Scraping fails**: Website structure might have changed, check scraper.py
4. **Render deployment fails**: Check logs in Render dashboard

### Checking Bot Status
```bash
# Check if webhook is set
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo"

# Remove webhook (for local development)
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/deleteWebhook"
```

## Support

If you encounter any issues, please create an issue in the GitHub repository with:
- Error message
- Steps to reproduce
- Environment details (local/Render)
- Example URL that failed
