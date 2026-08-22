# Myntra Wishlist AI Discovery & Intelligence Engine

> **Internal Discovery Dashboard** — Wishlist-to-Purchase Non-Conversion & Cognitive Friction Analysis  
> **Built for Myntra Growth Team** | Python • Streamlit • Plotly • Pydantic • SQLite/PostgreSQL

---

## 📌 Project Overview

The **Myntra Wishlist AI Discovery & Intelligence Engine** is an internal analytics pipeline designed to identify and quantify the psychological, UX, and non-monetary reasons why shoppers abandon items in their wishlists.

### 🚫 Strict Core Constraint: Zero Monetary Incentives
The engine strictly enforces a **Zero-Monetary Rule**. All feedback concerning discounts, coupons, sales (e.g. BBD, EOSS), price drops, and cashback are categorized as `Monetary_Wait` and purged from downstream decision models, isolating genuine UX, styling, and sizing friction.

---

## 🧠 Cognitive Friction Taxonomy

1. **`Styling_Isolation` (39.1%)**: User likes the item but cannot visualize how to style, match, or pair it with their existing wardrobe.
2. **`Fit_Body_Ambiguity` (28.8%)**: Uncertainty regarding measurements, cut, fabric stretch, and fear of size-mismatch returns.
3. **`Catalog_Clutter` (16.2%)**: Decision fatigue caused by duplicate listings, studio photo color distortion, and search exhaustion.
4. **`Occasion_Disconnect` (15.8%)**: Inability to justify buying due to lack of immediate wearing occasions or remote work lifestyle.
5. **`Monetary_Wait` (7.4% Purged)**: Price/discount noise dropped by deterministic two-tier regex and LLM filters.

---

## 🚀 Quick Start

### 1. Installation
```bash
# Clone repository
git clone https://github.com/kartikey-dotcom/myntra-revengine.git
cd myntra-revengine

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Data Ingestion (Phase 1)
```bash
python scripts/run_ingestion.py
```

### 3. Run Cognitive Classification & Zero-Monetary Purge (Phase 2)
```bash
python scripts/run_classification.py
```

### 4. Launch Executive Dashboard (Phase 3)
```bash
streamlit run app.py
```

### 5. Run Test Suite
```bash
pytest -v
```

---

## 📂 Project Structure

```
├── app.py                      # Streamlit Executive Dashboard
├── requirements.txt            # Project dependencies
├── pytest.ini                  # Pytest configuration
├── README.md                   # Repository documentation
├── .gitignore                  # Git ignore rules
│
├── docs/                       # Project Documentation & Architecture
│   ├── problemstatement.md     # Problem statement & context
│   ├── architecture.md         # Distributed system architecture
│   └── implementation.md       # 8-week phase-wise roadmap
│
├── src/
│   ├── config.py               # Central configuration & parameters
│   ├── database/
│   │   ├── schema.sql          # Data Lake & Classified table schemas
│   │   └── db_manager.py       # SQLite / PostgreSQL manager
│   ├── ingestion/
│   │   ├── preprocessor.py     # Anonymization (SHA-256) & cleaning
│   │   ├── reddit_scraper.py   # Reddit scraper (PRAW / stream)
│   │   ├── youtube_scraper.py  # YouTube Data API scraper
│   │   └── app_store_scraper.py# App Store / Play Store review scraper
│   ├── classification/
│   │   ├── taxonomy.py         # Pydantic schemas & CognitiveCategory enum
│   │   ├── prompt_templates.py # Few-shot system prompting
│   │   ├── zero_monetary_filter.py # Deterministic regex price drop filter
│   │   └── llm_classifier.py   # Batch inference & quote extraction
│   └── ui/
│       ├── styles.py           # Custom CSS & HTML components
│       └── charts.py           # Plotly Donut & Stacked Bar charts
│
├── scripts/
│   ├── run_ingestion.py        # Phase 1 Ingestion CLI
│   └── run_classification.py   # Phase 2 Classification CLI
│
└── tests/
    ├── test_ingestion.py       # Scraper & preprocessor tests
    ├── test_classification.py  # Taxonomy & regex filter tests
    └── test_ui.py              # Dashboard & visualization tests
```

---

## 📄 License
© 2024 Myntra Internal Tools • Confidential Data
