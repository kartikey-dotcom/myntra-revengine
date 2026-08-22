"""Unit and Integration Tests for Phase 4 QA Audits."""

import pandas as pd
import pytest

from src.qa.audit_engine import AuditEngine
from src.database.db_manager import DatabaseManager


class TestQAAudits:
    def test_zero_monetary_purity_clean(self):
        engine = AuditEngine()
        clean_df = pd.DataFrame([
            {"id": "1", "clean_text": "Need styling advice on pairing this green pleated skirt."},
            {"id": "2", "clean_text": "I am 5'3, worried the waist on these trousers will gap."},
        ])
        res = engine.audit_zero_monetary_purity(clean_df)
        assert res["status"] == "PASSED"
        assert res["polluted_count"] == 0
        assert res["purity_rate"] == 100.0

    def test_zero_monetary_purity_polluted_detection(self):
        engine = AuditEngine()
        polluted_df = pd.DataFrame([
            {"id": "1", "clean_text": "Waiting for ₹500 discount coupon code during BBD sale."},
            {"id": "2", "clean_text": "Need styling advice on pairing this skirt."},
        ])
        res = engine.audit_zero_monetary_purity(polluted_df)
        assert res["status"] == "FAILED"
        assert res["polluted_count"] == 1
        assert res["purity_rate"] == 50.0

    def test_hallucination_containment_audit(self):
        engine = AuditEngine()
        raw_df = pd.DataFrame([
            {"id": "r1", "clean_text": "I literally have no idea what top or footwear will go with this olive skirt."},
        ])
        classified_df = pd.DataFrame([
            {
                "id": "c1",
                "raw_feedback_id": "r1",
                "clean_text": "I literally have no idea what top or footwear will go with this olive skirt.",
                "verbatim_quote": "no idea what top or footwear will go with this olive skirt",
            }
        ])
        res = engine.audit_hallucinations(classified_df, raw_df)
        assert res["status"] == "PASSED"
        assert res["hallucinated_count"] == 0
        assert res["containment_rate"] == 100.0

    def test_live_data_lake_audit_compliance(self):
        db = DatabaseManager()
        engine = AuditEngine(db_manager=db)
        report = engine.generate_full_audit_report()

        assert report["overall_status"] == "PASSED"
        assert report["zero_monetary_purity"]["purity_rate"] == 100.0
        assert report["zero_monetary_purity"]["polluted_count"] == 0
        assert report["hallucination_verification"]["containment_rate"] >= 95.0
