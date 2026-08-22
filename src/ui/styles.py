"""Custom CSS styles and HTML templates for Myntra Growth Analytics dashboard."""

CUSTOM_CSS = """
<style>
/* Main Page Layout and Font */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: #1E293B;
}

/* Hide Streamlit default header/footer padding */
.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 2rem !important;
    max-width: 1200px !important;
}

header[data-testid="stHeader"] {
    background: transparent !important;
}

#MainMenu, footer, header {visibility: hidden;}

/* Custom Top Navigation Bar */
.top-navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem 0rem 1.25rem 0rem;
    border-bottom: 1px solid #E2E8F0;
    margin-bottom: 1.5rem;
}

.nav-brand {
    font-size: 1.35rem;
    font-weight: 700;
    color: #E11D48;
    text-decoration: none;
    letter-spacing: -0.02em;
}

.nav-links {
    display: flex;
    gap: 2rem;
    align-items: center;
}

.nav-link {
    color: #64748B;
    font-size: 0.95rem;
    font-weight: 500;
    text-decoration: none;
    padding-bottom: 0.5rem;
}

.nav-link.active {
    color: #E11D48;
    font-weight: 600;
    border-bottom: 2px solid #E11D48;
}

.nav-icons {
    display: flex;
    gap: 1rem;
    color: #64748B;
    font-size: 1.1rem;
}

/* Page Header */
.page-title {
    font-size: 1.75rem;
    font-weight: 700;
    color: #0F172A;
    margin-bottom: 0.25rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.page-subtitle {
    font-size: 0.95rem;
    color: #64748B;
    margin-bottom: 1.5rem;
}

/* Metric KPI Cards */
.kpi-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    height: 100%;
}

.kpi-title {
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #64748B;
    margin-bottom: 0.6rem;
}

.kpi-value-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.kpi-value {
    font-size: 1.85rem;
    font-weight: 700;
    color: #0F172A;
    line-height: 1.2;
}

.kpi-value.critical {
    color: #E11D48;
    font-size: 1.5rem;
}

/* Pill Badges */
.badge {
    font-size: 0.75rem;
    font-weight: 600;
    padding: 0.25rem 0.6rem;
    border-radius: 9999px;
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
}

.badge-baseline {
    background-color: #ECFDF5;
    color: #059669;
}

.badge-filtered {
    background-color: #FFF7ED;
    color: #EA580C;
}

.badge-critical {
    background-color: #FFF1F2;
    color: #E11D48;
}

.badge-channel {
    background-color: #F1F5F9;
    color: #475569;
    font-size: 0.7rem;
    font-weight: 600;
    padding: 0.2rem 0.5rem;
    border-radius: 6px;
}

.badge-confidence {
    background-color: #ECFDF5;
    color: #059669;
    font-size: 0.75rem;
    font-weight: 600;
    padding: 0.2rem 0.5rem;
    border-radius: 6px;
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
}

/* Chart Containers */
.chart-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 1.25rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    height: 100%;
}

.chart-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: #0F172A;
    margin-bottom: 0.75rem;
}

/* Verbatim Evidence Quote Cards */
.evidence-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-left: 4px solid #E11D48;
    border-radius: 10px;
    padding: 1rem 1.15rem;
    box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    margin-bottom: 1rem;
    min-height: 115px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}

.evidence-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.6rem;
}

.evidence-text {
    font-size: 0.88rem;
    font-style: italic;
    color: #334155;
    line-height: 1.45;
}

/* Strategic Recommendation Card */
.recommendation-card {
    background: #FFF5F7;
    border: 1px solid #FFE4E9;
    border-radius: 12px;
    padding: 1.5rem;
    margin-top: 1.5rem;
    margin-bottom: 2rem;
}

.recommendation-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #0F172A;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
}

.recommendation-text {
    font-size: 0.92rem;
    color: #475569;
    line-height: 1.5;
    margin-bottom: 1rem;
}

/* Custom Styled Button */
div.stButton > button:first-child {
    background-color: #E11D48 !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    padding: 0.5rem 1.25rem !important;
    border-radius: 8px !important;
    border: none !important;
    box-shadow: 0 1px 2px rgba(225, 29, 72, 0.2) !important;
    transition: all 0.2s ease !important;
}

div.stButton > button:first-child:hover {
    background-color: #BE123C !important;
    color: #FFFFFF !important;
}

/* Footer */
.custom-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: 1.5rem;
    border-top: 1px solid #E2E8F0;
    margin-top: 2rem;
    font-size: 0.8rem;
    color: #94A3B8;
}

.footer-links {
    display: flex;
    gap: 1.5rem;
}

.footer-links a {
    color: #64748B;
    text-decoration: none;
}
</style>
"""

NAVBAR_HTML = """
<div class="top-navbar">
    <div class="nav-brand">Growth Analytics</div>
    <div class="nav-links">
        <span class="nav-link">Performance</span>
        <span class="nav-link">Traffic</span>
        <span class="nav-link active">Customer</span>
        <span class="nav-link">Revenue</span>
    </div>
    <div class="nav-icons">
        <span>🔔</span>
        <span>👤</span>
    </div>
</div>
"""

FOOTER_HTML = """
<div class="custom-footer">
    <div>© 2024 Myntra Internal Tools • Confidential Data</div>
    <div class="footer-links">
        <a href="#">Privacy Policy</a>
        <a href="#">Support</a>
        <a href="#">Documentation</a>
    </div>
</div>
"""
