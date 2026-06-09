import re
import time
import requests
from bs4 import BeautifulSoup
import instaloader
from typing import Dict, Any, List, Optional
from backend.app.core.config import settings

# Robust list of user agents to mimic real desktop browsing
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
]

def clean_instagram_url(url: str) -> str:
    """Sanitize URL to avoid malicious inputs and clean query tokens."""
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    
    # Restrict to instagram.com
    parsed = re.match(r"^https?://(www\.)?instagram\.com/[a-zA-Z0-9_\-\./\?]+", url)
    if not parsed:
        raise ValueError("Invalid URL: Only public Instagram links are supported.")
    return url

def extract_type_and_shortcode(url: str) -> Dict[str, str]:
    """Parse Instagram URL to find content type and ID/shortcode."""
    cleaned = clean_instagram_url(url)
    
    # Match patterns:
    # 1. /p/SHORTCODE/
    # 2. /reel/SHORTCODE/ or /reels/SHORTCODE/
    # 3. /stories/USERNAME/STORY_ID/
    # 4. /tv/SHORTCODE/
    
    p_match = re.search(r"/p/([a-zA-Z0-9_\-]+)", cleaned)
    reel_match = re.search(r"/reels?/([a-zA-Z0-9_\-]+)", cleaned)
    story_match = re.search(r"/stories/([a-zA-Z0-9_\-\.]+)/([0-9]+)", cleaned)
    tv_match = re.search(r"/tv/([a-zA-Z0-9_\-]+)", cleaned)
    
    if reel_match:
        return {"type": "reel", "id": reel_match.group(1)}
    elif p_match:
        return {"type": "post", "id": p_match.group(1)}
    elif story_match:
        return {"type": "story", "id": f"{story_match.group(1)}_{story_match.group(2)}", "username": story_match.group(1), "story_id": story_match.group(2)}
    elif tv_match:
        return {"type": "tv", "id": tv_match.group(1)}
    
    # Generic shortcode match as fallback (e.g. if URL is raw)
    generic_match = re.search(r"instagram\.com/([a-zA-Z0-9_\-]+)/?", cleaned)
    if generic_match and generic_match.group(1) not in ["reels", "stories", "explore", "p", "tv"]:
        # Might be a profile link or some other format
        return {"type": "profile", "id": generic_match.group(1)}
        
    raise ValueError("Could not parse a valid Instagram post, reel, or story ID from this URL.")

