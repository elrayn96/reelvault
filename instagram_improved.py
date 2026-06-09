"""
Improved Instagram scraper with better retry logic and fallback mechanisms
to handle Instagram's 403 blocks.
"""

import re
import time
import requests
import instaloader
from typing import Dict, Any, List, Optional
from backend.app.core.config import settings

def improved_scraper(url: str) -> Dict[str, Any]:
    """
    Enhanced scraper with retry logic for 403 errors
    """
    # Extract shortcode
    shortcode_match = re.findall(r'/(?:reels?|p)/([^/?]+)', url)
    if not shortcode_match:
        raise ValueError(f"Could not extract shortcode from {url}")
    
    shortcode = shortcode_match[0]
    print(f"[Improved Scraper] Shortcode: {shortcode}")
    
    # Retry loop to bypass 403 blocks
    for attempt in range(1, 4):
        try:
            print(f"[Improved Scraper] Attempt {attempt}/3 to fetch post...")
            
            # Create fresh loader each time (helps with 403s)
            loader = instaloader.Instaloader(
                max_connection_attempts=2,
                quiet=True,
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
            # Try to fetch
            post = instaloader.Post.from_shortcode(loader.context, shortcode)
            
            print(f"[Improved Scraper] ✓ Successfully fetched post on attempt {attempt}")
            
            # Extract data
            is_video = post.is_video
            download_url = post.video_url if is_video else post.url
            thumbnail_url = post.url
            
            print(f"[Improved Scraper] Media: {('video' if is_video else 'image')}")
            print(f"[Improved Scraper] URLs extracted successfully")
            
            return {
                "id": shortcode,
                "type": "video" if is_video else "image",
                "original_type": "reel" if "reel" in url.lower() else "post",
                "caption": post.caption or "",
                "owner": post.owner_username,
                "timestamp": int(post.date_local.timestamp()),
                "items": [{
                    "index": 0,
                    "is_video": is_video,
                    "url": download_url,
                    "thumbnail": thumbnail_url
                }],
                "fallback_active": False,
                "direct_extraction": True
            }
            
        except instaloader.exceptions.ConnectionException as e:
            error_msg = str(e)
            if "403" in error_msg or "Forbidden" in error_msg:
                print(f"[Improved Scraper] Attempt {attempt}: Instagram blocked (403). Retrying...")
                if attempt < 3:
                    # Exponential backoff
                    wait_time = min(2 ** attempt, 8)
                    print(f"[Improved Scraper] Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                    continue
            raise
        
        except Exception as e:
            print(f"[Improved Scraper] Attempt {attempt} failed: {e}")
            if attempt < 3:
                time.sleep(2)
                continue
            raise
    
    raise Exception("Could not fetch Instagram post after 3 attempts. Instagram is blocking requests.")


if __name__ == "__main__":
    try:
        result = improved_scraper("https://www.instagram.com/reels/DZS8sy_uj5U/")
        print("\n✅ SUCCESS!")
        print(f"Video URL: {result['items'][0]['url'][:80]}...")
        print(f"Thumbnail: {result['items'][0]['thumbnail'][:80]}...")
    except Exception as e:
        print(f"\n❌ FAILED: {e}")
