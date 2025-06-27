import requests
import logging
from bs4 import BeautifulSoup
from typing import Optional
from urllib.parse import urljoin, urlparse
import time
import random
import json
import re

from models import GameInfo, CommentInfo, WTGData

# Configure logging
logger = logging.getLogger(__name__)

# Request headers to mimic a real browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}


class WTGScraper:
    """WTG.com.ua scraper for extracting game and comment information"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
    
    def scrape_game_page(self, url: str) -> Optional[WTGData]:
        """
        Main scraping function to extract game and comment data.
        Uses a two-step process:
        1. Extract game_slug from the HTML page
        2. Use API to get comment data
        
        Args:
            url: WTG comment URL to scrape
            
        Returns:
            WTGData object with extracted information or None if failed
        """
        try:
            logger.info(f"Scraping WTG page: {url}")
            
            # Extract comment ID and game slug from URL
            comment_id = url.split('/comment/')[-1]
            game_slug = url.split('/game/')[-1].split('/comment/')[0]
            
            logger.info(f"Comment ID: {comment_id}")
            logger.info(f"Game slug: {game_slug}")
            
            # Add random delay to avoid being blocked
            time.sleep(random.uniform(1, 3))
            
            # Get the HTML page for game information
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract game information from HTML
            game_info = self._extract_game_info(soup, url)
            if not game_info:
                logger.error("Failed to extract game information")
                return None
            
            # Use API to get comment information with game slug
            comment_info = self._get_comment_from_api(comment_id, game_slug)
            if not comment_info:
                logger.warning("API comment extraction failed, using HTML fallback")
                # Fallback to HTML parsing
                comment_info = self._extract_comment_info_fallback(soup, comment_id)
            
            if not comment_info:
                logger.error("Failed to extract comment information")
                return None
            
            return WTGData(
                game=game_info,
                comment=comment_info,
                original_url=url
            )
            
        except requests.RequestException as e:
            logger.error(f"Network error while scraping {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error while scraping {url}: {e}")
            return None
    
    def _extract_game_slug(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Extract game_slug from the __NEXT_DATA__ script tag.
        
        Args:
            soup: BeautifulSoup object of the page
            
        Returns:
            game_slug string or None if not found
        """
        try:
            # Find the __NEXT_DATA__ script tag
            script_tag = soup.find('script', {'id': '__NEXT_DATA__'})
            if not script_tag:
                logger.error("__NEXT_DATA__ script tag not found")
                return None
            
            # Parse the JSON data
            next_data = json.loads(script_tag.string)
            
            # Navigate through the data structure to find game_slug
            # The structure seems to be: props.pageProps.initialState.api.queries
            queries = next_data.get('props', {}).get('pageProps', {}).get('initialState', {}).get('api', {}).get('queries', {})
            
            # Look for the getGameDataBySlug query
            for query_key, query_data in queries.items():
                if query_key.startswith('getGameDataBySlug'):
                    game_data = query_data.get('data', {})
                    game_slug = game_data.get('game_slug')
                    if game_slug:
                        return str(game_slug)
            
            # Alternative: try to find game_slug in any data structure
            def find_game_slug(obj):
                if isinstance(obj, dict):
                    if 'game_slug' in obj:
                        return obj['game_slug']
                    for value in obj.values():
                        result = find_game_slug(value)
                        if result:
                            return result
                elif isinstance(obj, list):
                    for item in obj:
                        result = find_game_slug(item)
                        if result:
                            return result
                return None
            
            game_slug = find_game_slug(next_data)
            if game_slug:
                return str(game_slug)
            
            logger.error("game_slug not found in __NEXT_DATA__")
            return None
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing __NEXT_DATA__ JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"Error extracting game_slug: {e}")
            return None
    
    def _extract_game_slug_from_html(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Extract game_slug from the HTML page's JSON data.
        
        Args:
            soup: BeautifulSoup object of the page
            
        Returns:
            Game ID string or None if not found
        """
        try:
            # Look for the __NEXT_DATA__ script tag that contains the game data
            script_tag = soup.find('script', {'id': '__NEXT_DATA__', 'type': 'application/json'})
            
            if not script_tag:
                logger.warning("Could not find __NEXT_DATA__ script tag")
                return None
            
            import json
            data = json.loads(script_tag.string)
            
            # Navigate through the JSON structure to find game_slug
            try:
                # The structure seems to be: props.pageProps.initialState.api.queries
                queries = data['props']['pageProps']['initialState']['api']['queries']
                
                # Look for getGameDataBySlug query
                for query_key, query_data in queries.items():
                    if query_key.startswith('getGameDataBySlug('):
                        game_data = query_data.get('data', {})
                        game_slug = game_data.get('game_slug')
                        if game_slug:
                            logger.info(f"Extracted game_slug: {game_slug}")
                            return str(game_slug)
                
                logger.warning("Could not find game_slug in query data")
                return None
                
            except (KeyError, TypeError) as e:
                logger.error(f"Error navigating JSON structure: {e}")
                return None
                
        except Exception as e:
            logger.error(f"Error extracting game_slug from HTML: {e}")
            return None
    
    def _extract_game_info(self, soup: BeautifulSoup, url: str) -> Optional[GameInfo]:
        """
        Extract game information from the page.
        
        Args:
            soup: BeautifulSoup object of the page
            url: Original URL for context
            
        Returns:
            GameInfo object or None if extraction failed
        """
        try:
            # Try to find game title - look for various possible selectors
            title_selectors = [
                'h1.game-title',
                'h1',
                '.game-header h1',
                '.title',
                '[data-testid="game-title"]'
            ]
            
            title = None
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    break
            
            if not title:
                # Fallback: extract from URL
                title = url.split('/game/')[-1].split('/comment/')[0].replace('-', ' ').title()
            
            # Try to find score - look for rating/score elements
            score_selectors = [
                '.score',
                '.rating',
                '.game-score',
                '[class*="score"]',
                '[class*="rating"]'
            ]
            
            score = "N/A"
            for selector in score_selectors:
                score_elem = soup.select_one(selector)
                if score_elem:
                    score_text = score_elem.get_text(strip=True)
                    # Extract numeric score
                    import re
                    score_match = re.search(r'\d+', score_text)
                    if score_match:
                        score = score_match.group()
                        break
            
            # Try to find game image
            image_selectors = [
                '.game-image img',
                '.poster img',
                '.cover img',
                'img[alt*="game"]',
                'img[src*="game"]',
                '.game-header img'
            ]
            
            image_url = None
            for selector in image_selectors:
                img_elem = soup.select_one(selector)
                if img_elem:
                    src = img_elem.get('src') or img_elem.get('data-src')
                    if src:
                        image_url = urljoin(url, src)
                        break
            
            # If no specific game image found, try any large image
            if not image_url:
                all_images = soup.find_all('img')
                for img in all_images:
                    src = img.get('src') or img.get('data-src')
                    if src and any(keyword in src.lower() for keyword in ['game', 'cover', 'poster']):
                        image_url = urljoin(url, src)
                        break
            
            logger.info(f"Extracted game info - Title: {title}, Score: {score}, Image: {bool(image_url)}")
            logger.debug(f"Game details - Title: '{title}', Score: '{score}', Image URL: '{image_url}'")
            
            return GameInfo(
                title=title,
                score=score,
                image_url=image_url or ""
            )
            
        except Exception as e:
            logger.error(f"Error extracting game info: {e}")
            return None
    
    def _extract_comment_info_fallback(self, soup: BeautifulSoup, comment_id: str) -> Optional[CommentInfo]:
        """
        Extract comment information from the page (fallback method).
        
        Args:
            soup: BeautifulSoup object of the page
            comment_id: Comment ID extracted from URL
            
        Returns:
            CommentInfo object or None if extraction failed
        """
        try:
            # Try to find the specific comment by ID or find comment elements
            comment_selectors = [
                f'[id="{comment_id}"]',
                f'[data-id="{comment_id}"]',
                '.comment',
                '.user-comment',
                '[class*="comment"]'
            ]
            
            comment_elem = None
            for selector in comment_selectors:
                comment_elem = soup.select_one(selector)
                if comment_elem:
                    break
            
            # If specific comment not found, try to find comment section
            if not comment_elem:
                comment_sections = soup.find_all(['div', 'article', 'section'], class_=lambda x: x and 'comment' in x.lower())
                if comment_sections:
                    comment_elem = comment_sections[0]
            
            if not comment_elem:
                logger.warning("Could not find comment element, using fallback")
                return CommentInfo(
                    author="Unknown User",
                    date="Unknown Date",
                    text="Comment content not available",
                    comment_id=comment_id
                )
            
            # Extract author
            author_selectors = [
                '.author',
                '.username',
                '.user-name',
                '.comment-author',
                '[class*="author"]',
                '[class*="user"]'
            ]
            
            author = "Unknown User"
            for selector in author_selectors:
                author_elem = comment_elem.select_one(selector)
                if author_elem:
                    author = author_elem.get_text(strip=True)
                    break
            
            # Extract date
            date_selectors = [
                '.date',
                '.timestamp',
                '.comment-date',
                'time',
                '[datetime]',
                '[class*="date"]',
                '[class*="time"]'
            ]
            
            date = "Unknown Date"
            for selector in date_selectors:
                date_elem = comment_elem.select_one(selector)
                if date_elem:
                    date = date_elem.get_text(strip=True)
                    # If element has datetime attribute, prefer that
                    if date_elem.get('datetime'):
                        date = date_elem.get('datetime')
                    break
            
            # Extract comment text
            text_selectors = [
                '.comment-text',
                '.comment-body',
                '.text',
                '.content',
                'p'
            ]
            
            comment_text = "Comment text not available"
            for selector in text_selectors:
                text_elem = comment_elem.select_one(selector)
                if text_elem:
                    comment_text = text_elem.get_text(strip=True)
                    if len(comment_text) > 10:  # Ensure we got substantial text
                        break
            
            # If no specific text found, get all text from comment element
            if comment_text == "Comment text not available":
                all_text = comment_elem.get_text(strip=True)
                if len(all_text) > 10:
                    comment_text = all_text[:500]  # Limit length
            
            logger.info(f"Extracted comment info - Author: {author}, Date: {date}, Text length: {len(comment_text)}")
            logger.debug(f"Comment details - Author: '{author}', Date: '{date}', Text: '{comment_text[:100]}...'")
            
            return CommentInfo(
                author=author,
                date=date,
                text=comment_text,
                comment_id=comment_id
            )
            
        except Exception as e:
            logger.error(f"Error extracting comment info: {e}")
            return None
    
    def download_image(self, image_url: str) -> Optional[bytes]:
        """
        Download image from URL.
        
        Args:
            image_url: URL of the image to download
            
        Returns:
            Image bytes or None if download failed
        """
        try:
            if not image_url:
                return None
            
            logger.info(f"Downloading image: {image_url}")
            response = self.session.get(image_url, timeout=10)
            response.raise_for_status()
            
            # Check if response is actually an image
            content_type = response.headers.get('content-type', '')
            if not content_type.startswith('image/'):
                logger.warning(f"URL does not return an image: {content_type}")
                return None
            
            return response.content
            
        except Exception as e:
            logger.error(f"Error downloading image {image_url}: {e}")
            return None
    
    def _get_comment_from_api(self, comment_id: str, game_slug: str) -> Optional[CommentInfo]:
        """
        Get comment information using the WTG API.
        
        Args:
            comment_id: The sharing ID of the comment
            game_slug: The game ID extracted from HTML
            
        Returns:
            CommentInfo object or None if failed
        """
        try:
            # Construct API URL
            api_url = "https://wtg.com.ua/api/backlog/user_review/user"
            params = {
                'sharing_id': comment_id,
                'game_slug': game_slug,
                'page': 1,
                'per_page': 1
            }
            
            logger.info(f"Calling API: {api_url} with params: {params}")
            
            # Make API request
            response = self.session.get(api_url, params=params, timeout=10)
            response.raise_for_status()
            
            # Ensure proper UTF-8 encoding for Cyrillic text
            response.encoding = 'utf-8'
            
            # Parse JSON response
            api_data = response.json()
            logger.info(f"API response status: {response.status_code}")
            logger.info(f"API response keys: {list(api_data.keys()) if isinstance(api_data, dict) else 'Not a dict'}")
            
            # Check if we have data in the response
            if 'user_reviews' in api_data and api_data['user_reviews']:
                data_content = api_data['user_reviews']
                
                # The data might be a list of reviews or a single review object
                if isinstance(data_content, list) and len(data_content) > 0:
                    review_data = data_content[0]
                elif isinstance(data_content, dict):
                    review_data = data_content
                else:
                    logger.warning("Unexpected data structure in API response")
                    return None
                
                logger.info(f"Review data keys: {list(review_data.keys()) if isinstance(review_data, dict) else 'Not a dict'}")
                
                # Extract user information
                author = review_data.get('user', {})

                # Extract review text - try different possible field names
                review_text = (review_data.get('text') or 'Review text not available')
                
                # Extract date
                date_created = (review_data.get('created_at') or 
                              review_data.get('updated_at') or 
                              'Unknown Date')
                
                # Format date if it's in ISO format
                if date_created and date_created != 'Unknown Date':
                    try:
                        from datetime import datetime
                        if 'T' in str(date_created):
                            dt = datetime.fromisoformat(str(date_created).replace('Z', '+00:00'))
                            date_created = dt.strftime('%d.%m.%Y')
                    except Exception as e:
                        logger.debug(f"Date parsing error: {e}")
                        # Keep original date if parsing fails
                        pass
                
                logger.info(f"Successfully extracted comment from API - Author: {author}, Date: {date_created}, Text length: {len(str(review_text))}")
                
                return CommentInfo(
                    author=author,
                    date=str(date_created),
                    text=str(review_text),
                    comment_id=comment_id
                )
            else:
                logger.warning("No data found in API response or data is empty")
                logger.debug(f"Full API response: {api_data}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"API request error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error processing API response: {e}")
            return None
    
    def _parse_date(self, date_string: str) -> str:
        """
        Parse various date formats from the API.
        
        Args:
            date_string: Date string from API
            
        Returns:
            Formatted date string
        """
        try:
            # Try different date formats
            import datetime
            
            # ISO format: 2024-06-15T12:30:00Z
            if 'T' in date_string:
                dt = datetime.datetime.fromisoformat(date_string.replace('Z', '+00:00'))
                return dt.strftime('%d.%m.%Y')
            
            # Other formats can be added here as needed
            return date_string
            
        except Exception as e:
            logger.warning(f"Could not parse date '{date_string}': {e}")
            return date_string
