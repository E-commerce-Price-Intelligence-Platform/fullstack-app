import streamlit as st
import pandas as pd

# ── Color Palette ──────────────────────────────────────────
BG_MAIN      = "#FAFAFC"
BG_CARD      = "#FFFFFF"
BORDER_COLOR = "rgba(0, 0, 0, 0.08)"
TEXT_PRIMARY = "#0B0F19"
TEXT_MUTED   = "#475569"

# Curated, professional, softer color palette for light mode
COLOR_CYAN   = "#3A86C8"  # Soft slate blue
COLOR_PURPLE = "#7F56D9"  # Muted premium purple
COLOR_AMBER  = "#DD9022"  # Softer warm amber
COLOR_GREEN  = "#2E9D8F"  # Softer forest/sage green
COLOR_RED    = "#E06666"  # Soft dusty rose

# ── SVG Icons ──────────────────────────────────────────────
ICONS = {
    "price": """<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-tag"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"></path><line x1="7" y1="7" x2="7.01" y2="7"></line></svg>""",
    "min_price": """<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-trending-down"><polyline points="23 18 13.5 8.5 8.5 13.5 1 6"></polyline><polyline points="17 18 23 18 23 12"></polyline></svg>""",
    "max_price": """<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-trending-up"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline></svg>""",
    "database": """<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-database"><ellipse cx="12" cy="5" rx="9" ry="3"></ellipse><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path><path d="M3 12c0 1.66 4 3 9 3s9-1.34 9-3"></path></svg>""",
    "platforms": """<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-cpu"><rect x="4" y="4" width="16" height="16" rx="2" ry="2"></rect><rect x="9" y="9" width="6" height="6"></rect><line x1="9" y1="1" x2="9" y2="4"></line><line x1="15" y1="1" x2="15" y2="4"></line><line x1="9" y1="20" x2="9" y2="23"></line><line x1="15" y1="20" x2="15" y2="23"></line><line x1="20" y1="9" x2="23" y2="9"></line><line x1="20" y1="15" x2="23" y2="15"></line><line x1="1" y1="9" x2="4" y2="9"></line><line x1="1" y1="15" x2="4" y2="15"></line></svg>""",
    "activity": """<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-activity"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>""",
    "layers": """<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-layers"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline></svg>""",
    "check": """<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-check-circle"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>""",
    "alert": """<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-alert-triangle"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>"""
}

