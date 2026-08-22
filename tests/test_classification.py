"""Unit and Integration Tests for Phase 2 Cognitive Taxonomy & Classification."""

import gc
import tempfile
from pathlib import Path
import pytest

from src.classification.taxonomy import CognitiveCategory, ClassificationResult
from src.classification.zero_monetary_filter import ZeroMonetaryFilter
from src.classification.llm_classifier import LLMCognitiveClassifier
from src.database.db_manager import DatabaseManager


@pytest.fixture
def temp_db():
    """Creates an isolated temporary SQLite database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        tmp_path = Path(tmp.name)
    db = DatabaseManager(db_path=tmp_path)
    yield db
    gc.collect()
    try:
        if tmp_path.exists():
            tmp_path.unlink()
    except Exception:
        pass


class TestCognitiveTaxonomy:
    def test_valid_classification_model(self):
        res = ClassificationResult(
            primary_category=CognitiveCategory.STYLING_ISOLATION,
            confidence_score=0.945,
            verbatim_quote="no idea what top or shoes to wear with it",
            decision_barrier_summary="Shopper cannot find matching top or footwear for skirt.",
            secondary_category=None,
        )
        assert res.primary_category == "Styling_Isolation"
        assert res.confidence_score == 0.945
        assert "no idea" in res.verbatim_quote

    def test_invalid_category_fails(self):
        with pytest.raises(Exception):
            ClassificationResult(
                primary_category="Invalid_Category_Name",
                confidence_score=0.5,
                verbatim_quote="quote",
                decision_barrier_summary="summary",
            )


class TestZeroMonetaryFilter:
    def test_detects_price_and_discount(self):
        f = ZeroMonetaryFilter()
        polluted_samples = [
            "Waiting for price drop to ₹1500",
            "Is there any coupon code for 500 off?",
            "Will buy during Big Fashion Festival sale",
            "Waiting for 10% instant bank discount on card",
            "Too expensive at INR 4500",
        ]
        for s in polluted_samples:
            is_polluted, token = f.contains_monetary_pollution(s)
            assert is_polluted is True, f"Failed to detect monetary pollution in: '{s}'"
            assert token is not None

    def test_clean_non_monetary_passes(self):
        f = ZeroMonetaryFilter()
        clean_samples = [
            "Love the cut of this midi skirt but don't know how to style it.",
            "I am 5'3 and curvy, worried the waist will gap on these jeans.",
            "Nowhere to wear a backless cocktail dress when friends prefer casual cafes.",
            "Search shows 40 duplicate listings of the same kurti.",
        ]
        for s in clean_samples:
            is_polluted, _ = f.contains_monetary_pollution(s)
            assert is_polluted is False, f"False positive monetary pollution in: '{s}'"


class TestLLMClassifier:
    def test_styling_isolation_classification(self):
        classifier = LLMCognitiveClassifier()
        text = "I have this pleated skirt in my wishlist, but no idea what top or shoes to wear with it."
        res = classifier.classify_text(text)
        assert res.primary_category == CognitiveCategory.STYLING_ISOLATION
        assert res.confidence_score >= 0.85
        assert res.verbatim_quote in text

    def test_fit_ambiguity_classification(self):
        classifier = LLMCognitiveClassifier()
        text = "I am 5'2 and have broad ribcage, worried the size S will be suffocating and too tight."
        res = classifier.classify_text(text)
        assert res.primary_category == CognitiveCategory.FIT_BODY_AMBIGUITY
        assert res.confidence_score >= 0.85
        assert res.verbatim_quote in text

    def test_monetary_wait_classification(self):
        classifier = LLMCognitiveClassifier()
        text = "Waiting for upcoming BBD sale to see if the price drops below 2000 rupees."
        res = classifier.classify_text(text)
        assert res.primary_category == CognitiveCategory.MONETARY_WAIT
        assert res.confidence_score >= 0.95


class TestClassificationDatabasePersistence:
    def test_insert_classified_and_purge_log(self, temp_db):
        classifier = LLMCognitiveClassifier()
        sample_records = [
            {
                "id": "rec_001",
                "source_channel": "reddit",
                "timestamp": "2026-08-20T12:00:00",
                "clean_text": "Need styling advice on how to pair this olive green jacket.",
            },
            {
                "id": "rec_002",
                "source_channel": "reddit",
                "timestamp": "2026-08-20T12:00:00",
                "clean_text": "Waiting for 20% discount coupon code during sale.",
            },
        ]
        results = classifier.classify_batch(sample_records)
        valid = [r for r in results if not r["should_purge"]]
        purged = [r for r in results if r["should_purge"]]

        inserted_valid = temp_db.insert_classified_records(valid, "batch_test")
        logged_purged = temp_db.insert_monetary_purge_logs(purged, "batch_test")

        assert inserted_valid == 1
        assert logged_purged == 1

        metrics = temp_db.get_classification_metrics()
        assert metrics["total_classified"] == 1
        assert metrics["total_purged"] == 1
        assert CognitiveCategory.STYLING_ISOLATION.value in metrics["categories"]
