"""Configuration settings for Myntra Wishlist AI Discovery & Intelligence Engine."""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Ensure data directories exist
DATA_DIR.mkdir(exist_ok=True)
RAW_DATA_DIR.mkdir(exist_ok=True)
PROCESSED_DATA_DIR.mkdir(exist_ok=True)

# Database Configuration (SQLite default for zero-setup portability, PostgreSQL compatible)
SQLITE_DB_PATH = DATA_DIR / "myntra_wishlist_lake.db"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{SQLITE_DB_PATH}")

# Target Ingestion Volumes (Targeting 4,300 to comfortably guarantee 4,000+ unique records post-dedup)
TARGET_RECORDS = {
    "reddit": 1750,
    "youtube": 1350,
    "app_store": 1350,
}

# Target Keywords for Ingestion
HIGH_INTENT_KEYWORDS = [
    "wishlist",
    "cart",
    "hesitate",
    "hesitation",
    "styling",
    "style",
    "fit",
    "sizing",
    "size",
    "confused",
    "quality",
    "fabric",
    "look",
    "wardrobe",
    "return",
    "dilemma",
    "clutter",
    "occasion",
]

# Targeted Communities
REDDIT_SUBREDDITS = [
    "IndianFashionAddicts",
    "TwoXIndia",
    "DesiFragranceAddicts",
    "IndiaThriftStore",
    "IndianBeautyDeals",
]

# Target YouTube Search Queries
YOUTUBE_QUERIES = [
    "Myntra fashion haul honest review",
    "Myntra try on haul styling tips",
    "Myntra clothes fit sizing review",
    "Myntra wishlist vs reality",
    "Myntra party wear styling dilemma",
]

# API Credentials (Optional - Graceful fallback if missing)
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "MyntraWishlistBot/1.0")

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
