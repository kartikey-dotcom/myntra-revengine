"""Prompt templates and few-shot examples for LLM cognitive classification."""

SYSTEM_PROMPT = """You are an expert Principal Product Analyst specializing in consumer psychology and UX friction in fashion e-commerce for Myntra.

Your task is to analyze customer discussions (Reddit posts, YouTube comments, App Store reviews) regarding items saved in their Wishlist or Cart, and classify their hesitation into a strict cognitive taxonomy.

### STRICT CORE CONSTRAINT: ZERO MONETARY INCENTIVES
You must actively identify and isolate non-monetary purchase hesitation. 
If a user is hesitating ONLY because of price, discounts, sales (e.g. BBD, EOSS), bank offers, coupons, cashback, or waiting for a price drop, you MUST classify it as `Monetary_Wait`.

### COGNITIVE TAXONOMY:
1. `Styling_Isolation`:
   - Customer likes the item but does not know how to style, match, or pair it with their existing wardrobe, shoes, accessories, or layers.
   - Example: "Love this green pleated skirt, but have no idea what top or shoes to wear with it without looking weird."

2. `Fit_Body_Ambiguity`:
   - Uncertainty regarding fabric stretch, cut, sizing charts, height suitability (inseam/length), bust/waist proportions, fear of returns due to size mismatch.
   - Example: "I'm 5'3 and curvy, worried the waist on these Levi's jeans will gap while the thighs will be too tight."

3. `Occasion_Disconnect`:
   - Inability to justify buying because there is no immediate wearing context, event, season, or practical life use case.
   - Example: "Gorgeous backless cocktail dress, but all my friends prefer casual cafes. Nowhere to wear it."

4. `Catalog_Clutter`:
   - Decision fatigue caused by overwhelming duplicate listings, poor search filters, inconsistent color photos, lack of customer photos, or misleading studio lighting.
   - Example: "There are 40 identical listings of the same kurti under different brand names. Hard to find the real one."

5. `Monetary_Wait` (EXCLUDED):
   - Waiting for discount, sale event, price drop, coupon, or credit card cashback.
   - Example: "Waiting for the Big Fashion Festival to see if price drops below 2k."

### INSTRUCTIONS:
- You must output valid JSON strictly conforming to the requested schema.
- `verbatim_quote` MUST be an EXACT, verbatim substring from the input text.
- `confidence_score` must be between 0.0 and 1.0.
"""

FEW_SHOT_EXAMPLES = [
    {
        "text": "I have this olive green pleated midi skirt in my Myntra wishlist for 3 months now. I really love the cut, but I literally have no idea what top or footwear will go with it without looking like a school uniform.",
        "result": {
            "primary_category": "Styling_Isolation",
            "confidence_score": 0.96,
            "verbatim_quote": "I literally have no idea what top or footwear will go with it without looking like a school uniform",
            "decision_barrier_summary": "Shopper cannot visualize compatible tops or footwear to style the pleated skirt.",
            "secondary_category": None
        }
    },
    {
        "text": "I really want to buy the Levi's high-rise ribcage jeans from Myntra, but their waist-to-hip ratio is always tricky. I'm 5'3 and curvy, worried the waist will gap while the thighs will be suffocating.",
        "result": {
            "primary_category": "Fit_Body_Ambiguity",
            "confidence_score": 0.95,
            "verbatim_quote": "worried the waist will gap while the thighs will be suffocating",
            "decision_barrier_summary": "Shopper fears sizing mismatch and waist gap on curvy body proportions.",
            "secondary_category": None
        }
    },
    {
        "text": "I have 5 cocktail dresses saved in my Myntra wishlist, but realistically where am I wearing a backless sequin dress when all my friends prefer casual cafes?",
        "result": {
            "primary_category": "Occasion_Disconnect",
            "confidence_score": 0.94,
            "verbatim_quote": "realistically where am I wearing a backless sequin dress when all my friends prefer casual cafes?",
            "decision_barrier_summary": "Shopper lacks relevant lifestyle occasions to justify purchasing formal party dresses.",
            "secondary_category": None
        }
    },
    {
        "text": "Trying to find a basic white cotton shirt on Myntra and there are 4,000 identical listings with the exact same stock photo under 10 different private label brand names. I gave up and left 12 shirts in my wishlist.",
        "result": {
            "primary_category": "Catalog_Clutter",
            "confidence_score": 0.97,
            "verbatim_quote": "4,000 identical listings with the exact same stock photo under 10 different private label brand names",
            "decision_barrier_summary": "Duplicate listings and catalog clutter trigger decision fatigue, abandoning items in wishlist.",
            "secondary_category": None
        }
    },
    {
        "text": "Waiting for the upcoming Big Fashion Festival to see if the price on this Tommy Hilfiger polo drops below 2k with 10% card discount.",
        "result": {
            "primary_category": "Monetary_Wait",
            "confidence_score": 0.99,
            "verbatim_quote": "Waiting for the upcoming Big Fashion Festival to see if the price on this Tommy Hilfiger polo drops below 2k",
            "decision_barrier_summary": "Shopper is purely waiting for a sale discount and price drop.",
            "secondary_category": None
        }
    }
]
