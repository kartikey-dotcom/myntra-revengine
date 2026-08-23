"""Pipeline runner for Phase 2: Cognitive Taxonomy & LLM Batch Processing.

Applies:
1. Explicit Relevance Filter (Wishlist & Purchase Hesitation).
2. Zero-Monetary Purge Policy.
3. Per-Record Semantic Friction Categorization.
4. Independent Evidence-Grounded Extraction of User_Intent and Detected_Off_Platform_Action (Zero Lookups).
"""

import io
import random
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

from src.database.db_manager import DatabaseManager
from src.classification.llm_classifier import LLMCognitiveClassifier


def run_batch_classification():
    print("=" * 75)
    print(">> Starting Phase 2: Cognitive Taxonomy & Relevance-Filtered Batch Processing")
    print("=" * 75)

    db = DatabaseManager()
    classifier = LLMCognitiveClassifier()
    batch_id = f"cls_batch_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"

    print(f"[*] Initialized Classification Batch ID: {batch_id}")

    # Fetch raw data lake records
    raw_records = db.get_raw_records()
    total_raw = len(raw_records)
    print(f"[*] Loaded {total_raw} raw records from Data Lake\n")

    if total_raw == 0:
        print("[!] No raw records found in Data Lake. Please run `python scripts/run_ingestion.py` first.")
        return

    # Clear previous classification records for fresh clean state
    with db.get_connection() as conn:
        c = conn.cursor()
        c.execute("DELETE FROM classified_feedback;")
        c.execute("DELETE FROM monetary_purge_log;")
        c.execute("DELETE FROM relevance_exclusion_log;")
        conn.commit()

    # Process batch
    valid_classified = []
    purged_monetary = []
    excluded_irrelevant = []

    print(f"[*] Executing Relevance Filter & Cognitive Taxonomy Classification...")
    results = classifier.classify_batch(raw_records)

    for res in results:
        if not res.get("is_relevant", True):
            excluded_irrelevant.append(res)
        elif res.get("should_purge", False):
            purged_monetary.append(res)
        else:
            valid_classified.append(res)

    print(f"   [+] Processed: {total_raw} total records")
    print(f"   [+] Relevant Non-Monetary Friction: {len(valid_classified)}")
    print(f"   [+] Monetary Data Purged:            {len(purged_monetary)}")
    print(f"   [+] Irrelevant Records Excluded:    {len(excluded_irrelevant)}")

    # Persist to Database
    print("\n[*] Writing records to PostgreSQL/SQLite tables...")
    inserted_valid = db.insert_classified_records(valid_classified, batch_id)
    logged_purged = db.insert_monetary_purge_logs(purged_monetary, batch_id)
    logged_excluded = db.insert_relevance_exclusions(excluded_irrelevant, batch_id)

    print(f"   [+] Persisted {inserted_valid} records to 'classified_feedback'")
    print(f"   [+] Logged {logged_purged} records to 'monetary_purge_log'")
    print(f"   [+] Logged {logged_excluded} records to 'relevance_exclusion_log'")

    # Relevance Rate Report
    relevance_rate = (len(valid_classified) / total_raw * 100) if total_raw else 0
    print("\n" + "=" * 75)
    print("📊 RELEVANCE & CLASSIFICATION AUDIT REPORT")
    print("=" * 75)
    print(f"  Total Records Analyzed:     {total_raw}")
    print(f"  Wishlist-Relevant Records:  {len(valid_classified)} ({relevance_rate:.1f}%)")
    print(f"  Excluded (Generic/Noise):   {len(excluded_irrelevant)} ({len(excluded_irrelevant)/total_raw*100:.1f}%)")
    print(f"  Purged (Monetary/Discounts):{len(purged_monetary)} ({len(purged_monetary)/total_raw*100:.1f}%)")
    print("-" * 75)

    # Sample Excluded Records
    print("🔍 Sample EXCLUDED Records (Filter Judgment):")
    for r in random.sample(excluded_irrelevant, min(3, len(excluded_irrelevant))):
        print(f"  ❌ \"{r['clean_text'][:80]}...\"")
        print(f"     Reason: {r.get('relevance_reason')}\n")

    # Sample Relevant Records
    if valid_classified:
        print("🔍 Sample RELEVANT Classified Records:")
        for r in random.sample(valid_classified, min(3, len(valid_classified))):
            print(f"  ✅ \"{r['clean_text'][:80]}...\"")
            print(f"     Category: {r.get('primary_category')} | Score: {r.get('confidence_score')}")
            print(f"     Intent: {r.get('user_intent')} | Off-Platform: {r.get('detected_off_platform_action')}\n")

    print("=" * 75)
    print("[SUCCESS] Phase 2 Relevance-Filtered Batch Classification Completed!")


if __name__ == "__main__":
    run_batch_classification()
