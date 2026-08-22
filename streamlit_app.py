"""Myntra Wishlist Discovery Engine - Streamlit Executive Dashboard.

Default Streamlit Cloud entrypoint (streamlit_app.py).
Internal analytics tool used by Growth Product Managers to analyze
non-monetary wishlist abandonment friction and size product opportunities.
"""

import sys
from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from src.database.db_manager import DatabaseManager
from src.ui.styles import CUSTOM_CSS, FOOTER_HTML
from src.ui.charts import (
    build_donut_chart,
    build_channel_stacked_bar,
    build_performance_funnel,
    build_traffic_trend_chart,
)
from src.qa.engine_chat import StrategicQAChatbot, generate_mock_response

# Page configuration
st.set_page_config(
    page_title="Growth Analytics — Myntra Wishlist Discovery Engine",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Inject Custom CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


@st.cache_data(ttl=3600)
def load_dashboard_data():
    """Loads and caches processed feedback data from the data lake."""
    db = DatabaseManager()
    df = db.fetch_classified_dataframe()
    metrics = db.get_classification_metrics()
    return df, metrics


# Load data
df, metrics = load_dashboard_data()

# Initialize active navigation state
if "active_nav" not in st.session_state:
    st.session_state.active_nav = "Customer"

# -----------------------------------------------------------------------------
# TOP NAVIGATION BAR (CLICKABLE & INTERACTIVE)
# -----------------------------------------------------------------------------
nav_col1, nav_col2, nav_col3, nav_col4, nav_col5, nav_col6 = st.columns(
    [3.0, 1.3, 1.1, 1.2, 1.2, 1.6]
)

with nav_col1:
    st.markdown('<div class="nav-brand">Growth Analytics</div>', unsafe_allow_html=True)

with nav_col2:
    if st.button(
        "Performance",
        key="nav_perf",
        use_container_width=True,
        type="primary" if st.session_state.active_nav == "Performance" else "secondary",
    ):
        st.session_state.active_nav = "Performance"
        st.rerun()

with nav_col3:
    if st.button(
        "Traffic",
        key="nav_traffic",
        use_container_width=True,
        type="primary" if st.session_state.active_nav == "Traffic" else "secondary",
    ):
        st.session_state.active_nav = "Traffic"
        st.rerun()

with nav_col4:
    if st.button(
        "Customer",
        key="nav_customer",
        use_container_width=True,
        type="primary" if st.session_state.active_nav == "Customer" else "secondary",
    ):
        st.session_state.active_nav = "Customer"
        st.rerun()

with nav_col5:
    if st.button(
        "Revenue",
        key="nav_revenue",
        use_container_width=True,
        type="primary" if st.session_state.active_nav == "Revenue" else "secondary",
    ):
        st.session_state.active_nav = "Revenue"
        st.rerun()

with nav_col6:
    if st.button(
        "Strategic Q&A",
        key="nav_qa",
        use_container_width=True,
        type="primary" if st.session_state.active_nav == "Strategic Q&A" else "secondary",
    ):
        st.session_state.active_nav = "Strategic Q&A"
        st.rerun()

st.markdown("<hr style='margin-top: 0.2rem; margin-bottom: 1.5rem; border-color: #E2E8F0;'>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# TAB 1: CUSTOMER VIEW (DEFAULT / MAIN DISCOVERY ENGINE)
# -----------------------------------------------------------------------------
if st.session_state.active_nav == "Customer":
    # Page Header
    st.markdown(
        """
        <div class="page-title">🛍️ Myntra Wishlist Discovery Engine</div>
        <div class="page-subtitle">Internal discovery dashboard — wishlist-to-purchase non-conversion analysis</div>
        """,
        unsafe_allow_html=True,
    )

    # TOP ROW: KPI SUMMARY METRIC CARDS
    total_valid = metrics.get("total_classified", 29067)
    total_purged = metrics.get("total_purged", 2250)
    categories = metrics.get("categories", {})

    dominant_cat = "Styling Isolation"
    dominant_pct = 38.2
    if categories and total_valid > 0:
        top_cat, top_count = max(categories.items(), key=lambda x: x[1])
        dominant_cat = top_cat.replace("_", " ")
        dominant_pct = round((top_count / total_valid) * 100, 1)

    kpi_col1, kpi_col2, kpi_col3 = st.columns(3)

    with kpi_col1:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-title">Valid Records Analyzed</div>
                <div class="kpi-value-row">
                    <div class="kpi-value">{total_valid:,}</div>
                    <div class="badge badge-baseline">↗ Baseline</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with kpi_col2:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-title">Monetary Noise Purged</div>
                <div class="kpi-value-row">
                    <div class="kpi-value">{total_purged:,} dropped</div>
                    <div class="badge badge-filtered">🗑️ Filtered</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with kpi_col3:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-title">Dominant Friction Pattern</div>
                <div class="kpi-value-row">
                    <div class="kpi-value critical">{dominant_cat} ({dominant_pct}%)</div>
                    <div class="badge badge-critical">⚠️ Critical</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

    # MIDDLE ROW: CHARTS (DONUT & CHANNEL BREAKDOWN)
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown(
            """
            <div class="chart-card">
                <div class="chart-title">Friction Categories Distribution</div>
            """,
            unsafe_allow_html=True,
        )
        donut_fig = build_donut_chart(categories)
        st.plotly_chart(donut_fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    with chart_col2:
        st.markdown(
            """
            <div class="chart-card">
                <div class="chart-title">Friction by Source Channel</div>
            """,
            unsafe_allow_html=True,
        )
        bar_fig = build_channel_stacked_bar(df)
        st.plotly_chart(bar_fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

    # BOTTOM SECTION: VERBATIM QUOTE EXPLORER
    st.markdown(
        """
        <div class="chart-card">
            <div class="chart-title">Authentic Customer Verbatim Evidence</div>
        """,
        unsafe_allow_html=True,
    )

    f_col1, f_col2 = st.columns([1, 3])
    with f_col1:
        selected_category = st.selectbox(
            "Filter Friction Category:",
            ["All", "Styling Isolation", "Fit Body Ambiguity", "Occasion Disconnect", "Catalog Clutter"],
            key="cat_filter_cust",
        )

    # Filter dataframe
    filtered_df = df.copy()
    if selected_category != "All":
        filtered_df = filtered_df[filtered_df["primary_category"].str.replace("_", " ").str.lower() == selected_category.lower()]

    quotes_to_display = filtered_df.head(6)

    q_cols = st.columns(2)
    for idx, (_, row) in enumerate(quotes_to_display.iterrows()):
        with q_cols[idx % 2]:
            cat_label = str(row.get("primary_category", "Unknown")).replace("_", " ")
            channel = str(row.get("source_channel", "Unknown")).title()
            quote_text = row.get("verbatim_quote") or row.get("clean_text", "")
            summary = row.get("decision_barrier_summary", "")

            st.markdown(
                f"""
                <div class="quote-card">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                        <span class="badge badge-critical">{cat_label}</span>
                        <span style="font-size: 0.75rem; color: #94A3B8; font-weight: 500;">{channel}</span>
                    </div>
                    <div class="quote-text">"{quote_text}"</div>
                    <div class="quote-barrier"><strong>Barrier:</strong> {summary}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("</div>", unsafe_allow_html=True)

    # STRATEGIC RECOMMENDATION & MVP PROPOSAL
    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="chart-card">
            <div class="chart-title">Strategic Intervention: Complete the Look Engine</div>
            <p style="font-size: 0.95rem; color: #475569; line-height: 1.6;">
                Based on <strong>38.2% of high-intent wishlist hesitations</strong> stemming from Styling Isolation, 
                our primary non-monetary product recommendation is an AI-driven bundling engine that dynamically generates 
                outfit pairings directly on the Wishlist and PDP surfaces.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if "show_prd" not in st.session_state:
        st.session_state.show_prd = False

    btn_col1, btn_col2 = st.columns([1, 4])
    with btn_col1:
        if st.button("View MVP Proposal", use_container_width=True, key="btn_mvp_cust"):
            st.session_state.show_prd = not st.session_state.show_prd

    if st.session_state.show_prd:
        with st.expander("📋 PRD: 'Complete the Look' AI Bundling Feature (Click to collapse)", expanded=True):
            st.markdown(
                """
                ### Product Requirements Document (PRD)
                **Feature Name:** *Myntra StyleSync — Complete the Look Bundling*  
                **Target Metric:** +12% Wishlist-to-Cart Conversion Rate  
                **Target Quarter:** Q3/Q4 Growth Roadmap  

                ---

                #### 1. Problem Statement
                * **38.2% of high-intent shoppers** abandon wishlist items because they cannot visualize how to pair the garment with existing wardrobe items or compatible accessories.
                * Standalone product photos fail to provide outfit inspiration, leading to decision paralysis.

                #### 2. Proposed AI Solution
                1. **Dynamic Outfit Generator:** Automatically generate 3 curated outfit bundles (e.g. *Office Casual, Weekend Brunch, Evening Party*) around any saved wishlist SKU.
                2. **Wardrobe Harmony Score:** Allow shoppers to select items from their past purchase history to calculate outfit compatibility.
                3. **1-Click Bundle Checkout:** Purchase the primary item with 1-click add-on options for paired bottoms or accessories, eliminating navigation friction.

                #### 3. Success Metrics & KPIs
                * **Primary KPI:** +12% Lift in Wishlist conversion within 14 days of save.
                * **Secondary KPI:** +18% increase in Average Order Value (AOV) via paired cross-selling.
                """
            )

# -----------------------------------------------------------------------------
# TAB 2: PERFORMANCE VIEW
# -----------------------------------------------------------------------------
elif st.session_state.active_nav == "Performance":
    st.markdown(
        """
        <div class="page-title">📈 Simulated Funnel Metrics (Based on Industry Benchmarks)</div>
        <div class="page-subtitle">Tracking wishlist-to-checkout velocity and cognitive bottleneck resolution</div>
        """,
        unsafe_allow_html=True,
    )

    p1, p2, p3, p4 = st.columns(4)
    with p1:
        st.markdown(
            """
            <div class="kpi-card">
                <div class="kpi-title">Wishlist Conversion Rate</div>
                <div class="kpi-value-row">
                    <div class="kpi-value">4.2%</div>
                    <div class="badge badge-critical">Target: 6.5%</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with p2:
        st.markdown(
            """
            <div class="kpi-card">
                <div class="kpi-title">Cart Abandonment Rate</div>
                <div class="kpi-value-row">
                    <div class="kpi-value">68.4%</div>
                    <div class="badge badge-filtered">-2.1% MoM</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with p3:
        st.markdown(
            """
            <div class="kpi-card">
                <div class="kpi-title">Average Order Value (AOV)</div>
                <div class="kpi-value-row">
                    <div class="kpi-value">₹ 2,140</div>
                    <div class="badge badge-baseline">+8.4% YoY</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with p4:
        st.markdown(
            """
            <div class="kpi-card">
                <div class="kpi-title">Est. GMV Recovery Potential</div>
                <div class="kpi-value-row">
                    <div class="kpi-value critical">₹ 14.8 Cr</div>
                    <div class="badge badge-critical">High Priority</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

    # Conversion Funnel Chart
    st.markdown(
        """
        <div class="chart-card">
            <div class="chart-title">Wishlist Drop-off Funnel Analysis (Monthly Cohort)</div>
        """,
        unsafe_allow_html=True,
    )
    funnel_fig = build_performance_funnel()
    st.plotly_chart(funnel_fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# TAB 3: TRAFFIC & INGESTION HEALTH
# -----------------------------------------------------------------------------
elif st.session_state.active_nav == "Traffic":
    st.markdown(
        """
        <div class="page-title">📡 Ingestion Traffic & Multi-Channel Pipeline Health</div>
        <div class="page-subtitle">Data lake crawl volume, API rates, and channel ingestion distribution</div>
        """,
        unsafe_allow_html=True,
    )

    channels_data = metrics.get("channels", {})
    reddit_vol = channels_data.get("reddit", 11772)
    yt_vol = channels_data.get("youtube", 8806)
    app_vol = channels_data.get("app_store", 8489)

    t1, t2, t3 = st.columns(3)
    with t1:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-title">Reddit Discussions (PRAW)</div>
                <div class="kpi-value-row">
                    <div class="kpi-value">{reddit_vol:,}</div>
                    <div class="badge badge-baseline">🟢 Active Stream</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with t2:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-title">YouTube Comments (API v3)</div>
                <div class="kpi-value-row">
                    <div class="kpi-value">{yt_vol:,}</div>
                    <div class="badge badge-baseline">🟢 Quota Normal</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with t3:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-title">App Store & Google Play</div>
                <div class="kpi-value-row">
                    <div class="kpi-value">{app_vol:,}</div>
                    <div class="badge badge-baseline">🟢 Synced</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

    # Ingestion timeline chart
    st.markdown(
        """
        <div class="chart-card">
            <div class="chart-title">Weekly Feedback Ingestion Trend by Source Channel</div>
        """,
        unsafe_allow_html=True,
    )
    trend_fig = build_traffic_trend_chart()
    st.plotly_chart(trend_fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# TAB 4: REVENUE OPPORTUNITY CALCULATOR
# -----------------------------------------------------------------------------
elif st.session_state.active_nav == "Revenue":
    st.markdown(
        """
        <div class="page-title">💰 Opportunity Sizing: Simulated Revenue Recovery Calculator</div>
        <div class="page-subtitle">Interactive financial sizing of Wishlist UX & styling intervention roadmaps</div>
        """,
        unsafe_allow_html=True,
    )

    r_col1, r_col2 = st.columns([1, 1.2])

    with r_col1:
        st.markdown("### 🎛️ Simulation Parameters")
        monthly_wishlists = st.slider("Monthly Active Wishlist Saves", min_value=500000, max_value=5000000, value=2000000, step=100000, format="%d")
        current_cvr = st.slider("Current Wishlist Conversion Rate (%)", min_value=1.0, max_value=10.0, value=4.2, step=0.1)
        expected_lift = st.slider("Expected Lift from 'Complete the Look' MVP (%)", min_value=0.5, max_value=5.0, value=1.5, step=0.1)
        aov = st.slider("Average Order Value (₹)", min_value=1000, max_value=5000, value=2140, step=50)

    with r_col2:
        new_cvr = current_cvr + expected_lift
        current_orders = monthly_wishlists * (current_cvr / 100)
        new_orders = monthly_wishlists * (new_cvr / 100)
        incremental_orders = new_orders - current_orders
        monthly_gmv_lift = (incremental_orders * aov) / 10000000  # in Crores
        annual_gmv_lift = monthly_gmv_lift * 12

        st.markdown("### 📊 Opportunity Sizing Results")
        st.markdown(
            f"""
            <div class="kpi-card" style="margin-bottom: 1rem;">
                <div class="kpi-title">Incremental Monthly Orders</div>
                <div class="kpi-value">{int(incremental_orders):,} orders</div>
                <div class="badge badge-baseline">+{expected_lift}% Conversion Lift</div>
            </div>
            <div class="kpi-card" style="margin-bottom: 1rem;">
                <div class="kpi-title">Monthly Recovered GMV</div>
                <div class="kpi-value critical">₹ {monthly_gmv_lift:.2f} Crores / month</div>
                <div class="badge badge-critical">High Impact</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Annualized Revenue Potential</div>
                <div class="kpi-value critical">₹ {annual_gmv_lift:.2f} Crores / year</div>
                <div class="badge badge-filtered">Zero Discount Cost</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# -----------------------------------------------------------------------------
# TAB 5: STRATEGIC PM Q&A & AI COPILOT VIEW (GPT MODE)
# -----------------------------------------------------------------------------
elif st.session_state.active_nav == "Strategic Q&A":
    from src.qa.engine_chat import StrategicQAChatbot

    st.markdown(
        """
        <div class="page-title">🤖 Ask the Engine: Strategic AI Copilot</div>
        <div class="page-subtitle">Interactive GPT intelligence layer powered by RAG on 29,067 customer reviews across Reddit, YouTube & App Store</div>
        """,
        unsafe_allow_html=True,
    )

    # Top summary metrics for Q&A
    q_col1, q_col2, q_col3 = st.columns(3)
    with q_col1:
        st.markdown(
            """
            <div class="kpi-card">
                <div class="kpi-title">Primary Purchase Blocker</div>
                <div class="kpi-value critical">Styling Isolation</div>
                <div class="badge badge-critical">38.2% Share</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with q_col2:
        st.markdown(
            """
            <div class="kpi-card">
                <div class="kpi-title">Off-Platform Leakage Rate</div>
                <div class="kpi-value">43.7%</div>
                <div class="badge badge-filtered">WhatsApp / Pinterest</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with q_col3:
        st.markdown(
            """
            <div class="kpi-card">
                <div class="kpi-title">Recommended Feature ROI</div>
                <div class="kpi-value">+12% CVR</div>
                <div class="badge badge-baseline">+18% AOV Lift</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

    # Initialize Chatbot & Session State History
    if "qa_chatbot" not in st.session_state:
        st.session_state.qa_chatbot = StrategicQAChatbot()

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "Hello! I am your Myntra Wishlist Strategic AI Copilot. "
                    "I am connected to our 29,067 customer feedback records across Reddit (r/IndianFashionAddicts, r/TwoXIndia), "
                    "YouTube try-on hauls, and App Store reviews. Ask me any strategic product question, search for customer quote evidence, "
                    "or inquire about roadmap interventions!"
                ),
            }
        ]

    # Callback for quick-suggestion chips
    def send_chip_prompt(prompt_text):
        st.session_state.messages.append({"role": "user", "content": prompt_text})
        response = st.session_state.qa_chatbot.generate_response(prompt_text)
        st.session_state.messages.append({"role": "assistant", "content": response})

    # Header controls (Reset chat option)
    if len(st.session_state.messages) > 1:
        reset_col1, reset_col2 = st.columns([6, 1])
        with reset_col2:
            if st.button("🔄 New Chat", key="btn_reset_chat", use_container_width=True):
                st.session_state.messages = [
                    {
                        "role": "assistant",
                        "content": (
                            "Hello! I am your Myntra Wishlist Strategic AI Copilot. "
                            "I am connected to our 29,067 customer feedback records across Reddit (r/IndianFashionAddicts, r/TwoXIndia), "
                            "YouTube try-on hauls, and App Store reviews. Ask me any strategic product question, search for customer quote evidence, "
                            "or inquire about roadmap interventions!"
                        ),
                    }
                ]
                st.rerun()

    # 1. Render Chat History FIRST (Main vertical body)
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="🛍️" if message["role"] == "assistant" else "👤"):
            st.markdown(message["content"])

    # 2. Quick Suggestion Chips (Only appear on fresh/initial chat)
    if len(st.session_state.messages) <= 1:
        st.markdown("<div style='font-size: 0.85rem; font-weight: 600; color: #64748B; margin-top: 1.25rem; margin-bottom: 0.5rem;'>💡 Suggested Topics to Explore (Click to ask):</div>", unsafe_allow_html=True)
        chip_col1, chip_col2, chip_col3, chip_col4 = st.columns(4)
        with chip_col1:
            st.button(
                "👗 Why Styling Isolation?",
                key="chip_style",
                use_container_width=True,
                on_click=send_chip_prompt,
                args=("Why is Styling Isolation the #1 reason users abandon their wishlists?",),
            )
        with chip_col2:
            st.button(
                "📏 Sizing Complaints?",
                key="chip_fit",
                use_container_width=True,
                on_click=send_chip_prompt,
                args=("What are the most frequent sizing and fit ambiguity complaints in the reviews?",),
            )
        with chip_col3:
            st.button(
                "📱 WhatsApp / Pinterest Leakage?",
                key="chip_off",
                use_container_width=True,
                on_click=send_chip_prompt,
                args=("How do users try to solve fashion hesitation off-platform on WhatsApp and Pinterest?",),
            )
        with chip_col4:
            st.button(
                "🚀 Complete the Look ROI?",
                key="chip_roi",
                use_container_width=True,
                on_click=send_chip_prompt,
                args=("What is the expected ROI and GMV recovery of the 'Complete the Look' MVP?",),
            )

    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

    # 3. Prominent, Directly Visible Search Box (In-Page)
    with st.container():
        st.markdown(
            """
            <div style="background: #FFFFFF; border: 1.5px solid #E2E8F0; border-radius: 12px; padding: 1rem 1.25rem 0.5rem 1.25rem; margin-bottom: 1rem; box-shadow: 0 2px 4px rgba(0,0,0,0.03);">
                <div style="font-size: 0.95rem; font-weight: 700; color: #0F172A; margin-bottom: 0.35rem;">
                    🔎 Ask the Intelligence Engine
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        with st.form("inpage_qa_search_form", clear_on_submit=True):
            f_col1, f_col2 = st.columns([5, 1.2])
            with f_col1:
                inpage_input = st.text_input(
                    "Search Input",
                    placeholder="Ask me about customer hesitation patterns, styling isolation, or sizing...",
                    label_visibility="collapsed",
                )
            with f_col2:
                inpage_submit = st.form_submit_button("Ask Copilot 🚀", use_container_width=True, type="primary")

    # 4. Native Pinned Chat Input (Bottom bar)
    user_bottom_input = st.chat_input("Ask me about customer hesitation patterns...")

    query_to_process = None
    if inpage_submit and inpage_input.strip():
        query_to_process = inpage_input.strip()
    elif user_bottom_input and user_bottom_input.strip():
        query_to_process = user_bottom_input.strip()

    if query_to_process:
        # Append user message
        st.session_state.messages.append({"role": "user", "content": query_to_process})
        
        # Generate and append AI response
        ai_response = st.session_state.qa_chatbot.generate_response(query_to_process)
        st.session_state.messages.append({"role": "assistant", "content": ai_response})
        st.rerun()

# Footer (render on all tabs)
st.markdown(FOOTER_HTML, unsafe_allow_html=True)
