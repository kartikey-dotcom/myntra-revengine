"""Pipeline runner for Phase 2: Cognitive Taxonomy & LLM Batch Processing."""

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

from src.database.db_manager import DatabaseManager
from src.classification.llm_classifier import LLMCognitiveClassifier


def run_batch_classification():
    print("=" * 75)
    print(">> Starting Phase 2: Cognitive Taxonomy & LLM Batch Processing")
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
        conn.commit()

    # Process in batches
    batch_size = 500
    valid_classified = []
    purged_monetary = []

    print(f"[*] Executing LLM Cognitive Classification & Zero-Monetary Filter...")
    for i in range(0, total_raw, batch_size):
        chunk = raw_records[i : i + batch_size]
        results = classifier.classify_batch(chunk)

        for res in results:
            if res["should_purge"]:
                purged_monetary.append(res)
            else:
                valid_classified.append(res)

        print(f"   Processed {min(i + batch_size, total_raw)} / {total_raw} records...", end="\r")

    print(f"\n   [+] Classification Completed: {len(valid_classified)} non-monetary | {len(purged_monetary)} monetary purged")

    # Persist to Database
    print("\n[*] Writing records to PostgreSQL/SQLite tables...")
    inserted_valid = db.insert_classified_records(valid_classified, batch_id)
    logged_purged = db.insert_monetary_purge_logs(purged_monetary, batch_id)

    print(f"   [+] Persisted {inserted_valid} records to 'classified_feedback'")
    print(f"   [+] Logged {logged_purged} purged records to 'monetary_purge_log'")

    # Generate Executive Summary Report
    metrics = db.get_classification_metrics()
    print("\n" + "=" * 75)
    print(">> Phase 2: Cognitive Friction Distribution & Executive Summary Report")
    print("=" * 75)
    print(f"  Total Raw Feedback Analyzed:  {total_raw}")
    print(f"  Non-Monetary Friction Volume: {metrics['total_classified']} ({metrics['total_classified']/total_raw*100:.1f}%)")
    print(f"  Monetary Data Purged:         {metrics['total_purged']} ({metrics['total_purged']/total_raw*100:.1f}%)")
    print("-" * 75)
    print("  Non-Monetary Cognitive Friction Breakdown:")
    for cat, count in sorted(metrics["categories"].items(), key=lambda x: x[1], reverse=True):
        pct = (count / metrics['total_classified']) * 100 if metrics['total_classified'] else 0
        print(f"    • {cat:<24}: {count:>5} records ({pct:>5.1f}%)")

    print("-" * 75)
    print("  Distribution by Source Channel:")
    for ch, count in metrics["channels"].items():
        print(f"    • {ch:<14}: {count:>5} records")

    print("=" * 75)
    print("[SUCCESS] Phase 2 LLM Batch Classification and Zero-Monetary Enforcement Completed!")


if __name__ == "__main__":
    run_batch_classification()
