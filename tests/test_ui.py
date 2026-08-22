"""Unit and Integration Tests for Phase 3 UI Dashboard and Visualizations."""

import pandas as pd
import pytest

from src.database.db_manager import DatabaseManager
from src.ui.charts import build_donut_chart, build_channel_stacked_bar


class TestUIDashboard:
    def test_database_classified_fetch(self):
        db = DatabaseManager()
        df = db.fetch_classified_dataframe()
        metrics = db.get_classification_metrics()

        assert isinstance(df, pd.DataFrame)
        assert "primary_category" in df.columns
        assert "source_channel" in df.columns
        assert "verbatim_quote" in df.columns
        assert metrics["total_classified"] > 0
        assert len(metrics["categories"]) > 0

    def test_donut_chart_generation(self):
        sample_categories = {
            "Styling_Isolation": 2988,
            "Fit_Body_Ambiguity": 2201,
            "Catalog_Clutter": 1237,
            "Occasion_Disconnect": 1208,
        }
        fig = build_donut_chart(sample_categories)
        assert fig is not None
        assert len(fig.data) == 1
        assert fig.data[0].type == "pie"
        assert fig.data[0].hole == 0.62
        assert len(fig.data[0].labels) == 4

    def test_channel_stacked_bar_generation(self):
        # Create a mock dataframe with valid category and channel distributions
        mock_data = {
            "primary_category": ["Styling_Isolation", "Fit_Body_Ambiguity", "Catalog_Clutter", "Occasion_Disconnect"] * 10,
            "source_channel": ["reddit", "youtube", "app_store", "reddit"] * 10,
        }
        df = pd.DataFrame(mock_data)
        fig = build_channel_stacked_bar(df)

        assert fig is not None
        assert len(fig.data) == 3  # 3 traces: Reddit, YouTube, App Store
        assert fig.layout.barmode == "stack"
        assert fig.data[0].name == "Reddit"
        assert fig.data[1].name == "YouTube"
        assert fig.data[2].name == "App Store"