# ── Custom CSS Style Injection ──────────────────────────────
def inject_custom_css():
    st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Outfit:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;700&display=swap" rel="stylesheet">
    
    <style>
    /* Main Layout */
    .stApp {
        background-color: #FAFAFC !important;
        font-family: 'Outfit', sans-serif !important;
        color: #0B0F19 !important;
    }
    
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
    }
    
    /* Hide Streamlit Default UI Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #F3F4F6 !important;
        border-right: 1.5px solid rgba(0, 0, 0, 0.06) !important;
    }
    
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] p {
        color: #475569 !important;
        font-family: 'Outfit', sans-serif !important;
    }
    
    [data-testid="stSidebar"] select, [data-testid="stSidebar"] div {
        font-family: 'Outfit', sans-serif !important;
    }
    
    /* Dataframe viewer custom border styles */
    [data-testid="stDataFrame"] {
        border: 1.5px solid rgba(0, 0, 0, 0.08) !important;
        border-radius: 8px !important;
        overflow: hidden;
    }
    
    /* Inputs */
    .stTextInput>div>div>input {
        background-color: #FFFFFF !important;
        border: 1.5px solid rgba(0, 0, 0, 0.1) !important;
        color: #0B0F19 !important;
        border-radius: 6px !important;
        font-family: 'Outfit', sans-serif !important;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: #0ea5e9 !important;
        box-shadow: 0 0 8px rgba(14, 165, 233, 0.15) !important;
    }
    
    /* Selectbox custom styles */
    .stSelectbox>div>div {
        background-color: #FFFFFF !important;
        border: 1.5px solid rgba(0, 0, 0, 0.1) !important;
        color: #0B0F19 !important;
        border-radius: 6px !important;
    }

    /* Custom Tech Card (KPIs) */
    .cyber-kpi-card {
        background: #FFFFFF;
        border: 1.5px solid rgba(0, 0, 0, 0.08);
        border-radius: 10px;
        padding: 16px 20px;
        display: flex;
        align-items: center;
        margin-bottom: 15px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .cyber-kpi-card:hover {
        border-color: rgba(14, 165, 233, 0.4);
        box-shadow: 0 4px 20px rgba(14, 165, 233, 0.08);
        transform: translateY(-2px);
    }
    
    .cyber-kpi-icon {
        width: 44px;
        height: 44px;
        background: rgba(14, 165, 233, 0.08);
        border: 1.5px solid rgba(14, 165, 233, 0.15);
        color: #0ea5e9;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 16px;
        flex-shrink: 0;
    }
    
    .cyber-kpi-info {
        flex-grow: 1;
    }
    
    .cyber-kpi-label {
        font-size: 11px !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #64748B !important;
        margin-bottom: 4px;
    }
    
    .cyber-kpi-value {
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 24px !important;
        font-weight: 700;
        color: #0B0F19;
        line-height: 1;
    }
    
    .cyber-kpi-subtext {
        font-size: 11px;
        color: #64748B;
        margin-top: 4px;
    }
    
    /* Custom Alert Banners */
    .cyber-alert {
        border-radius: 8px;
        padding: 14px 18px;
        display: flex;
        align-items: flex-start;
        margin: 15px 0;
        border-width: 1.5px;
        border-style: solid;
        font-size: 13.5px;
    }
    
    .cyber-alert-success {
        background: rgba(16, 185, 129, 0.06);
        border-color: rgba(16, 185, 129, 0.25);
        color: #059669;
    }
    
    .cyber-alert-info {
        background: rgba(157, 78, 221, 0.06);
        border-color: rgba(157, 78, 221, 0.25);
        color: #7c3aed;
    }

    .cyber-alert-warning {
        background: rgba(217, 119, 6, 0.06);
        border-color: rgba(217, 119, 6, 0.25);
        color: #d97706;
    }

    .cyber-alert-icon {
        margin-right: 12px;
        flex-shrink: 0;
        margin-top: 2px;
    }
    
    /* Code styling override */
    code, pre {
        font-family: 'JetBrains Mono', monospace !important;
        background-color: #F3F4F6 !important;
        border: 1px solid rgba(0, 0, 0, 0.08) !important;
        color: #7c3aed !important;
    }
    
    /* Scrollbars */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #FAFAFC;
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(0, 0, 0, 0.1);
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(0, 0, 0, 0.2);
    }
    </style>
    """, unsafe_allow_html=True)
# ── Plotly Custom Styler ────────────────────────────────────
def apply_plotly_theme(fig):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Outfit', color=TEXT_PRIMARY, size=11),
        xaxis=dict(
            gridcolor='rgba(0, 0, 0, 0.05)',
            color=TEXT_PRIMARY,
            linecolor='rgba(0, 0, 0, 0.12)',
            title=dict(font=dict(color=TEXT_PRIMARY, size=12, family='Outfit')),
            tickfont=dict(color=TEXT_MUTED, size=10, family='Outfit'),
            zeroline=False
        ),
        yaxis=dict(
            gridcolor='rgba(0, 0, 0, 0.05)',
            color=TEXT_PRIMARY,
            linecolor='rgba(0, 0, 0, 0.12)',
            title=dict(font=dict(color=TEXT_PRIMARY, size=12, family='Outfit')),
            tickfont=dict(color=TEXT_MUTED, size=10, family='Outfit'),
            zeroline=False
        ),
        legend=dict(
            bgcolor='rgba(255, 255, 255, 0.95)',
            bordercolor='rgba(0, 0, 0, 0.08)',
            borderwidth=1,
            font=dict(color=TEXT_MUTED, size=10, family='Outfit')
        ),
        margin=dict(l=40, r=20, t=40, b=40)
    )
    # Style title if it exists to prevent rendering "undefined" when it does not
    if fig.layout.title and getattr(fig.layout.title, 'text', None):
        fig.update_layout(
            title_font=dict(family='Outfit', color=TEXT_PRIMARY, size=14)
        )
    # Check trace types to apply appropriate color sequences
    for trace in fig.data:
        if trace.type == 'pie':
            trace.marker.line = dict(color='#FFFFFF', width=2)
        elif 'marker' in trace:
            if hasattr(trace.marker, 'line') and trace.marker.line:
                trace.marker.line.width = 0
    return fig

# ── Currency Standardizer (1 EUR = 10.8 MAD) ──────────────────
CONVERSION_RATE = 10.8

def standardize_currency(df, target_currency):
    """
    Standardizes the price and old_price columns to the target currency.
    If the raw row's currency matches the target, it remains unchanged.
    Otherwise, it converts using the conversion rate.
    """
    if df.empty:
        return df
        
    f = df.copy()
    
    # Standardize currency column names if they fall back from CSV (which has 'currency' and 'price')
    # Clean prices to numeric
    f['price'] = pd.to_numeric(f['price'], errors='coerce')
    if 'old_price' in f.columns:
        f['old_price'] = pd.to_numeric(f['old_price'], errors='coerce')
    else:
        f['old_price'] = None

    if 'currency' not in f.columns:
        f['currency'] = 'MAD'  # Default fallback

    # Apply conversions
    if target_currency == "EUR":
        # Convert MAD -> EUR (divide by 10.8)
        mask_mad = f['currency'].str.upper().isin(['MAD', 'DHS', 'DH'])
        f.loc[mask_mad, 'price'] = f.loc[mask_mad, 'price'] / CONVERSION_RATE
        f.loc[mask_mad & f['old_price'].notna(), 'old_price'] = f.loc[mask_mad & f['old_price'].notna(), 'old_price'] / CONVERSION_RATE
        f['currency'] = 'EUR'
    else:
        # Convert EUR -> MAD (multiply by 10.8)
        mask_eur = f['currency'].str.upper().isin(['EUR', '€'])
        f.loc[mask_eur, 'price'] = f.loc[mask_eur, 'price'] * CONVERSION_RATE
        f.loc[mask_eur & f['old_price'].notna(), 'old_price'] = f.loc[mask_eur & f['old_price'].notna(), 'old_price'] * CONVERSION_RATE
        f['currency'] = 'MAD'
        
    # Re-calculate discounts if missing but old_price and price are present
    if 'discount' in f.columns:
        mask_discount = f['discount'].isna() & f['old_price'].notna() & (f['old_price'] > f['price'])
        f.loc[mask_discount, 'discount'] = ((f['old_price'] - f['price']) / f['old_price'] * 100).round(0).astype(str) + '%'

    return f

# ── HTML KPI Card Builder ───────────────────────────────────
def render_kpi(label, value, icon_name, subtext=None):
    icon_svg = ICONS.get(icon_name, ICONS["price"])
    subtext_html = f'<div class="cyber-kpi-subtext">{subtext}</div>' if subtext else ''
    card_html = f"""
    <div class="cyber-kpi-card">
        <div class="cyber-kpi-icon">
            {icon_svg}
        </div>
        <div class="cyber-kpi-info">
            <div class="cyber-kpi-label">{label}</div>
            <div class="cyber-kpi-value">{value}</div>
            {subtext_html}
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

# ── Alert Banner Builder ────────────────────────────────────
def render_alert(text, type="info", icon="activity"):
    alert_class = f"cyber-alert cyber-alert-{type}"
    icon_svg = ICONS.get(icon, ICONS["activity"])
    html = f"""
    <div class="{alert_class}">
        <div class="cyber-alert-icon">{icon_svg}</div>
        <div>{text}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
