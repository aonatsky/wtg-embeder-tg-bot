from dataclasses import dataclass
from typing import Optional


@dataclass
class GameInfo:
    """Data model for game information"""
    title: str
    score: str
    image_url: str
    
    
@dataclass  
class CommentInfo:
    """Data model for comment information"""
    author: str
    date: str
    text: str
    comment_id: str


@dataclass
class WTGData:
    """Combined data model for WTG page information"""
    game: GameInfo
    comment: CommentInfo
    original_url: str
