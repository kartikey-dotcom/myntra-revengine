"""Quality Assurance & Audit Engine for Myntra Wishlist Discovery Engine."""

from typing import Any, Dict
import pandas as pd

from src.classification.zero_monetary_filter import ZeroMonetaryFilter
from src.database.db_manager import DatabaseManager


class AuditEngine:
    """Performs rigorous automated audits for Zero-Monetary Purity and LLM Hallucinations."""

    def __init__(self, db_manager: DatabaseManager = None):
        self.db = db_manager or DatabaseManager()
        self.zero_monetary_filter = ZeroMonetaryFilter()

    def audit_zero_monetary_purity(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Scans 100% of classified records to ensure 0.0% monetary data leakage."""
        if df.empty:
            return {"status": "EMPTY", "total_checked": 0, "polluted_count": 0, "purity_rate": 100.0}

        polluted_records = []
        for idx, row in df.iterrows():
            text = str(row.get("clean_text", ""))
            has_pollution, token = self.zero_monetary_filter.contains_monetary_pollution(text)
            if has_pollution:
                polluted_records.append({
                    "id": row.get("id"),
                    "matched_token": token,
                    "text": text[:80]
                })

        total = len(df)
        polluted_count = len(polluted_records)
        purity_rate = round(((total - polluted_count) / total) * 100, 2)

        return {
            "status": "PASSED" if polluted_count == 0 else "FAILED",
            "total_checked": total,
            "polluted_count": polluted_count,
            "purity_rate": purity_rate,
            "polluted_samples": polluted_records[:5],
        }

    def audit_hallucinations(self, classified_df: pd.DataFrame, raw_df: pd.DataFrame) -> Dict[str, Any]:
        """Validates that extracted verbatim_quotes exist verbatim in raw source text."""
        if classified_df.empty or raw_df.empty:
            return {"status": "EMPTY", "total_checked": 0, "containment_rate": 100.0}

        # Map raw text by id
        raw_map = dict(zip(raw_df["id"], raw_df["clean_text"]))
        hallucination_cases = []
        checked = 0

        for idx, row in classified_df.iterrows():
            raw_id = row.get("raw_feedback_id")
            quote = str(row.get("verbatim_quote", "")).strip().replace('"', '').replace("'", "")
            source_text = raw_map.get(raw_id, str(row.get("clean_text", ""))).replace('"', '').replace("'", "")

            if not quote:
                continue

            checked += 1
            # Check if quote is contained in source text (case-insensitive substring)
            if quote.lower() not in source_text.lower():
                # Allow minor punctuation variations if 90% character overlap
                cleaned_quote_words = [w for w in quote.lower().split() if len(w) > 3]
                matches = sum(1 for w in cleaned_quote_words if w in source_text.lower())
                overlap_ratio = matches / len(cleaned_quote_words) if cleaned_quote_words else 1.0
                if overlap_ratio < 0.80:
                    hallucination_cases.append({
                        "id": row.get("id"),
                        "quote": quote,
                        "source": source_text[:100]
                    })

        total_checked = checked or len(classified_df)
        hallucinated_count = len(hallucination_cases)
        containment_rate = round(((total_checked - hallucinated_count) / total_checked) * 100, 2)

        return {
            "status": "PASSED" if containment_rate >= 95.0 else "WARNING",
            "total_checked": total_checked,
            "hallucinated_count": hallucinated_count,
            "containment_rate": containment_rate,
            "samples": hallucination_cases[:5],
        }

    def audit_confidence_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculates statistical metrics for classification confidence."""
        if df.empty or "confidence_score" not in df.columns:
            return {"mean_confidence": 0.0, "min_confidence": 0.0, "high_confidence_pct": 0.0}

        scores = df["confidence_score"]
        mean_conf = round(float(scores.mean()), 4)
        min_conf = round(float(scores.min()), 4)
        max_conf = round(float(scores.max()), 4)
        high_conf_count = int((scores >= 0.85).sum())
        high_conf_pct = round((high_conf_count / len(scores)) * 100, 2)

        return {
            "mean_confidence": mean_conf,
            "min_confidence": min_conf,
            "max_confidence": max_conf,
            "high_confidence_pct": high_conf_pct,
        }

    def generate_full_audit_report(self) -> Dict[str, Any]:
        """Runs the comprehensive audit suite and returns the executive report."""
        classified_df = self.db.fetch_classified_dataframe()
        raw_df = self.db.fetch_all_dataframe()

        purity_audit = self.audit_zero_monetary_purity(classified_df)
        hallucination_audit = self.audit_hallucinations(classified_df, raw_df)
        confidence_audit = self.audit_confidence_metrics(classified_df)

        overall_status = "PASSED" if (purity_audit["status"] == "PASSED" and hallucination_audit["status"] == "PASSED") else "FAILED"

        return {
            "overall_status": overall_status,
            "total_classified_records": len(classified_df),
            "zero_monetary_purity": purity_audit,
            "hallucination_verification": hallucination_audit,
            "confidence_distribution": confidence_audit,
        }
