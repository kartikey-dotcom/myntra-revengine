"""Deterministic Zero-Monetary Rule Filter and Audit Engine."""

import re
from typing import Optional, Tuple
from src.classification.taxonomy import ClassificationResult, CognitiveCategory


class ZeroMonetaryFilter:
    """Enforces the strict Zero-Monetary Incentives rule via deterministic regex and classification checks."""

    # Forbidden monetary patterns (prices, discounts, sales, coupons, cashback)
    MONETARY_PATTERNS = [
        r"(?:₹|\brs\.?|\binr\b)\s*\d+",                   # e.g. ₹2000, Rs 500, INR 1200
        r"\b(?:discount|discounted|discounts)\b",          # discount terms
        r"\b(?:coupon|coupons|promo\s*code|voucher)\b",     # coupons
        r"\b(?:cashback|bank\s*offer|card\s*offer)\b",     # card/bank cashback
        r"\b(?:price\s*drop|price\s*cut|expensive|cheap|costly|pricey)\b", # price dynamics
        r"\b(?:bbd|eoss|big\s*fashion\s*festival|clearance\s*sale|festive\s*sale|sale\s*event)\b", # sale events
        r"\b\d+%\s*(?:off|instant\s*discount)\b",          # percentage off
    ]

    def __init__(self):
        self.compiled_patterns = [re.compile(p, re.IGNORECASE) for p in self.MONETARY_PATTERNS]

    def contains_monetary_pollution(self, text: str) -> Tuple[bool, Optional[str]]:
        """Checks if text contains any forbidden monetary terms."""
        if not text:
            return False, None

        for pattern in self.compiled_patterns:
            match = pattern.search(text)
            if match:
                return True, match.group(0)

        return False, None

    def should_purge_record(self, classification: ClassificationResult, raw_text: str) -> Tuple[bool, str]:
        """
        Determines whether a classified record should be purged from non-monetary analytics.
        Returns (should_purge, reason).
        """
        # Tier 1: Model classified as Monetary_Wait
        if classification.primary_category == CognitiveCategory.MONETARY_WAIT:
            return True, "Classified as Monetary_Wait by Cognitive Engine"

        # Tier 2: Deterministic Regex Filter
        has_pollution, matched_token = self.contains_monetary_pollution(raw_text)
        if has_pollution:
            return True, f"Regex detected monetary pollution token: '{matched_token}'"

        return False, "Passed Zero-Monetary Filter"
