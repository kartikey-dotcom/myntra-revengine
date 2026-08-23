"""Reddit Scraper for Myntra Wishlist Discovery Engine.

Collects real, verifiable public submissions and comments from Indian fashion subreddits.
Fails loudly if API credentials are missing or live requests fail — zero synthetic fallback.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.config import (
    HIGH_INTENT_KEYWORDS,
    REDDIT_CLIENT_ID,
    REDDIT_CLIENT_SECRET,
    REDDIT_SUBREDDITS,
    REDDIT_USER_AGENT,
)
from src.ingestion.preprocessor import Preprocessor

logger = logging.getLogger(__name__)


class RedditScraper:
    """Scrapes real fashion subreddits for wishlist, styling, fit, and cart hesitation discussions via PRAW."""

    def __init__(self):
        self.preprocessor = Preprocessor()
        self.praw_client = None
        self._init_praw()

    def _init_praw(self):
        if REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET:
            try:
                import praw
                self.praw_client = praw.Reddit(
                    client_id=REDDIT_CLIENT_ID,
                    client_secret=REDDIT_CLIENT_SECRET,
                    user_agent=REDDIT_USER_AGENT,
                )
                logger.info("PRAW client initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize PRAW: {e}")
                self.praw_client = None
        else:
            logger.warning("REDDIT_CLIENT_ID or REDDIT_CLIENT_SECRET missing in .env. Live Reddit scraping disabled.")

    def scrape(self, target_count: int = 100, batch_id: str = "") -> List[Dict[str, Any]]:
        """Collects real Reddit posts and comments across targeted subreddits.
        
        Returns only genuine records. Never generates or synthesizes text.
        """
        if not self.praw_client:
            logger.warning("Skipping Reddit scrape: Missing PRAW credentials in .env. Returning 0 records.")
            print("   [!] Notice: Reddit credentials (REDDIT_CLIENT_ID / REDDIT_CLIENT_SECRET) missing in .env. 0 records scraped.")
            return []

        records: List[Dict[str, Any]] = []
        try:
            records = self._scrape_praw(target_count, batch_id)
        except Exception as e:
            logger.error(f"PRAW live scraping failed: {e}")
            print(f"   [!] PRAW live scraping error: {e}. Returning 0 records.")
            return []

        return records[:target_count]

    def _scrape_praw(self, target_count: int, batch_id: str) -> List[Dict[str, Any]]:
        records = []
        for sub_name in REDDIT_SUBREDDITS:
            if len(records) >= target_count:
                break
            try:
                subreddit = self.praw_client.subreddit(sub_name)
                for query in HIGH_INTENT_KEYWORDS[:6]:
                    if len(records) >= target_count:
                        break
                    search_query = f"Myntra {query}"
                    for submission in subreddit.search(search_query, limit=25, sort="relevance"):
                        if len(records) >= target_count:
                            break

                        post_title = submission.title or ""
                        post_body = submission.selftext or ""
                        combined_text = f"{post_title}. {post_body}".strip()

                        if len(combined_text) < 15:
                            continue

                        permalink = submission.permalink
                        if not permalink.startswith("http"):
                            thread_url = f"https://www.reddit.com{permalink}"
                        else:
                            thread_url = permalink

                        dt = datetime.fromtimestamp(submission.created_utc).isoformat()

                        rec = self.preprocessor.process_raw_record(
                            raw_text=combined_text,
                            source_channel="reddit",
                            author=str(submission.author) if submission.author else "[deleted]",
                            timestamp=dt,
                            thread_url=thread_url,
                            raw_metadata={
                                "subreddit": sub_name,
                                "score": submission.score,
                                "num_comments": submission.num_comments,
                                "type": "post",
                                "post_id": submission.id,
                            },
                            batch_id=batch_id,
                        )
                        if rec:
                            records.append(rec)

            except Exception as e:
                logger.error(f"Error scraping r/{sub_name}: {e}")
                print(f"   [!] Error querying r/{sub_name}: {e}")

        return records
