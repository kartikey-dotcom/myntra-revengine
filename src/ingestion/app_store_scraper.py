"""App Store & Play Store Reviews Scraper for Myntra Wishlist Discovery.

Collects real customer reviews for com.myntra.android via google-play-scraper.
Fails loudly if network requests fail — zero synthetic fallback.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.ingestion.preprocessor import Preprocessor

logger = logging.getLogger(__name__)


class AppStoreScraper:
    """Scrapes authentic 2-star, 3-star, and 4-star app store customer reviews for Myntra focusing on wishlist UX, sizing, and shopping friction."""

    def __init__(self):
        self.preprocessor = Preprocessor()

    def scrape(self, target_count: int = 150, batch_id: str = "") -> List[Dict[str, Any]]:
        """Collects real Google Play reviews.
        
        Returns only genuine live reviews. Never generates or synthesizes text.
        """
        records: List[Dict[str, Any]] = []
        try:
            records = self._scrape_live_app_stores(target_count, batch_id)
        except Exception as e:
            logger.error(f"Live App Store scraping failed: {e}")
            print(f"   [!] App Store live scraping error: {e}. Returning 0 records.")
            return []

        return records[:target_count]

    def _scrape_live_app_stores(self, target_count: int, batch_id: str) -> List[Dict[str, Any]]:
        records = []
        try:
            from google_play_scraper import Sort, reviews
            
            # Fetch real reviews from Google Play Store for Myntra across newest & most relevant
            scores_to_fetch = [2, 3, 4]
            sort_modes = [Sort.MOST_RELEVANT, Sort.NEWEST]

            for sort_mode in sort_modes:
                for score in scores_to_fetch:
                    if len(records) >= target_count:
                        break

                    result, _ = reviews(
                        "com.myntra.android",
                        lang="en",
                        country="in",
                        sort=sort_mode,
                        count=60,
                        filter_score_with=score,
                    )

                for rev in result:
                    if len(records) >= target_count:
                        break

                    text = rev.get("content", "").strip()
                    if len(text) < 15:
                        continue

                    author = rev.get("userName", "Anonymous")
                    rating = rev.get("score", score)
                    raw_date = rev.get("at")
                    dt = raw_date.isoformat() if isinstance(raw_date, datetime) else str(raw_date or datetime.utcnow().isoformat())
                    review_id = rev.get("reviewId", "")

                    # Direct permalink to the app on Google Play Store
                    thread_url = f"https://play.google.com/store/apps/details?id=com.myntra.android&reviewId={review_id}" if review_id else "https://play.google.com/store/apps/details?id=com.myntra.android"

                    rec = self.preprocessor.process_raw_record(
                        raw_text=text,
                        source_channel="app_store",
                        author=author,
                        timestamp=dt,
                        thread_url=thread_url,
                        raw_metadata={
                            "rating": rating,
                            "platform": "google_play",
                            "app_version": rev.get("reviewCreatedVersion", "unknown"),
                            "thumbs_up": rev.get("thumbsUpCount", 0),
                            "review_id": review_id,
                        },
                        batch_id=batch_id,
                    )
                    if rec:
                        records.append(rec)

        except ImportError:
            logger.error("google-play-scraper package is not installed.")
            print("   [!] Error: google-play-scraper package not installed. Returning 0 records.")
        except Exception as e:
            logger.error(f"Google Play live scraping exception: {e}")
            print(f"   [!] Google Play scraper exception: {e}")

        return records
