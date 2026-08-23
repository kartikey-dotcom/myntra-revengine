"""Relevance Filter for Wishlist-to-Purchase Non-Conversion Research.

Evaluates raw customer feedback to determine whether it specifically pertains to:
1. Saving, wishlisting, shortlisting, or carting products.
2. Hesitation, postponement, or deciding not to purchase saved items.
3. Non-monetary friction: Styling uncertainty, fit/body ambiguity, catalog clutter, or occasion disconnect.

Excludes generic post-purchase delivery issues, technical app bugs, refund/payment complaints,
or generic praise/criticism with no purchase-decision content.
"""

import re
from typing import Dict, Optional, Tuple


class RelevanceFilter:
    """Evaluates whether feedback contains signals of wishlist/shopping decision friction."""

    # Explicit decision / pre-purchase / hesitation / sizing / styling / discovery markers
    DECISION_KEYWORDS = [
        "wishlist", "wishlisted", "wish listing", "shortlist", "shortlisted",
        "save for later", "saved", "saving", "bag", "cart", "basket",
        "hesitate", "hesitation", "hesitating", "dilemma", "confused", "confusion",
        "buy", "buying", "purchase", "purchasing", "order", "ordering", "checkout",
        "style", "styling", "pair", "pairing", "match", "matching", "outfit", "wardrobe",
        "fit", "fitting", "sizing", "size", "size chart", "measure", "measurement",
        "tight", "loose", "waist", "bust", "chest", "inseam", "petite", "broad",
        "clutter", "duplicate", "identical", "search", "filter", "filters", "compare", "comparing",
        "studio photo", "model", "lighting", "color", "fabric", "material", "quality",
        "occasion", "event", "wear", "wedding", "party", "office", "formal", "casual",
        "return", "returns", "exchange", "exchanging"
    ]

    # Explicit post-purchase / operational noise markers (irrelevant if unaccompanied by decision context)
    IRRELEVANT_PATTERNS = [
        (r"otp", "Account login / OTP authentication issue with zero purchase decision context."),
        (r"(delivery boy|delivery person|delivery agent|courier guy)", "Post-purchase delivery personnel behavior issue with zero purchase decision context."),
        (r"(refund not received|refund credited|bank account|payment deduction|upi failed)", "Post-purchase transaction / payment gateway error with zero product evaluation context."),
        (r"^(good app|nice app|bad app|worst app|superb app|fraud company|fake app)[\.!\s]*$", "Generic sentiment without actionable purchase decision or wishlist context."),
        (r"^(update|version|bug|lag|crashing|crash|slow)[\.!\s]*$", "Pure technical app performance / release bug with zero shopping decision context.")
    ]

    def evaluate(self, text: str) -> Tuple[bool, str]:
        """Evaluates a raw feedback text and returns (is_relevant: bool, reason: str)."""
        if not text or len(text.strip()) < 15:
            return False, "Feedback text is too short (< 15 characters) to establish decision context."

        clean = text.strip()
        lower = clean.lower()

        # Check for pure generic/operational patterns first
        for pattern, reason in self.IRRELEVANT_PATTERNS:
            if re.search(pattern, lower) and not any(k in lower for k in ["wishlist", "cart", "size", "fit", "style", "dress", "pair", "clutter"]):
                return False, reason

        # Check for high-intent wishlist & save behaviors
        if any(w in lower for w in ["wishlist", "wishlisted", "save for later", "saved in", "saved this", "in my cart", "in my bag", "carted"]):
            return True, "Contains explicit mention of wishlist, saved items, or carted products."

        # Check for pre-purchase styling & outfit pairing hesitation
        if any(s in lower for s in ["how to style", "what to wear with", "pair with", "matching with", "styling advice", "complete the look", "outfit combination"]):
            return True, "Contains pre-purchase styling isolation or outfit coordination dilemma."

        # Check for sizing, body dimension, or fit ambiguity
        if any(f in lower for f in ["size chart", "sizing issue", "runs small", "runs large", "size discrepancy", "model measurement", "waist size", "chest tight", "loose fit", "tight fit", "body shape"]):
            return True, "Contains fit, sizing chart, or body proportion hesitation signal."

        # Check for catalog search, photo lighting, or comparison fatigue
        if any(c in lower for c in ["search duplicate", "identical product", "catalog clutter", "studio photo misleading", "color different in real", "compare mode", "too many copies"]):
            return True, "Contains catalog clutter, studio lighting discrepancy, or choice comparison friction."

        # Check for return fear / hesitation impacting purchasing
        if any(r in lower for r in ["hesitate to order", "scared to buy", "afraid to purchase", "return process hectic", "avoid return", "return hassle"]):
            return True, "Contains checkout hesitation driven by return friction or product uncertainty."

        # Broader combined decision + fashion item context
        has_decision = any(k in lower for k in ["size", "fit", "fitting", "fabric", "material", "quality", "style", "dress", "shirt", "shoes", "kurti", "jeans", "color", "return"])
        has_context = any(c in lower for c in ["confused", "problem", "issue", "poor", "worst", "not good", "bad", "heavy", "transparent", "expensive", "different", "expect"])

        if has_decision and has_context and not re.search(r"(delivery|refund|boy|courier|login|otp)", lower):
            return True, "Discusses garment attributes (size, fit, fabric, returnability) directly impacting purchase confidence."

        # If it's a delivery or refund complaint
        if any(w in lower for w in ["delivery", "delivered", "courier", "late", "delay", "shipping", "refund", "customer care", "support"]):
            return False, "Post-purchase delivery, shipping logistics, or customer service complaint with no wishlist/decision friction."

        # Generic appraisal / short comment
        return False, "Generic app feedback lacking specific purchase hesitation, sizing, styling, or wishlist behavior."