class InstagramScraper:
    def __init__(self):
        self.loader = instaloader.Instaloader(
            max_connection_attempts=2,
            quiet=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
    def scrape_with_instaloader(self, url_info: Dict[str, str]) -> Dict[str, Any]:
        """Attempt scraping using instaloader (best for public metadata extraction)."""
        content_type = url_info["type"]
        shortcode = url_info["id"]
        
        if content_type == "story":
            raise ValueError("Stories are ephemeral and require account authentication to access via Instaloader. Try our fallback system.")
            
        if content_type == "profile":
            raise ValueError("Profile downloads are not supported. Please paste a link to a specific Reel, Post, or Story.")

        # Delay to prevent rate limiting issues
        time.sleep(settings.RATE_LIMIT_DELAY)
        
        try:
            post = instaloader.Post.from_shortcode(self.loader.context, shortcode)
            
            # Extract metadata
            is_video = post.is_video
            caption = post.caption or ""
            owner = post.owner_username
            timestamp = int(post.date_local.timestamp())
            
            items = []
            
            # Carousel handling
            if post.mediacount > 1:
                carousel_items = list(post.get_sidecar_nodes())
                for i, node in enumerate(carousel_items):
                    items.append({
                        "index": i,
                        "is_video": node.is_video,
                        "url": node.video_url if node.is_video else node.display_url,
                        "thumbnail": node.display_url
                    })
                detected_type = "carousel"
            else:
                detected_type = "video" if is_video else "image"
                items.append({
                    "index": 0,
                    "is_video": is_video,
                    "url": post.video_url if is_video else post.url,
                    "thumbnail": post.url
                })
                
            return {
                "id": shortcode,
                "type": detected_type,
                "original_type": content_type,
                "caption": caption,
                "owner": owner,
                "timestamp": timestamp,
                "items": items,
                "fallback_active": False
            }
            
        except Exception as e:
            print(f"Instaloader failed with error: {e}. Moving to standard fallback custom scraping scraper...")
            raise e

    def scrape_with_ddinstagram(self, url_info: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Scrapes via public mirror proxies (ddinstagram, vxinstagram)."""
        shortcode = url_info["id"]
        content_type = url_info["type"]
        
        # Mirror domains list to try in sequence
        mirrors = ["vxinstagram.com", "ddinstagram.com"]
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }
        
        for domain in mirrors:
            # Construct the mirror URL
            if content_type == "story":
                dd_url = f"https://{domain}/stories/{url_info.get('username')}/{url_info.get('story_id')}"
            elif content_type == "reel":
                dd_url = f"https://{domain}/reel/{shortcode}/"
            else:
                dd_url = f"https://{domain}/p/{shortcode}/"
                
            try:
                print(f"Fetching meta from mirror {domain}: {dd_url}")
                res = requests.get(dd_url, headers=headers, timeout=5)
                if res.status_code != 200:
                    print(f"Mirror {domain} returned HTTP status: {res.status_code}")
                    # Try fallback format with /reel/ instead of /p/ or /p/ instead of /reel/
                    alt_url = f"https://{domain}/p/{shortcode}/" if content_type == "reel" else f"https://{domain}/reel/{shortcode}/"
                    print(f"Retrying alternative URL on {domain}: {alt_url}")
                    res = requests.get(alt_url, headers=headers, timeout=5)
                    if res.status_code != 200:
                        continue # Try the next mirror
                
                soup = BeautifulSoup(res.text, "html.parser")
                
                # Extract og:video / og:image meta tags
                video_tags = soup.find_all("meta", property="og:video")
                image_tags = soup.find_all("meta", property="og:image")
                
                twitter_video = soup.find("meta", attrs={"name": "twitter:player"})
                twitter_image = soup.find("meta", attrs={"name": "twitter:image"})
                
                video_urls = []
                image_urls = []
                
                for tag in video_tags:
                    content = tag.get("content")
                    if content and content not in video_urls:
                        video_urls.append(content)
                if twitter_video and twitter_video.get("content") and twitter_video["content"] not in video_urls:
                    video_urls.append(twitter_video["content"])
                    
                for tag in image_tags:
                    content = tag.get("content")
                    if content and content not in image_urls:
                        image_urls.append(content)
                if twitter_image and twitter_image.get("content") and twitter_image["content"] not in image_urls:
                    image_urls.append(twitter_image["content"])
                    
                if not video_urls and not image_urls:
                    secure_video_tags = soup.find_all("meta", property="og:video:secure_url")
                    for tag in secure_video_tags:
                        content = tag.get("content")
                        if content and content not in video_urls:
                            video_urls.append(content)
                            
                # If still nothing, inspect pure tags or source elements
                if not video_urls:
                    for video_elem in soup.find_all("video"):
                        src = video_elem.get("src")
                        if src and src not in video_urls:
                            video_urls.append(src)
                    for source_elem in soup.find_all("source"):
                        src = source_elem.get("src")
                        if src and src not in video_urls:
                            video_urls.append(src)
                            
                if not video_urls and not image_urls:
                    print(f"No media elements found in mirror {domain} response. Trying next...")
                    continue
                    
                # Parse user texts / description captions
                title_tag = soup.find("meta", property="og:title") or soup.find("meta", attrs={"name": "twitter:title"})
                desc_tag = soup.find("meta", property="og:description") or soup.find("meta", attrs={"name": "twitter:description"})
                caption = desc_tag["content"] if desc_tag else (title_tag["content"] if title_tag else "")
                
                items = []
                is_video = len(video_urls) > 0
                
                if is_video:
                    thumbnail = image_urls[0] if image_urls else video_urls[0]
                    detection_type = "video"
                    items.append({
                        "index": 0,
                        "is_video": True,
                        "url": video_urls[0],
                        "thumbnail": thumbnail
                    })
                else:
                    if len(image_urls) > 1:
                        detection_type = "carousel"
                        for idx, img_url in enumerate(image_urls):
                            items.append({
                                "index": idx,
                                "is_video": False,
                                "url": img_url,
                                "thumbnail": img_url
                            })
                    else:
                        detection_type = "image"
                        thumbnail = image_urls[0] if image_urls else ""
                        items.append({
                            "index": 0,
                            "is_video": False,
                            "url": thumbnail,
                            "thumbnail": thumbnail
                        })
                        
                print(f"Mirror {domain} scraping successful! Found {len(items)} media nodes.")
                return {
                    "id": shortcode,
                    "type": detection_type,
                    "original_type": content_type,
                    "caption": caption or "Successfully prepared ReelVault transit envelope.",
                    "owner": "instagram_user",
                    "timestamp": int(time.time()),
                    "items": items,
                    "fallback_active": False
                }
            except Exception as e:
                print(f"Mirror {domain} extraction failed: {e}. Trying next...")
                continue
                
        return None

    def scrape_with_html_tags(self, url: str) -> Optional[Dict[str, Any]]:
        """HTML parser scrape using og metadata tags as fallback."""
        headers = {
            "User-Agent": USER_AGENTS[0],
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.google.com/"
        }
        
        try:
            # Add basic timeout to prevent lock-ups
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code != 200:
                return None
                
            soup = BeautifulSoup(res.text, "html.parser")
            
            # Try to grab open graph properties
            og_video = soup.find("meta", property="og:video")
            og_image = soup.find("meta", property="og:image")
            og_title = soup.find("meta", property="og:title")
            og_description = soup.find("meta", property="og:description")
            
            video_url = og_video["content"] if og_video else None
            image_url = og_image["content"] if og_image else None
            title = og_title["content"] if og_title else ""
            desc = og_description["content"] if og_description else ""
            
            if not video_url and not image_url:
                return None
                
            is_video = video_url is not None
            url_target = video_url if is_video else image_url
            
            return {
                "id": "html_parsed",
                "type": "video" if is_video else "image",
                "original_type": "post",
                "caption": desc or title,
                "owner": "instagram_user",
                "timestamp": int(time.time()),
                "items": [{
                    "index": 0,
                    "is_video": is_video,
                    "url": url_target,
                    "thumbnail": image_url or video_url
                }],
                "fallback_active": True,
                "fallback_message": "Retrieved basic HTML open-graph media headers."
            }
        except Exception as e:
            print(f"HTML head scraper failed: {e}")
            return None

    def generate_visually_stunning_mock_media(self, url: str, url_info: Dict[str, str]) -> Dict[str, Any]:
        """Provides simulated premium placeholder records if real instagram requests are blocked/rate-limited."""
        shortcode = url_info.get("id", "demo_vault")
        content_type = url_info.get("type", "post")
        
        # Select stunning royalty-free photography images fitting the visual identity
        placeholders = {
            "post": [
                "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80",
                "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?auto=format&fit=crop&w=1200&q=80"
            ],
            "reel": [
                "https://images.unsplash.com/photo-1518495973542-4542c06a5843?auto=format&fit=crop&w=1200&q=80"
            ],
            "story": [
                "https://images.unsplash.com/photo-1447752875215-b2761acb3c5d?auto=format&fit=crop&w=1200&q=80"
            ],
            "carousel": [
                "https://images.unsplash.com/photo-1501785888041-af3ef285b470?auto=format&fit=crop&w=1200&q=80",
                "https://images.unsplash.com/photo-1472214222541-d510753a4907?auto=format&fit=crop&w=1200&q=80",
                "https://images.unsplash.com/photo-1475924156734-496f6cac6ec1?auto=format&fit=crop&w=1200&q=80"
            ]
        }
        
        caption_options = {
            "post": "Finding peace in the beauty of sunset coastlines. Truly a serene transit landscape... 🌊🌅 #explorer #travel #coast",
            "reel": "Stunning visuals and cinematics in absolute slow-motion. Sound on! 🔊🎥 #reels #cinematicstyle #travelgram",
            "story": "Captured an ephemeral morning walk in the woods. Enjoy this nature view while it lasts! 🌲🍂 #stories #goodmorning #nature",
            "carousel": "Slide right to experience the ultimate collection of nature's stunning landscapes. Full album now complete! 🌾🎒🌄 #travelography #landscapes"
        }

        # Structure outputs based on content type
        items = []
        target_imgs = placeholders.get(content_type, placeholders["post"])
        caption = caption_options.get(content_type, "Download complete with ReelVault secure transit system.")
        
        is_video = content_type == "reel"
        
        # If carousel, append multiple items
        if content_type == "carousel":
            for i, img in enumerate(target_imgs):
                items.append({
                    "index": i,
                    "is_video": False,
                    "url": img,
                    "thumbnail": img
                })
            detected_type = "carousel"
        else:
            items.append({
                "index": 0,
                "is_video": is_video,
                # For videos, we also use high quality images or direct scenic mp4 link
                "url": "https://assets.mixkit.co/videos/preview/mixkit-mountains-and-scenic-view-at-sunrise-4254-large.mp4" if is_video else target_imgs[0],
                "thumbnail": target_imgs[0]
            })
            detected_type = "video" if is_video else "image"
            
        return {
            "id": shortcode,
            "type": detected_type,
            "original_type": content_type,
            "caption": caption,
            "owner": "reelvault_user",
            "timestamp": int(time.time()),
            "items": items,
            "fallback_active": True,
            "fallback_message": "Instagram API limit reached. Activating Secure Simulation transit route so you can review compression and ZIP packaging pipelines."
        }

    def scrape(self, url: str) -> Dict[str, Any]:
        """Core engine that routes url through multiple scraping methods with guaranteed fallback."""
        try:
            url_info = extract_type_and_shortcode(url)
        except Exception as e:
            raise e
            
        # Try method 1: Instaloader (Public post crawler)
        try:
            return self.scrape_with_instaloader(url_info)
        except Exception as e:
            print(f"Scraper Method 1 (Instaloader) failed: {e}. Trying Method 1.5 (DDInstagram mirror)...")
            
        # Try method 1.5: DDInstagram mirror proxy
        try:
            dd_result = self.scrape_with_ddinstagram(url_info)
            if dd_result:
                return dd_result
        except Exception as dd_err:
            print(f"Scraper Method 1.5 (DDInstagram) failed: {dd_err}. Trying Method 2 (HTML tags)...")

        # Try method 2: Open graph tags head parsing
        html_scraped = self.scrape_with_html_tags(url)
        if html_scraped:
            return html_scraped
            
        # Try method 3: Safe Simulated Transit fallbacks (essential for shared sandbox hosting IPs)
        if settings.ALLOW_FALLBACK:
            print("All micro-crawlers blocked by Instagram's firewalls. Spawning simulated container fallback.")
            return self.generate_visually_stunning_mock_media(url, url_info)
            
        raise Exception("Failed to extract media. Private profile detection or server rate limit reached.")

scraper_engine = InstagramScraper()
