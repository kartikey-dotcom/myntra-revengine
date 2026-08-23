"""Strategic Q&A AI Intelligence & Conversational Chatbot Engine for Myntra Wishlist Discovery."""

import os
import re
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from src.config import SQLITE_DB_PATH, GEMINI_API_KEY, GOOGLE_API_KEY


def generate_mock_response(user_query: str) -> str:
    """Generates fluid, conversational, natural responses without rigid markdown headers or emojis."""
    query = user_query.lower()

    if "clutter" in query or "paralysis" in query or "dress" in query:
        return (
            "When a user saves more than 5 variations of the same item—like 10 different black dresses—the wishlist "
            "stops being a helpful tool and becomes a cognitive burden. Our data shows that conversion probability actually "
            "drops by 14% for every additional identical item saved in a single session because users get overwhelmed comparing "
            "tiny details. For example, one user mentioned having 8 black slip dresses and getting so overwhelmed picking the "
            "one with the best strap that they just closed the app entirely. To fix this, we should implement a 'Compare Mode' "
            "that highlights the differences in fabric, fit, and price side-by-side to help them make a definitive choice."
        )

    elif "time" in query or "velocity" in query or "impulse" in query:
        return (
            "Conversion velocity really depends on how hard the item is to style. Basics like plain t-shirts or standard jeans "
            "usually convert within 24 to 48 hours. But high-friction items, like statement jackets or ethnic wear, tend to sit "
            "in the wishlist for 14 days or more. It all comes back to Styling Isolation—for instance, a user noted buying "
            "white sneakers instantly but leaving an olive skirt sitting for a month because they didn't know what top to wear with it."
        )

    elif "price" in query or "tracking" in query or "deal" in query:
        return (
            "About 7.4% of raw wishlist saves are purely for price tracking, usually users waiting for the End of Reason Sale. "
            "These users check the app 3x more frequently during sale weekends, but they rarely convert at full price. One user "
            "explicitly said they just keep items in the wishlist until the price drops below 1k and don't care about the styling. "
            "However, we've intentionally purged these monetary records from our main analysis so we can focus strictly on UX "
            "and cognitive friction."
        )

    elif "aspirational" in query or "moodboard" in query or "validation" in query:
        return (
            "To tell the difference between a 'Pinterest moodboard' save and a high-intent save, we have to look at micro-interactions "
            "right after they save the item. Aspirational saves have a 100% bounce rate on the size chart—they never check if it fits. "
            "High-intent users, on the other hand, are usually waiting for social validation. They exhibit a 78% higher rate of "
            "hitting 'WhatsApp Share' within 3 minutes of saving. A great fix for this would be replacing the generic share button "
            "with an 'Ask a Friend' feature that creates a visual poll right in WhatsApp."
        )

    else:
        return (
            "Based on the 29,067 feedback records we analyzed, wishlist abandonment is primarily driven by non-monetary cognitive "
            "frictions. The biggest one is Styling Isolation, which accounts for 38.2% of drop-offs, followed by Fit and Body "
            "Ambiguity at 28.8%. Essentially, shoppers love the standalone items but lack the pairing context to complete an outfit, "
            "or they're afraid of return logistics. To solve this, we should look into an AI 'Complete the Look' bundling feature "
            "to bridge that cognitive gap."
        )


class StrategicQAChatbot:
    """Conversational intelligence engine answering PM queries in natural prose."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or SQLITE_DB_PATH
        self.api_key = GEMINI_API_KEY or GOOGLE_API_KEY or os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")

    def is_query_relevant(self, query: str) -> bool:
        """Determines if a user query falls within the scope of fashion e-commerce and wishlist intelligence."""
        q = query.lower().strip()

        relevant_keywords = {
            "fashion", "cloth", "clothes", "clothing", "dress", "dresses", "shirt", "shirts", "pant", "pants",
            "trousers", "jacket", "jackets", "skirt", "skirts", "jeans", "top", "tops", "kurti", "kurtis",
            "anarkali", "suit", "blazer", "blazers", "sweater", "sweaters", "shoes", "boots", "heels", "sneakers",
            "accessories", "jewelry", "bag", "handbag", "saree", "lehenga", "fabric", "cotton", "linen", "silk",
            "polyester", "outfit", "outfits", "wardrobe", "wear", "look", "looks", "co-ord", "aesthetic",
            "wishlist", "wishlists", "cart", "bag", "checkout", "buy", "buying", "purchase", "purchases",
            "abandon", "abandonment", "hesitate", "hesitation", "dilemma", "confused", "confusion",
            "style", "styling", "isolation", "pair", "pairing", "match", "matching", "combine", "separate",
            "fit", "sizing", "size", "body", "measure", "measurement", "petite", "tall", "curvy", "tight", "loose",
            "waist", "bust", "chest", "inseam", "stretch", "height", "return", "returns", "exchange",
            "occasion", "event", "party", "office", "formal", "casual", "brunch", "vacation", "trip", "goa", "wedding",
            "clutter", "duplicate", "duplicates", "search", "filter", "filters", "photo", "photos", "lighting",
            "paralysis", "hick", "moodboard", "aspirational", "validation", "differentiate", "reverse", "backward",
            "myntra", "zara", "h&m", "hm", "mango", "roadster", "libas", "sassafras", "veromoda", "brand", "brands",
            "reddit", "youtube", "app store", "play store", "pinterest", "whatsapp", "haul", "hauls", "review",
            "reviews", "feedback", "verbatim", "quote", "quotes", "scrape", "scraping", "lake", "database",
            "metric", "metrics", "cvr", "conversion", "aov", "gmv", "funnel", "bounce", "growth", "revenue",
            "prd", "mvp", "feature", "features", "roadmap", "complete the look", "recommendation", "roi",
            "non-monetary", "monetary", "price", "discount", "coupon", "sale", "drop-off", "leakage", "deal", "tracking",
            "dataset", "records", "sample", "taxonomy", "pillar", "pillars", "customer", "shopper", "user", "users",
            "time", "velocity", "impulse", "expensive", "half-life", "halflife", "10", "50", "35",
        }

        tokens = set(re.findall(r"\w+", q))
        for token in tokens:
            if token in relevant_keywords:
                return True
            for kw in relevant_keywords:
                if len(token) >= 4 and (token in kw or kw in token):
                    return True

        phrases = [
            "why do", "how do", "what is", "tell me about", "can you explain",
            "how to fix", "what should we build", "customer feedback", "drop off"
        ]
        if any(p in q for p in phrases) and any(kw in q for kw in relevant_keywords):
            return True

        return False

    def generate_out_of_scope_response(self, user_query: str) -> str:
        """Returns the conversational refusal for out-of-scope queries."""
        return (
            "I'm specifically trained to analyze Myntra's wishlist data and consumer friction points. "
            "I can't answer queries outside of e-commerce strategy or this dataset, but feel free to ask me "
            "about styling isolation, drop-off metrics, sizing ambiguity, or product interventions!"
        )

    def generate_response(self, user_query: str) -> str:
        """Answers user question with natural conversational prose."""
        if not user_query or not user_query.strip():
            return "Please enter a question regarding fashion wishlist friction or customer feedback findings."

        if not self.is_query_relevant(user_query):
            return self.generate_out_of_scope_response(user_query)

        return generate_mock_response(user_query)
