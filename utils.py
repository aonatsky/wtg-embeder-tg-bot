import re
import logging
from typing import Optional, List

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def extract_wtg_links(text: str) -> List[str]:
    """
    Extract WTG.com.ua comment links from text message.
    
    Args:
        text: Message text to search for links
        
    Returns:
        List of valid WTG comment URLs
    """
    # Pattern to match WTG comment URLs
    pattern = r'https://wtg\.com\.ua/game/[^/]+/comment/[a-f0-9\-]+'
    links = re.findall(pattern, text, re.IGNORECASE)
    
    logger.info(f"Found {len(links)} WTG links in message")
    return links


def sanitize_text(text: str) -> str:
    """
    Sanitize text content for safe display in Telegram MarkdownV2.
    
    Args:
        text: Raw text to sanitize
        
    Returns:
        Sanitized text safe for Telegram MarkdownV2
    """
    if not text:
        return ""
    
    # Remove excessive whitespace and normalize
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Escape special MarkdownV2 characters
    # These characters must be escaped: _*[]()~`>#+-=|{}.!
    special_chars = [
        '\\', '_', '*', '[', ']', '(', ')', '~', '`', 
        '>', '#', '+', '-', '=', '|', '{', '}', '.', '!'
    ]
    
    # Escape backslashes first to avoid double escaping
    text = text.replace('\\', '\\\\')
    
    # Then escape other special characters
    for char in special_chars[1:]:  # Skip backslash as it's already handled
        text = text.replace(char, f'\\{char}')
    
    return text


def sanitize_html(text: str) -> str:
    """
    Sanitize text for HTML formatting (more reliable than MarkdownV2).
    
    Args:
        text: Raw text to sanitize
        
    Returns:
        HTML-safe text
    """
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Escape HTML special characters
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    
    return text


def format_game_message(wtg_data) -> str:
    """
    Format game and comment data into a nice Telegram message.
    
    Args:
        wtg_data: WTGData object with game and comment info
        
    Returns:
        Formatted message string
    """
    game = wtg_data.game
    comment = wtg_data.comment
    
    # Sanitize text fields
    title = sanitize_text(game.title)
    score = sanitize_text(game.score)
    author = sanitize_text(comment.author)
    date = sanitize_text(comment.date)
    comment_text = sanitize_text(comment.text)
    
    # Truncate comment if too long
    if len(comment_text) > 300:
        comment_text = comment_text[:297] + "\\.\\.\\."
    
    message = f"""🎮 *{title}*
⭐ Score: {score}/100
👤 Comment by: {author} \\- {date}

💬 {comment_text}

🔗 [View original post]({wtg_data.original_url})"""

    return message


def format_game_message_html(wtg_data) -> str:
    """
    Format game and comment data using HTML (more reliable than MarkdownV2).
    
    Args:
        wtg_data: WTGData object with game and comment info
        
    Returns:
        HTML formatted message string
    """
    game = wtg_data.game
    comment = wtg_data.comment
    
    # Log the raw data
    logger.info(f"Formatting data - Game: {game.title}, Score: {game.score}, Author: {comment.author}")
    
    # Sanitize text fields for HTML
    title = sanitize_html(game.title)
    score = sanitize_html(game.score)
    author = sanitize_html(comment.author)
    date = sanitize_html(comment.date)
    comment_text = sanitize_html(comment.text)
    
    # Log sanitized data
    logger.info(f"Sanitized data - Title: '{title}', Score: '{score}', Author: '{author}'")
    
    # Truncate comment if too long
    if len(comment_text) > 1000:
        comment_text = comment_text[:297] + "..."
    
    message = f"""🎮 <b>{title}</b>
⭐ Score: {score}/100
👤 Comment by: {author} - {date}

💬 {comment_text}

🔗 <a href="{wtg_data.original_url}">View original post</a>"""

    return message


def validate_wtg_url(url: str) -> bool:
    """
    Validate if URL is a proper WTG comment URL.
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid WTG comment URL, False otherwise
    """
    pattern = r'^https://wtg\.com\.ua/game/[^/]+/comment/[a-f0-9\-]+$'
    return bool(re.match(pattern, url, re.IGNORECASE))


def truncate_text(text: str, max_length: int = 500) -> str:
    """
    Truncate text to maximum length with ellipsis.
    
    Args:
        text: Text to truncate
        max_length: Maximum length allowed
        
    Returns:
        Truncated text with ellipsis if needed
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."
