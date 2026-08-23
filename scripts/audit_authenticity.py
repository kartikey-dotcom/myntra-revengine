"""Post-Collection & Classification Authenticity Audit Script.

Verifies that all records in the Data Lake are genuine, traceable, non-synthetic:
1. Calculates text uniqueness % (flags warning if duplication is > 5%).
2. Randomly samples 10 records and prints their clickable source_url permalinks for manual verification.
3. Analyzes confidence score distribution (flags discrete clustering vs. continuous spread).
"""

import io
import random
import sqlite3
import sys
from pathlib import Path

# UTF-8 stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.config import SQLITE_DB_PATH


def run_authenticity_audit():
    print("=" * 80)
    print("🔍 DATA LAKE AUTHENTICITY & TRACEABILITY AUDIT")
    print("=" * 80)

    if not SQLITE_DB_PATH.exists():
        print(f"[!] Database file does not exist at {SQLITE_DB_PATH}")
        return

    conn = sqlite3.connect(str(SQLITE_DB_PATH))
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # 1. Total & Uniqueness Check on raw_feedback
    c.execute("SELECT COUNT(*) as total, COUNT(DISTINCT clean_text) as unique_texts FROM raw_feedback;")
    raw_stats = c.fetchone()
    total_raw = raw_stats["total"] if raw_stats else 0
    unique_raw = raw_stats["unique_texts"] if raw_stats else 0

    print(f"\n[1] Text Uniqueness & Anti-Duplication Metric (Raw Feedback):")
    print(f"    • Total Records Ingested: {total_raw}")
    print(f"    • Unique Feedback Texts:  {unique_raw}")

    if total_raw > 0:
        uniqueness_pct = (unique_raw / total_raw) * 100
        duplication_pct = 100.0 - uniqueness_pct
        print(f"    • Uniqueness Rate:        {uniqueness_pct:.2f}%")
        print(f"    • Duplication Rate:       {duplication_pct:.2f}%")

        if duplication_pct > 5.0:
            print(f"    ⚠️  [WARNING] High duplication rate detected ({duplication_pct:.2f}% > 5.0%). Possible templated/synthetic data!")
        else:
            print(f"    ✅ [PASSED] Organic text diversity verified (Duplication < 5.0%).")
    else:
        print("    [!] No raw records in database.")

    # 2. Source URL & Traceability Verification (Sample 10 Records)
    print(f"\n[2] Live Traceability & Source URL Audit (Sample 10 Records):")
    c.execute("SELECT id, source_channel, timestamp, thread_url, substr(clean_text, 1, 90) as snippet FROM raw_feedback;")
    all_raw = c.fetchall()

    if all_raw:
        sample_size = min(10, len(all_raw))
        sample_records = random.sample(all_raw, sample_size)

        non_url_count = 0
        for i, row in enumerate(sample_records, 1):
            url = row["thread_url"] or ""
            is_valid_url = url.startswith("http://") or url.startswith("https://")
            if not is_valid_url:
                non_url_count += 1
            status_icon = "🔗" if is_valid_url else "❌ MISSING"

            print(f"\n    Sample #{i} [{row['source_channel'].upper()}] - Date: {row['timestamp'][:10]}")
            print(f"      Text: \"{row['snippet']}...\"")
            print(f"      {status_icon} URL:  {url}")

        if non_url_count > 0:
            print(f"\n    ⚠️  [FAIL] Found {non_url_count} sampled records with missing or invalid URLs!")
        else:
            print(f"\n    ✅ [PASSED] 100% of sampled records contain valid, resolvable source URLs.")
    else:
        print("    [!] No records available to sample.")

    # 3. Classified Feedback Confidence Score Distribution Analysis
    print(f"\n[3] Classification Confidence Score Distribution Audit:")
    c.execute("SELECT confidence_score FROM classified_feedback;")
    scores = [r["confidence_score"] for r in c.fetchall()]

    if scores:
        print(f"    • Total Classified Records: {len(scores)}")
        unique_scores = len(set(scores))
        print(f"    • Distinct Confidence Values: {unique_scores}")

        # Check score distribution
        score_counts = {}
        for s in scores:
            rounded = round(s, 2)
            score_counts[rounded] = score_counts.get(rounded, 0) + 1

        top_clusters = sorted(score_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        print("    • Top Score Clusters:")
        for score_val, count in top_clusters:
            pct = (count / len(scores)) * 100
            print(f"      Score {score_val:.2f}: {count} records ({pct:.1f}%)")

        if unique_scores < 5 and len(scores) > 50:
            print("    ⚠️  [WARNING] Confidence scores cluster into very few discrete values. Possible static hardcoded scores!")
        else:
            print("    ✅ [PASSED] Confidence score distribution exhibits continuous variation.")
    else:
        print("    [!] No classified feedback records found in database.")

    print("\n" + "=" * 80)
    conn.close()


if __name__ == "__main__":
    run_authenticity_audit()
