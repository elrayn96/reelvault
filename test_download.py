#!/usr/bin/env python3
"""
Test script to validate Instagram reel/post downloads with .mp4 and .zip support.
Uses the improved scraper logic similar to a.py
"""

import sys
import os
import re
import requests
import instaloader
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.core.config import settings
from app.scrapers.instagram import InstagramScraper, extract_type_and_shortcode

def extract_shortcode_simple(url: str) -> str:
    """Extract shortcode using simple regex (from a.py logic)"""
    shortcode_match = re.findall(r'/reels?/([^/?]+)', url)
    if shortcode_match:
        return shortcode_match[0]
    raise ValueError(f"Could not extract shortcode from URL: {url}")

def test_direct_extraction(url: str) -> dict:
    """Test direct video URL extraction similar to a.py"""
    print(f"\n📝 Testing Direct Extraction from: {url}")
    print("=" * 60)
    
    try:
        # Extract shortcode
        shortcode = extract_shortcode_simple(url)
        print(f"✓ Shortcode extracted: {shortcode}")
        
        # Initialize Instaloader
        loader = instaloader.Instaloader(quiet=True)
        
        # Fetch post
        print("🔗 Fetching Instagram post...")
        post = instaloader.Post.from_shortcode(loader.context, shortcode)
        
        # Get video URL (main logic from a.py)
        if post.is_video:
            video_url = post.video_url
            print(f"✓ Video detected!")
            print(f"✓ Direct video URL: {video_url[:80]}...")
            
            # Test downloading a small chunk
            print("📥 Testing video download...")
            response = requests.head(video_url, timeout=10)
            if response.status_code == 200:
                content_length = response.headers.get('content-length', 'unknown')
                print(f"✓ Video accessible! Size: {content_length} bytes")
                file_format = ".mp4"
            else:
                print(f"✗ Video not accessible (HTTP {response.status_code})")
                file_format = None
        else:
            display_url = post.display_url
            print(f"✓ Image detected!")
            print(f"✓ Direct image URL: {display_url[:80]}...")
            file_format = ".jpg"
        
        # Collect metadata
        result = {
            "status": "success",
            "shortcode": shortcode,
            "is_video": post.is_video,
            "media_type": "video" if post.is_video else "image",
            "file_format": file_format,
            "caption": post.caption[:100] if post.caption else "No caption",
            "owner": post.owner_username,
            "post_url": f"https://www.instagram.com/p/{shortcode}/"
        }
        
        print(f"\n✓ Direct Extraction Result:")
        print(f"  - Media Type: {result['media_type']}")
        print(f"  - File Format: {result['file_format']}")
        print(f"  - Owner: {result['owner']}")
        print(f"  - Status: {result['status']}")
        
        return result
        
    except Exception as e:
        print(f"\n✗ Error during extraction: {e}")
        return {"status": "failed", "error": str(e)}

def test_scraper_engine(url: str) -> dict:
    """Test the improved scraper engine"""
    print(f"\n🔧 Testing Improved Scraper Engine")
    print("=" * 60)
    
    try:
        scraper = InstagramScraper()
        result = scraper.scrape(url)
        
        print(f"✓ Scraper completed successfully!")
        print(f"  - ID: {result.get('id')}")
        print(f"  - Type: {result.get('type')}")
        print(f"  - Items: {len(result.get('items', []))}")
        print(f"  - Fallback Active: {result.get('fallback_active', False)}")
        
        if result.get('items'):
            first_item = result['items'][0]
            print(f"  - First Item Is Video: {first_item.get('is_video')}")
            print(f"  - URL Available: {'url' in first_item}")
        
        return {"status": "success", "scraped_data": result}
        
    except Exception as e:
        print(f"\n✗ Scraper error: {e}")
        return {"status": "failed", "error": str(e)}

def validate_zip_creation() -> dict:
    """Test ZIP file creation logic"""
    print(f"\n📦 Testing ZIP Creation Logic")
    print("=" * 60)
    
    import zipfile
    import tempfile
    import uuid
    
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            test_files = [
                ("video_1.mp4", b"fake mp4 data 1"),
                ("video_2.mp4", b"fake mp4 data 2"),
                ("image_1.jpg", b"fake jpg data 1"),
            ]
            
            # Create test files
            file_paths = []
            for filename, data in test_files:
                fpath = os.path.join(tmpdir, filename)
                with open(fpath, 'wb') as f:
                    f.write(data)
                file_paths.append((fpath, filename))
            
            # Create ZIP
            zip_name = f"ReelVault_test_{uuid.uuid4().hex[:6]}.zip"
            zip_path = os.path.join(tmpdir, zip_name)
            
            print(f"📝 Creating ZIP with {len(file_paths)} files...")
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_f:
                for file_path, user_filename in file_paths:
                    zip_f.write(file_path, arcname=user_filename)
                    print(f"  ✓ Added: {user_filename}")
            
            # Verify ZIP
            if os.path.exists(zip_path):
                zip_size = os.path.getsize(zip_path)
                print(f"\n✓ ZIP created successfully!")
                print(f"  - Name: {zip_name}")
                print(f"  - Size: {zip_size} bytes")
                
                # List contents
                with zipfile.ZipFile(zip_path, 'r') as zip_f:
                    print(f"  - Contents: {zip_f.namelist()}")
                
                return {"status": "success", "zip_file": zip_name, "size": zip_size}
            else:
                return {"status": "failed", "error": "ZIP file not created"}
                
    except Exception as e:
        print(f"\n✗ ZIP creation error: {e}")
        return {"status": "failed", "error": str(e)}

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("🧪 ReelVault Download Testing Suite")
    print("=" * 60)
    
    # Test URL (you can modify this)
    test_url = "https://www.instagram.com/reels/DZS8sy_uj5U/"
    
    print(f"\n📌 Test Configuration:")
    print(f"  - Test URL: {test_url}")
    print(f"  - Temp Directory: {settings.TEMP_DIR}")
    print(f"  - Rate Limit Delay: {settings.RATE_LIMIT_DELAY}s")
    
    # Run tests
    results = {}
    
    # Test 1: Direct extraction
    results['direct_extraction'] = test_direct_extraction(test_url)
    
    # Test 2: Scraper engine
    results['scraper_engine'] = test_scraper_engine(test_url)
    
    # Test 3: ZIP creation
    results['zip_creation'] = validate_zip_creation()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    for test_name, test_result in results.items():
        status = test_result.get('status', 'unknown')
        status_icon = "✓" if status == "success" else "✗"
        print(f"{status_icon} {test_name}: {status}")
    
    print("\n✅ Testing completed!")

if __name__ == "__main__":
    main()
