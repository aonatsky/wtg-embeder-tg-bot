#!/usr/bin/env python3
"""
Simple test script to validate WTG scraping functionality
"""

import sys
import asyncio
from scraper import WTGScraper
from utils import extract_wtg_links, validate_wtg_url, format_game_message_html

# Test URLs
TEST_URLS = [
    "https://wtg.com.ua/game/lost-in-random-the-eternal-die/comment/06672ce6-96ce-471c-aea2-6ec3cd30cde8",
    "https://wtg.com.ua/game/test-game-name/comment/12345678-1234-5678-9abc-123456789abc"
]

def test_url_extraction():
    """Test URL extraction from text"""
    print("Testing URL extraction...")
    
    test_text = f"""
    Check out this game review: {TEST_URLS[0]}
    And also this one: {TEST_URLS[1]}
    This is not a WTG link: https://example.com
    """
    
    links = extract_wtg_links(test_text)
    print(f"Found {len(links)} WTG links:")
    for link in links:
        print(f"  - {link}")
        print(f"    Valid: {validate_wtg_url(link)}")
    
    return len(links) == 2

def test_scraping():
    """Test scraping functionality"""
    print("\nTesting scraping...")
    
    scraper = WTGScraper()
    
    # Test with first URL
    url = TEST_URLS[0]
    print(f"Scraping: {url}")
    
    try:
        wtg_data = scraper.scrape_game_page(url)
        
        if wtg_data:
            print("✅ Scraping successful!")
            print(f"Game: {wtg_data.game.title}")
            print(f"Score: {wtg_data.game.score}")
            print(f"Image: {wtg_data.game.image_url[:50]}..." if wtg_data.game.image_url else "No image")
            print(f"Comment by: {wtg_data.comment.author}")
            print(f"Comment date: {wtg_data.comment.date}")
            print(f"Comment text: {wtg_data.comment.text[:100]}...")
            
            # Test message formatting
            print("\nFormatted message:")
            message = format_game_message_html(wtg_data)
            print(message)
            
            return True
        else:
            print("❌ Scraping failed - no data returned")
            return False
            
    except Exception as e:
        print(f"❌ Scraping error: {e}")
        return False

def main():
    """Run all tests"""
    print("WTG Bot Test Suite")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 2
    
    # Test URL extraction
    if test_url_extraction():
        tests_passed += 1
        print("✅ URL extraction test passed")
    else:
        print("❌ URL extraction test failed")
    
    # Test scraping (this will fail without actual WTG site access)
    if test_scraping():
        tests_passed += 1
        print("✅ Scraping test passed")
    else:
        print("❌ Scraping test failed (expected if WTG site is inaccessible)")
    
    print("\n" + "=" * 50)
    print(f"Tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed - this is expected without internet access")
        return 1

if __name__ == "__main__":
    sys.exit(main())
