"""CLI script to run Phase 4 Quality Assurance & Compliance Audits."""

import io
import sys
from pathlib import Path

# Reconfigure stdout/stderr for UTF-8 on Windows environments
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.qa.audit_engine import AuditEngine


def run_qa_audit():
    print("=" * 75)
    print(">> Starting Phase 4: Quality Assurance & Compliance Audit")
    print("=" * 75)

    engine = AuditEngine()
    report = engine.generate_full_audit_report()

    purity = report["zero_monetary_purity"]
    hallucination = report["hallucination_verification"]
    confidence = report["confidence_distribution"]

    print(f"[*] Total Records Audited: {report['total_classified_records']}")
    print("-" * 75)

    # 1. Zero-Monetary Purity Audit
    print("1. ZERO-MONETARY DATA PURITY AUDIT:")
    print(f"   • Status:             [{purity['status']}]")
    print(f"   • Data Purity Rate:   {purity['purity_rate']}% (Target: 100.0%)")
    print(f"   • Price Leaks Found:  {purity['polluted_count']} records")
    if purity["polluted_count"] == 0:
        print("   ✅ Zero monetary pollution detected. Core constraint strictly enforced.")
    else:
        print(f"   ❌ Warning: {purity['polluted_count']} price records detected!")

    print("-" * 75)

    # 2. LLM Hallucination Verification
    print("2. LLM HALLUCINATION & QUOTE CONTAINMENT AUDIT:")
    print(f"   • Status:             [{hallucination['status']}]")
    print(f"   • Quote Match Rate:   {hallucination['containment_rate']}% (Target: > 95.0%)")
    print(f"   • Hallucinated Quotes:{hallucination['hallucinated_count']} records")
    if hallucination["containment_rate"] >= 95.0:
        print("   ✅ Verbatim quotes faithfully extracted from raw customer feedback.")
    else:
        print("   ❌ Warning: High hallucination rate detected in extracted quotes.")

    print("-" * 75)

    # 3. Model Confidence Statistics
    print("3. MODEL CONFIDENCE & STATISTICAL METRICS:")
    print(f"   • Mean Confidence:    {confidence['mean_confidence']:.2f}")
    print(f"   • High-Conf (>=0.85): {confidence['high_confidence_pct']}% of records")
    print(f"   • Min Confidence:     {confidence['min_confidence']:.2f}")

    print("=" * 75)
    if report["overall_status"] == "PASSED":
        print("🏆 OVERALL QA AUDIT STATUS: PASSED (Ready for PM Handover)")
    else:
        print("⚠️ OVERALL QA AUDIT STATUS: FAILED")
    print("=" * 75)


if __name__ == "__main__":
    run_qa_audit()
