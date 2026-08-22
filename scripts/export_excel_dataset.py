"""Exports classified feedback records from the database to an Excel-ready tabular format (.csv and .xlsx)."""

import io
import sys
from pathlib import Path
import pandas as pd

# UTF-8 stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.database.db_manager import DatabaseManager


def export_dataset():
    db = DatabaseManager()
    df = db.fetch_classified_dataframe()

    if df.empty:
        print("No classified records found.")
        return

    # Map columns to required headers
    channel_map = {
        "reddit": "Reddit",
        "youtube": "YouTube",
        "app_store": "App Store",
    }

    # Off-platform actions mapping based on category/text
    def infer_off_platform_action(row):
        cat = row.get("primary_category", "")
        text = str(row.get("clean_text", "")).lower()
        if "instagram" in text or "pinterest" in text:
            return "Pinterest / Instagram Outfit Search"
        if "tailor" in text or "alteration" in text:
            return "Local Tailor Consultation"
        if "youtube" in text or "haul" in text or "try on" in text:
            return "YouTube Try-On Haul Research"
        if cat == "Styling_Isolation":
            return "Google / Pinterest Outfit Inspo Search"
        if cat == "Fit_Body_Ambiguity":
            return "Third-Party Brand Size Chart Lookup"
        if cat == "Catalog_Clutter":
            return "Competitor App Search (Amazon/Zara)"
        if cat == "Occasion_Disconnect":
            return "Postponed / Calendar Event Check"
        return "None Detected"

    # User Intent mapping
    def infer_user_intent(row):
        text = str(row.get("clean_text", "")).lower()
        if "cart" in text or "checkout" in text or "buying" in text or "order" in text:
            return "High-Intent"
        return "High-Intent" if row.get("confidence_score", 0.9) >= 0.88 else "Passive-Moodboard"

    export_rows = []
    for idx, row in df.iterrows():
        export_rows.append({
            "Record_ID": row.get("id"),
            "Source_Channel": channel_map.get(row.get("source_channel"), str(row.get("source_channel")).title()),
            "User_Intent": infer_user_intent(row),
            "Primary_Friction_Category": str(row.get("primary_category", "")).replace("_", " "),
            "Confidence_Score": round(float(row.get("confidence_score", 0.90)), 2),
            "Detected_Off_Platform_Action": infer_off_platform_action(row),
            "Verbatim_Quote": row.get("verbatim_quote") or row.get("clean_text"),
        })

    export_df = pd.DataFrame(export_rows)

    # Save to data directory
    csv_path = BASE_DIR / "data" / "myntra_categorized_wishlist_feedback.csv"
    export_df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    print(f"Exported CSV: {csv_path} ({len(export_df)} records)")

    try:
        xlsx_path = BASE_DIR / "data" / "myntra_categorized_wishlist_feedback.xlsx"
        export_df.to_excel(xlsx_path, index=False)
        print(f"Exported Excel: {xlsx_path}")
    except Exception as e:
        print(f"Excel export notice: {e}. CSV is ready.")


if __name__ == "__main__":
    export_dataset()
