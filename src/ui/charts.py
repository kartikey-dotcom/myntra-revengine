"""Plotly chart builders matching the Myntra Growth Analytics dashboard design."""

import pandas as pd
import plotly.graph_objects as go


def build_donut_chart(category_counts: dict) -> go.Figure:
    """Builds a high-polish Donut chart for Cognitive Friction Categories."""
    label_map = {
        "Styling_Isolation": "Styling Isolation",
        "Fit_Body_Ambiguity": "Fit/Body Ambiguity",
        "Catalog_Clutter": "Catalog Clutter",
        "Occasion_Disconnect": "Occasion Disconnect",
    }

    ordered_keys = ["Styling_Isolation", "Fit_Body_Ambiguity", "Catalog_Clutter", "Occasion_Disconnect"]
    labels = [label_map.get(k, k) for k in ordered_keys if k in category_counts]
    values = [category_counts.get(k, 0) for k in ordered_keys if k in category_counts]
    colors = ["#FF2A6D", "#FF7597", "#FFAAB9", "#FFD5DC"]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.62,
                sort=False,
                direction="clockwise",
                marker=dict(colors=colors, line=dict(color="#FFFFFF", width=2)),
                textinfo="label+percent",
                textposition="inside",
                insidetextorientation="radial",
                insidetextfont=dict(size=10, family="Inter, sans-serif", color="#475569"),
                hovertemplate="<b>%{label}</b><br>Volume: %{value:,} records<br>Share: %{percent}<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        showlegend=False,
        margin=dict(t=10, b=10, l=10, r=10),
        height=290,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    return fig


def build_channel_stacked_bar(df: pd.DataFrame) -> go.Figure:
    """Builds a stacked bar chart displaying channel distribution across friction categories."""
    category_order = ["Styling_Isolation", "Fit_Body_Ambiguity", "Catalog_Clutter", "Occasion_Disconnect"]
    display_names = ["Styling Isolation", "Fit/Body", "Clutter", "Occasion"]

    cross = pd.crosstab(df["primary_category"], df["source_channel"], normalize="index") * 100
    cross = cross.reindex(category_order).fillna(0)

    fig = go.Figure()

    # Reddit (Bottom stack - Navy)
    fig.add_trace(
        go.Bar(
            name="Reddit",
            x=display_names,
            y=cross["reddit"].values if "reddit" in cross.columns else [30, 20, 10, 5],
            marker=dict(color="#1E293B"),
            hovertemplate="<b>Reddit</b>: %{y:.1f}%<extra></extra>",
        )
    )

    # YouTube (Middle stack - Soft Pink)
    fig.add_trace(
        go.Bar(
            name="YouTube",
            x=display_names,
            y=cross["youtube"].values if "youtube" in cross.columns else [30, 45, 15, 20],
            marker=dict(color="#FFAAB9"),
            hovertemplate="<b>YouTube</b>: %{y:.1f}%<extra></extra>",
        )
    )

    # App Store (Top stack - Hot Pink)
    fig.add_trace(
        go.Bar(
            name="App Store",
            x=display_names,
            y=cross["app_store"].values if "app_store" in cross.columns else [30, 25, 60, 40],
            marker=dict(color="#FF2A6D"),
            hovertemplate="<b>App Store</b>: %{y:.1f}%<extra></extra>",
        )
    )

    fig.update_layout(
        barmode="stack",
        margin=dict(t=10, b=10, l=10, r=10),
        height=290,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.15,
            xanchor="center",
            x=0.5,
            font=dict(size=11, color="#64748B", family="Inter, sans-serif"),
        ),
        xaxis=dict(
            showgrid=False,
            showline=True,
            linecolor="#E2E8F0",
            tickfont=dict(size=11, color="#64748B", family="Inter, sans-serif"),
        ),
        yaxis=dict(
            range=[0, 105],
            showgrid=True,
            gridcolor="#F1F5F9",
            tickfont=dict(size=10, color="#94A3B8", family="Inter, sans-serif"),
        ),
    )

    return fig


def build_performance_funnel() -> go.Figure:
    """Builds the conversion funnel chart using correct Plotly singular 'color' property."""
    fig = go.Figure(
        go.Funnel(
            y=["Wishlist Saved", "Product Viewed >3x", "Look/Outfit Visualized", "Added to Cart", "Final Order Placed"],
            x=[1200000, 720000, 240000, 110000, 50400],
            textinfo="value+percent initial",
            marker=dict(
                color=["#1E293B", "#475569", "#FF7597", "#FF2A6D", "#E11D48"],
                line=dict(color="#FFFFFF", width=2),
            ),
            connector=dict(line=dict(color="#CBD5E1", width=1, dash="dot")),
        )
    )

    fig.update_layout(
        margin=dict(t=20, b=20, l=20, r=20),
        height=320,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    return fig


def build_traffic_trend_chart() -> go.Figure:
    """Builds the weekly multi-channel ingestion volume line chart."""
    weeks = [f"Week {i}" for i in range(1, 9)]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=weeks, y=[380, 420, 390, 450, 410, 430, 440, 426], mode="lines+markers", name="Reddit", line=dict(color="#1E293B", width=3)))
    fig.add_trace(go.Scatter(x=weeks, y=[280, 310, 300, 320, 340, 310, 330, 340], mode="lines+markers", name="YouTube", line=dict(color="#FF7597", width=3)))
    fig.add_trace(go.Scatter(x=weeks, y=[260, 290, 310, 300, 290, 310, 300, 308], mode="lines+markers", name="App Store", line=dict(color="#FF2A6D", width=3)))

    fig.update_layout(
        height=300,
        margin=dict(t=20, b=20, l=20, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.15,
            xanchor="center",
            x=0.5,
            font=dict(size=11, color="#64748B", family="Inter, sans-serif"),
        ),
    )

    return fig
