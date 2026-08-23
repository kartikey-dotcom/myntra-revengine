"""Pipeline runner for Phase 1: Multi-Channel Data Ingestion.

Executes live scraping across Reddit, YouTube, and Google Play Store.
Enforces zero synthetic text fallback.
"""

import io
import sys
import uuid
from datetime import datetime
from pathlib import Path

# Reconfigure stdout/stderr for UTF-8 on Windows environments
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.config import TARGET_RECORDS
from src.database.db_manager import DatabaseManager
from src.ingestion.reddit_scraper import RedditScraper
from src.ingestion.youtube_scraper import YouTubeScraper
from src.ingestion.app_store_scraper import AppStoreScraper


def run_pipeline(reset: bool = False):
    print("=" * 70)
    print(">> Starting Phase 1: Live Multi-Channel Data Ingestion Pipeline")
    print(">> Strict Traceability: Zero Synthetic Fallback Enforced")
    print("=" * 70)

    db = DatabaseManager()
    if reset:
        print("[*] Reset flag passed: Dropping and re-creating fresh database schema...")
        db.reset_db()
        print("   [+] Fresh schema initialized.\n")

    batch_id = f"batch_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    print(f"[*] Initialized Ingestion Batch ID: {batch_id}\n")

    # 1. Scrape Reddit
    print(f"[*] [1/3] Scraping Reddit communities (Target: {TARGET_RECORDS['reddit']} real records)...")
    db.create_batch(f"{batch_id}_reddit", "reddit")
    reddit_scraper = RedditScraper()
    reddit_records = reddit_scraper.scrape(target_count=TARGET_RECORDS["reddit"], batch_id=batch_id)
    inserted_reddit = db.insert_feedback_records(reddit_records)
    db.complete_batch(f"{batch_id}_reddit", inserted_reddit)
    print(f"   [+] Genuine Reddit records collected: {len(reddit_records)} | Inserted: {inserted_reddit}\n")

    # 2. Scrape YouTube
    print(f"[*] [2/3] Scraping YouTube fashion hauls (Target: {TARGET_RECORDS['youtube']} real records)...")
    db.create_batch(f"{batch_id}_youtube", "youtube")
    yt_scraper = YouTubeScraper()
    yt_records = yt_scraper.scrape(target_count=TARGET_RECORDS["youtube"], batch_id=batch_id)
    inserted_yt = db.insert_feedback_records(yt_records)
    db.complete_batch(f"{batch_id}_youtube", inserted_yt)
    print(f"   [+] Genuine YouTube records collected: {len(yt_records)} | Inserted: {inserted_yt}\n")

    # 3. Scrape App Store
    print(f"[*] [3/3] Scraping Google Play reviews (Target: {TARGET_RECORDS['app_store']} real records)...")
    db.create_batch(f"{batch_id}_app_store", "app_store")
    app_scraper = AppStoreScraper()
    app_records = app_scraper.scrape(target_count=TARGET_RECORDS["app_store"], batch_id=batch_id)
    inserted_app = db.insert_feedback_records(app_records)
    db.complete_batch(f"{batch_id}_app_store", inserted_app)
    print(f"   [+] Genuine App Store records collected: {len(app_records)} | Inserted: {inserted_app}\n")

    # Summary Report
    print("=" * 70)
    print(">> Phase 1 Ingestion Data Lake Summary Report")
    print("=" * 70)
    channel_counts = db.get_record_counts_by_channel()
    total_records = db.get_total_records()

    for ch, count in channel_counts.items():
        print(f"  • Channel: {ch:<12} | Genuine Records: {count:>6}")
    print("-" * 70)
    print(f"  Total Verified Records in Data Lake: {total_records}")
    print(f"  Database Location: {db.db_path}")
    print("=" * 70)


if __name__ == "__main__":
    reset_db = "--reset" in sys.argv
    run_pipeline(reset=reset_db)
