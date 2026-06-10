import streamlit as st
import plotly.express as px
import pandas as pd
import sys
import os
import time

# Inject path to backend
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
from bigtable_client import get_latest_prices

# Import design tokens and helper functions
from theme import (
    inject_custom_css, apply_plotly_theme, standardize_currency,
    render_kpi, ICONS, COLOR_CYAN, COLOR_PURPLE, COLOR_AMBER,
    COLOR_GREEN, COLOR_RED
)

# Page configuration
st.set_page_config(
    page_title="Price Intelligence Platform",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject CSS styles
inject_custom_css()

# Fetch raw data
df_raw = get_latest_prices()
if df_raw.empty:
    st.error("Aucune donnée trouvée.")
    st.stop()

# Detect if the source is Bigtable (has product_id column) or Fallback CSV
is_bigtable = 'product_id' in df_raw.columns

# ── Sidebar Configuration ──────────────────────────────────
st.sidebar.markdown("""
<div style='padding: 10px 0; border-bottom: 1px solid rgba(0, 0, 0, 0.08); margin-bottom: 20px;'>
    <h2 style='color:#0B0F19; font-size:18px; margin:0; font-weight:700; letter-spacing:1px;'>SMARTPHONE INTELLIGENCE</h2>
    <p style='color:#64748B; font-size:11px; margin:4px 0 0 0;'>Price Tracking Control Center</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("<h3 style='color:#0B0F19; font-size:14px; margin-bottom:10px;'>Filtres Globaux</h3>", unsafe_allow_html=True)

# Currency selection
currency_choice = st.sidebar.selectbox(
    "Devise d'affichage",
    ["Moroccan Dirham (MAD)", "Euro (EUR)"]
)
target_currency = "EUR" if "EUR" in currency_choice else "MAD"
currency_symbol = "€" if target_currency == "EUR" else "DH"

# Standardize currency first
df = standardize_currency(df_raw, target_currency)

# Platforms filter
available_platforms = ["Tous"] + sorted(df['platform'].dropna().unique().tolist())
sel_p = st.sidebar.selectbox("Plateforme", available_platforms)

# Brands filter
available_brands = ["Tous"] + sorted(df['brand'].dropna().unique().tolist())
sel_b = st.sidebar.selectbox("Marque", available_brands)

# Apply filters
f = df.copy()
if sel_p != "Tous":
    f = f[f['platform'] == sel_p]
if sel_b != "Tous":
    f = f[f['brand'] == sel_b]

# Sidebar Status Panels
st.sidebar.markdown("<br><h3 style='color:#0B0F19; font-size:14px; margin-bottom:10px;'>État du Système</h3>", unsafe_allow_html=True)

if is_bigtable:
    st.sidebar.markdown(f"""
    <div style='background: rgba(16, 185, 129, 0.06); border: 1.5px solid rgba(16, 185, 129, 0.2); border-radius: 8px; padding: 12px; margin-bottom: 12px;'>
        <div style='display: flex; align-items: center;'>
            <div style='width: 8px; height: 8px; background: #059669; border-radius: 50%; box-shadow: 0 0 8px rgba(5, 150, 105, 0.4); margin-right: 8px;'></div>
            <span style='color: #059669; font-size: 12px; font-weight: 600;'>GCP Bigtable Connecté</span>
        </div>
        <p style='color: #475569; font-size: 11px; margin: 6px 0 0 0;'>Flux de prix en temps réel actif.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.sidebar.markdown(f"""
    <div style='background: rgba(217, 119, 6, 0.06); border: 1.5px solid rgba(217, 119, 6, 0.2); border-radius: 8px; padding: 12px; margin-bottom: 12px;'>
        <div style='display: flex; align-items: center;'>
            <div style='width: 8px; height: 8px; background: #d97706; border-radius: 50%; box-shadow: 0 0 8px rgba(217, 119, 6, 0.4); margin-right: 8px;'></div>
            <span style='color: #d97706; font-size: 12px; font-weight: 600;'>Mode Hors-ligne (Local)</span>
        </div>
        <p style='color: #475569; font-size: 11px; margin: 6px 0 0 0;'>Données chargées depuis les fichiers CSV locaux. Bigtable injoignable.</p>
    </div>
    """, unsafe_allow_html=True)

# ── Main Content Header ─────────────────────────────────────
st.markdown("""
<div style='background: linear-gradient(135deg, #FFFFFF 0%, #F3F4F6 100%); border: 1.5px solid rgba(0, 0, 0, 0.08); border-radius: 12px; padding: 24px; margin-bottom: 24px; box-shadow: 0 4px 20px rgba(0,0,0,0.05);'>
    <div style='display: flex; justify-content: space-between; align-items: center;'>
        <div>
            <h1 style='font-size:28px; margin:0; font-weight:700; color:#0B0F19; background: linear-gradient(90deg, #0B0F19, #0ea5e9); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>PRICE INTELLIGENCE PLATFORM</h1>
            <p style='color:#64748B; font-size:13px; margin:8px 0 0 0; line-height: 1.5;'>
                Pipeline de tracking de smartphones · Collecte de données Scrapy/Selenium & Ingestion NiFi/Airflow vers GCP Bigtable & BigQuery.
            </p>
        </div>
        <div style='text-align: right;'>
            <div style='display:inline-block; background:rgba(14, 165, 233, 0.06); border: 1px solid rgba(14, 165, 233, 0.2); border-radius:20px; padding:4px 14px; color:#0ea5e9; font-size:11px; font-family: "JetBrains Mono", monospace; font-weight: 600;'>
                LIVE STREAMING ACTIVE
            </div>
            <p style='color:#64748b; font-size:11px; margin:6px 0 0 0;'>Régénération automatique toutes les 30s</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── KPIs Metrics Row ────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    render_kpi(
        "Prix Moyen",
        f"{f['price'].mean():,.0f} {currency_symbol}",
        "price",
        f"Ajusté en {target_currency}"
    )
with c2:
    render_kpi(
        "Prix Minimum",
        f"{f['price'].min():,.0f} {currency_symbol}",
        "min_price",
        f"Meilleur tarif trouvé"
    )
with c3:
    render_kpi(
        "Prix Maximum",
        f"{f['price'].max():,.0f} {currency_symbol}",
        "max_price",
        f"Tarif le plus élevé"
    )
with c4:
    render_kpi(
        "Produits Total",
        f"{len(f):,}",
        "database",
        f"Filtre actif: {len(f)}"
    )
with c5:
    render_kpi(
        "Plateformes",
        f"{f['platform'].nunique()}",
        "platforms",
        "Canaux actifs"
    )

st.markdown("<div style='margin:20px 0'></div>", unsafe_allow_html=True)

# ── Charts Row 1 ────────────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    st.markdown("### Prix moyen par plateforme")
    avg_p = f.groupby('platform')['price'].mean().reset_index()
    fig = px.bar(
        avg_p,
        x='platform',
        y='price',
        color='platform',
        color_discrete_sequence=[COLOR_CYAN, COLOR_PURPLE, COLOR_AMBER, COLOR_GREEN, COLOR_RED]
    )
    apply_plotly_theme(fig)
    fig.update_layout(
        showlegend=False,
        yaxis_title=f"Prix ({currency_symbol})",
        xaxis_title="Plateforme"
    )
    st.plotly_chart(fig, use_container_width=True, theme=None)

with col2:
    st.markdown("### Prix moyen par marque (Top 10)")
    avg_b = f.groupby('brand')['price'].mean().reset_index().sort_values('price', ascending=False).head(10)
    fig2 = px.bar(
        avg_b,
        x='brand',
        y='price',
        color='brand',
        color_discrete_sequence=[COLOR_CYAN, COLOR_PURPLE, COLOR_AMBER, COLOR_GREEN, COLOR_RED]
    )
    apply_plotly_theme(fig2)
    fig2.update_layout(
        showlegend=False,
        yaxis_title=f"Prix ({currency_symbol})",
        xaxis_title="Marque"
    )
    st.plotly_chart(fig2, use_container_width=True, theme=None)

# ── Charts Row 2 ────────────────────────────────────────────
col3, col4 = st.columns(2)
with col3:
    st.markdown("### Distribution des prix par plateforme")
    fig3 = px.box(
        f,
        x='platform',
        y='price',
        color='platform',
        color_discrete_sequence=[COLOR_CYAN, COLOR_PURPLE, COLOR_AMBER, COLOR_GREEN, COLOR_RED]
    )
    apply_plotly_theme(fig3)
    fig3.update_layout(
        showlegend=False,
        yaxis_title=f"Prix ({currency_symbol})",
        xaxis_title="Plateforme"
    )
    st.plotly_chart(fig3, use_container_width=True, theme=None)

with col4:
    st.markdown("### Comparaison par marque et plateforme")
    pivot = f.groupby(['brand', 'platform'])['price'].mean().reset_index()
    fig4 = px.bar(
        pivot,
        x='brand',
        y='price',
        color='platform',
        barmode='group',
        color_discrete_sequence=[COLOR_CYAN, COLOR_PURPLE, COLOR_AMBER]
    )
    apply_plotly_theme(fig4)
    fig4.update_layout(
        yaxis_title=f"Prix ({currency_symbol})",
        xaxis_title="Marque",
        legend_title="Plateforme"
    )
    st.plotly_chart(fig4, use_container_width=True, theme=None)

st.markdown("<div style='margin:20px 0'></div>", unsafe_allow_html=True)

# ── Data Details Row ────────────────────────────────────────
st.markdown("### Statistiques descriptives")
cs1, cs2 = st.columns(2)
with cs1:
    st.markdown("<p style='color:#00e5ff;font-size:11px;text-transform:uppercase;letter-spacing:1px;font-weight:600;margin-bottom:8px;'>Statistiques par Plateforme</p>", unsafe_allow_html=True)
    df_plat_desc = f.groupby('platform')['price'].describe().round(2)
    # Rename columns for clarity
    df_plat_desc.columns = ['Count', 'Mean', 'Std Dev', 'Min', '25%', '50% (Median)', '75%', 'Max']
    st.dataframe(df_plat_desc, use_container_width=True)
with cs2:
    st.markdown("<p style='color:#9d4edd;font-size:11px;text-transform:uppercase;letter-spacing:1px;font-weight:600;margin-bottom:8px;'>Statistiques par Marque</p>", unsafe_allow_html=True)
    df_brand_desc = f.groupby('brand')['price'].describe().round(2)
    df_brand_desc.columns = ['Count', 'Mean', 'Std Dev', 'Min', '25%', '50% (Median)', '75%', 'Max']
    st.dataframe(df_brand_desc, use_container_width=True)

st.markdown("<div style='margin:20px 0'></div>", unsafe_allow_html=True)

st.markdown("### Vue globale des données")
st.dataframe(
    f[['name', 'brand', 'model', 'price', 'currency', 'platform', 'timestamp']].sort_values('price', ascending=False),
    column_config={
        "name": st.column_config.TextColumn("Nom du produit", width="medium"),
        "brand": st.column_config.TextColumn("Marque"),
        "model": st.column_config.TextColumn("Modèle"),
        "price": st.column_config.NumberColumn(f"Prix ({currency_symbol})", format="%.2f" if target_currency == "EUR" else "%.0f"),
        "currency": st.column_config.TextColumn("Devise"),
        "platform": st.column_config.TextColumn("Source"),
        "timestamp": st.column_config.DatetimeColumn("Date de capture")
    },
    use_container_width=True,
    hide_index=True
)

# Rerun logic
time.sleep(30)
st.rerun()