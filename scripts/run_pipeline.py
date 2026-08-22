"""Master unified pipeline runner for Myntra Wishlist Discovery Engine."""

import io
import sys
from pathlib import Path

# Reconfigure stdout/stderr for UTF-8 on Windows environments
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from scripts.run_ingestion import run_pipeline as run_ingestion_step
from scripts.run_classification import run_batch_classification as run_classification_step
from scripts.run_audit import run_qa_audit as run_audit_step


def main():
    print("=" * 80)
    print("🌟 MYNTRA WISHLIST AI DISCOVERY & INTELLIGENCE ENGINE: MASTER PIPELINE")
    print("=" * 80)

    # 1. Ingestion
    print("\n>>> [STEP 1/3] MULTI-CHANNEL DATA INGESTION")
    run_ingestion_step()

    # 2. Classification
    print("\n>>> [STEP 2/3] COGNITIVE TAXONOMY & LLM BATCH CLASSIFICATION")
    run_classification_step()

    # 3. QA Audit
    print("\n>>> [STEP 3/3] QUALITY ASSURANCE & ZERO-MONETARY PURITY AUDIT")
    run_audit_step()

    print("\n" + "=" * 80)
    print("🎉 ALL PIPELINE PHASES COMPLETED SUCCESSFULLY!")
    print("   To launch the Streamlit Executive Dashboard, run:")
    print("   👉 streamlit run streamlit_app.py")
    print("=" * 80)


if __name__ == "__main__":
    main()
