#!/usr/bin/env python3
"""
Quick test to verify if direct Instagram reel extraction is working correctly.
Run this to see exactly what URLs are being extracted.
"""

import sys
import os
import re
import instaloader

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_direct_extraction():
    """Test direct video URL extraction"""
    
    # Test URL
    test_url = "https://www.instagram.com/reels/DZS8sy_uj5U/"
    
    print("\n" + "=" * 70)
    print("🔍 Testing Direct Instagram Reel Extraction")
    print("=" * 70)
    print(f"\nTest URL: {test_url}")
    
    # Step 1: Extract shortcode
    print("\n[Step 1] Extracting shortcode...")
    shortcode_match = re.findall(r'/(?:reels?|p)/([^/?]+)', test_url)
    if not shortcode_match:
        print("❌ Failed to extract shortcode!")
        return False
    
    shortcode = shortcode_match[0]
    print(f"✅ Shortcode: {shortcode}")
    
    # Step 2: Create instaloader instance
    print("\n[Step 2] Initializing Instaloader...")
    try:
        loader = instaloader.Instaloader(quiet=True)
        print("✅ Instaloader initialized")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return False
    
    # Step 3: Fetch post
    print("\n[Step 3] Fetching post from Instagram...")
    try:
        post = instaloader.Post.from_shortcode(loader.context, shortcode)
        print("✅ Post fetched successfully")
    except Exception as e:
        print(f"❌ Failed to fetch post: {e}")
        return False
    
    # Step 4: Check if video
    print(f"\n[Step 4] Analyzing media type...")
    print(f"  - is_video: {post.is_video}")
    print(f"  - mediacount: {post.mediacount}")
    print(f"  - owner: {post.owner_username}")
    print(f"  - caption: {post.caption[:60] if post.caption else 'None'}...")
    
    # Step 5: Extract URLs
    print(f"\n[Step 5] Extracting media URLs...")
    
    if post.is_video:
        video_url = post.video_url
        if not video_url:
            print("❌ Video URL is None!")
            return False
        
        print(f"✅ Video URL extracted:")
        print(f"   Length: {len(video_url)} chars")
        print(f"   URL (first 100 chars): {video_url[:100]}...")
        
        # Use post.url for thumbnail (this works in newer instaloader)
        thumbnail = post.url
        print(f"✅ Thumbnail extracted using post.url:")
        print(f"   Length: {len(thumbnail)} chars") 
        print(f"   URL: {thumbnail[:100]}...")
        
        # Test if URLs are accessible
        print(f"\n[Step 6] Testing URL accessibility...")
        import requests
        
        try:
            print("  Testing video URL...")
            resp = requests.head(video_url, timeout=10)
            if resp.status_code == 200:
                print(f"  ✅ Video URL is accessible! (HTTP {resp.status_code})")
                size = resp.headers.get('content-length', '?')
                print(f"     Size: {size} bytes")
            else:
                print(f"  ⚠️  Video URL returned HTTP {resp.status_code}")
        except Exception as e:
            print(f"  ❌ Video URL error: {e}")
        
        try:
            print("  Testing thumbnail URL...")
            resp = requests.head(thumbnail, timeout=10)
            if resp.status_code == 200:
                print(f"  ✅ Thumbnail URL is accessible! (HTTP {resp.status_code})")
            else:
                print(f"  ⚠️  Thumbnail URL returned HTTP {resp.status_code}")
        except Exception as e:
            print(f"  ❌ Thumbnail URL error: {e}")
        
        print("\n" + "=" * 70)
        print("✅ EXTRACTION SUCCESSFUL!")
        print("=" * 70)
        print(f"\nReady to download:")
        print(f"  Video:     {video_url}")
        print(f"  Thumbnail: {thumbnail}")
        
        return True
    else:
        # For images, post.url contains the image URL
        image_url = post.url
        if not image_url:
            print("❌ Image URL is None!")
            return False
        
        print(f"✅ Image URL extracted: {image_url}")
        return True

if __name__ == "__main__":
    try:
        success = test_direct_extraction()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
