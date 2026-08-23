"""Unit and Integration Tests for Phase 1 Ingestion Pipeline."""

import gc
import tempfile
from pathlib import Path
import pytest

from src.ingestion.preprocessor import Preprocessor
from src.database.db_manager import DatabaseManager
from src.ingestion.reddit_scraper import RedditScraper
from src.ingestion.youtube_scraper import YouTubeScraper
from src.ingestion.app_store_scraper import AppStoreScraper


@pytest.fixture
def temp_db():
    """Creates an isolated temporary SQLite database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        tmp_path = Path(tmp.name)
    db = DatabaseManager(db_path=tmp_path)
    yield db
    # Ensure garbage collection closes open handles on Windows
    gc.collect()
    try:
        if tmp_path.exists():
            tmp_path.unlink()
    except Exception:
        pass


class TestPreprocessor:
    def test_anonymize_author(self):
        p = Preprocessor()
        hash1 = p.anonymize_author("shopper123")
        hash2 = p.anonymize_author("SHOPPER123")
        hash_anon = p.anonymize_author(None)

        assert hash1 == hash2  # Case insensitive
        assert len(hash1) == 16
        assert len(hash_anon) == 16

    def test_clean_text(self):
        p = Preprocessor()
        raw = "<p>Hey check this out: [Myntra link](https://myntra.com/item)   and   http://example.com \n\n</p>"
        cleaned = p.clean_text(raw)
        assert "<p>" not in cleaned
        assert "http" not in cleaned
        assert "Hey check this out: Myntra link and" == cleaned

    def test_process_raw_record(self):
        p = Preprocessor()
        rec = p.process_raw_record(
            raw_text="This dress in my wishlist is so confusing for sizing.",
            source_channel="reddit",
            author="test_user",
            timestamp="2026-08-20T12:00:00",
            thread_url="https://reddit.com/r/test",
            batch_id="test_batch",
        )
        assert rec is not None
        assert rec["source_channel"] == "reddit"
        assert len(rec["author_id_hash"]) == 16
        assert len(rec["id"]) == 24
        assert rec["clean_text"] == "This dress in my wishlist is so confusing for sizing."


class TestDatabaseManager:
    def test_insert_and_deduplication(self, temp_db):
        p = Preprocessor()
        rec = p.process_raw_record(
            raw_text="Saved this jacket on Myntra wishlist, need styling advice.",
            source_channel="reddit",
            author="fashion_lover",
            timestamp="2026-08-20T12:00:00",
            thread_url="https://reddit.com/r/IndianFashionAddicts/comments/test123",
            batch_id="b1",
        )
        assert rec is not None

        # First insert
        count1 = temp_db.insert_feedback_records([rec])
        assert count1 == 1

        # Duplicate insert attempt should be ignored
        count2 = temp_db.insert_feedback_records([rec])
        assert count2 == 0

        assert temp_db.get_total_records() == 1


class TestScrapers:
    def test_reddit_scraper_graceful_handling(self):
        scraper = RedditScraper()
        records = scraper.scrape(target_count=10, batch_id="test_b")
        # When unconfigured in test environment, returns 0 without raising or synthesizing
        assert isinstance(records, list)

    def test_youtube_scraper_graceful_handling(self):
        scraper = YouTubeScraper()
        records = scraper.scrape(target_count=10, batch_id="test_b")
        # When unconfigured in test environment, returns 0 without raising or synthesizing
        assert isinstance(records, list)

    def test_app_store_scraper_output_schema(self):
        scraper = AppStoreScraper()
        records = scraper.scrape(target_count=10, batch_id="test_b")
        assert len(records) > 0
        for r in records:
            assert r["source_channel"] == "app_store"
            assert "raw_text" in r
            assert "clean_text" in r
            assert "author_id_hash" in r
            assert "timestamp" in r
            assert "thread_url" in r
            assert r["thread_url"].startswith("http")
