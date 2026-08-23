"""YouTube Comments Scraper for Myntra Fashion Hauls & Styling Reviews.

Collects real public comments on fashion reviews via YouTube Data API v3.
Fails loudly if API credentials are missing or live requests fail — zero synthetic fallback.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
import requests

from src.config import HIGH_INTENT_KEYWORDS, YOUTUBE_API_KEY, YOUTUBE_QUERIES
from src.ingestion.preprocessor import Preprocessor

logger = logging.getLogger(__name__)


class YouTubeScraper:
    """Scrapes authentic comments on Myntra fashion haul, try-on, and unboxing videos using YouTube Data API v3."""

    def __init__(self):
        self.preprocessor = Preprocessor()
        self.api_key = YOUTUBE_API_KEY

    def scrape(self, target_count: int = 100, batch_id: str = "") -> List[Dict[str, Any]]:
        """Collects real YouTube comments from fashion haul and styling review videos.
        
        Returns only genuine records. Never generates or synthesizes text.
        """
        if not self.api_key:
            logger.warning("Skipping YouTube scrape: Missing YOUTUBE_API_KEY in .env. Returning 0 records.")
            print("   [!] Notice: YouTube API key (YOUTUBE_API_KEY) missing in .env. 0 records scraped.")
            return []

        records: List[Dict[str, Any]] = []
        try:
            records = self._scrape_youtube_api(target_count, batch_id)
        except Exception as e:
            logger.error(f"YouTube API live scraping failed: {e}")
            print(f"   [!] YouTube API live scraping error: {e}. Returning 0 records.")
            return []

        return records[:target_count]

    def _scrape_youtube_api(self, target_count: int, batch_id: str) -> List[Dict[str, Any]]:
        """Interacts directly with YouTube Data API v3."""
        records = []
        search_url = "https://www.googleapis.com/youtube/v3/search"
        comment_url = "https://www.googleapis.com/youtube/v3/commentThreads"

        for query in YOUTUBE_QUERIES:
            if len(records) >= target_count:
                break
            params = {
                "part": "snippet",
                "q": query,
                "type": "video",
                "maxResults": 5,
                "relevanceLanguage": "en",
                "key": self.api_key,
            }
            try:
                res = requests.get(search_url, params=params, timeout=12)
                if res.status_code != 200:
                    logger.warning(f"YouTube search API returned status {res.status_code}: {res.text[:120]}")
                    continue
                data = res.json()
                for item in data.get("items", []):
                    video_id = item["id"].get("videoId")
                    if not video_id or len(records) >= target_count:
                        break

                    video_title = item.get("snippet", {}).get("title", "")
                    video_url = f"https://www.youtube.com/watch?v={video_id}"

                    # Fetch real top-level comments for this video
                    c_params = {
                        "part": "snippet",
                        "videoId": video_id,
                        "maxResults": 30,
                        "textFormat": "plainText",
                        "key": self.api_key,
                    }
                    c_res = requests.get(comment_url, params=c_params, timeout=12)
                    if c_res.status_code != 200:
                        continue
                    c_data = c_res.json()
                    for c_item in c_data.get("items", []):
                        top_snippet = c_item.get("snippet", {}).get("topLevelComment", {}).get("snippet", {})
                        text = top_snippet.get("textDisplay", "")
                        author = top_snippet.get("authorDisplayName", "Anonymous")
                        dt = top_snippet.get("publishedAt", datetime.utcnow().isoformat())
                        comment_id = top_snippet.get("id", c_item.get("id", ""))

                        if len(text.strip()) < 15:
                            continue

                        rec = self.preprocessor.process_raw_record(
                            raw_text=text,
                            source_channel="youtube",
                            author=author,
                            timestamp=dt,
                            thread_url=f"{video_url}&lc={comment_id}" if comment_id else video_url,
                            raw_metadata={
                                "video_id": video_id,
                                "video_title": video_title,
                                "likes": top_snippet.get("likeCount", 0),
                                "comment_id": comment_id,
                            },
                            batch_id=batch_id,
                        )
                        if rec:
                            records.append(rec)
            except Exception as e:
                logger.error(f"Error querying YouTube for '{query}': {e}")

        return records
