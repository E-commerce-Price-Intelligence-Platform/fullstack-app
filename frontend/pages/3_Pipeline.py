import streamlit as st
import plotly.express as px
import pandas as pd
import sys
import os

# Inject path to backend
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))
# pyrefly: ignore [missing-import]
from bigtable_client import get_latest_prices

# Import design tokens and helper functions
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from theme import (
    inject_custom_css, apply_plotly_theme, standardize_currency,
    render_kpi, render_alert, ICONS, COLOR_CYAN, COLOR_PURPLE,
    COLOR_AMBER, COLOR_GREEN, COLOR_RED
)

# Page configuration
st.set_page_config(page_title="Pipeline Status", layout="wide")

# Inject CSS styles
inject_custom_css()

# Pipeline-specific extra CSS (Animations and flow diagram)
st.markdown("""
<style>
@keyframes pulse-green {
    0% { box-shadow: 0 0 0 0 rgba(0, 230, 118, 0.7); }
    70% { box-shadow: 0 0 0 6px rgba(0, 230, 118, 0); }
    100% { box-shadow: 0 0 0 0 rgba(0, 230, 118, 0); }
}

@keyframes pulse-amber {
    0% { box-shadow: 0 0 0 0 rgba(255, 158, 0, 0.7); }
    70% { box-shadow: 0 0 0 6px rgba(255, 158, 0, 0); }
    100% { box-shadow: 0 0 0 0 rgba(255, 158, 0, 0); }
}

.glow-dot-active {
    width: 10px;
    height: 10px;
    background-color: #00e676;
    border-radius: 50%;
    display: inline-block;
    animation: pulse-green 2s infinite;
}

.glow-dot-warning {
    width: 10px;
    height: 10px;
    background-color: #ff9e00;
    border-radius: 50%;
    display: inline-block;
    animation: pulse-amber 2s infinite;
}

/* Architecture Flow styles */
.flow-container {
    background: #FFFFFF;
    border: 1.5px solid rgba(0, 0, 0, 0.08);
    border-radius: 12px;
    padding: 24px;
    margin: 20px 0;
}

.flow-grid {
    display: grid;
    grid-template-columns: 1.2fr 40px 1.5fr 40px 1.2fr;
    align-items: center;
    gap: 15px;
}

@media (max-width: 992px) {
    .flow-grid {
        grid-template-columns: 1fr;
        gap: 20px;
    }
    .flow-arrow-cell {
        transform: rotate(90deg);
        margin: 10px 0;
        text-align: center;
    }
}

.flow-node {
    background: #F9FAFB;
    border: 1.5px solid rgba(0, 0, 0, 0.08);
    border-radius: 10px;
    padding: 16px;
    position: relative;
    transition: all 0.3s;
}

.flow-node:hover {
    border-color: rgba(14, 165, 233, 0.3);
    box-shadow: 0 4px 15px rgba(14, 165, 233, 0.06);
}

.flow-node-title {
    font-size: 13px;
    font-weight: 700;
    color: #0B0F19;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 6px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.flow-node-desc {
    font-size: 11.5px;
    color: #475569;
    line-height: 1.4;
}

.flow-node-sub {
    font-size: 10px;
    font-family: 'JetBrains Mono', monospace;
    color: #64748B;
    margin-top: 8px;
    border-top: 1px solid rgba(0, 0, 0, 0.05);
    padding-top: 6px;
}

.flow-arrow-cell {
    display: flex;
    justify-content: center;
    align-items: center;
    color: #0ea5e9;
    font-size: 20px;
    font-weight: bold;
}

.flow-arrow-path {
    width: 100%;
    height: 2px;
    background: rgba(14, 165, 233, 0.2);
    position: relative;
}

.flow-arrow-path::after {
    content: '';
    position: absolute;
    right: 0;
    top: -4px;
    width: 0;
    height: 0;
    border-top: 5px solid transparent;
    border-bottom: 5px solid transparent;
    border-left: 8px solid rgba(14, 165, 233, 0.6);
}
</style>
""", unsafe_allow_html=True)

# Fetch data
df = get_latest_prices()
is_bigtable = 'product_id' in df.columns

# ── Header ──────────────────────────────────────────────────
st.markdown("""
<div style='background: linear-gradient(135deg, #FFFFFF 0%, #F3F4F6 100%); border: 1.5px solid rgba(0, 0, 0, 0.08); border-radius: 12px; padding: 24px; margin-bottom: 24px; box-shadow: 0 4px 20px rgba(0,0,0,0.05);'>
    <h1 style='font-size:28px; margin:0; font-weight:700; color:#0B0F19; background: linear-gradient(90deg, #0B0F19, #059669); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>PIPELINE STATUS & AUDIT</h1>
    <p style='color:#64748B; font-size:13px; margin:8px 0 0 0; line-height: 1.5;'>
        Orchestration des flux de données · Suivi d'ingestion en temps réel · Audit de complétude et qualité du catalogue.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Component Status Panel ──────────────────────────────────
st.markdown("### Statut des Services d'Orchestration")
c_stat1, c_stat2, c_stat3, c_stat4 = st.columns(4)

with c_stat1:
    st.markdown(f"""
    <div style='background: #FFFFFF; border: 1.5px solid rgba(0, 0, 0, 0.08); border-radius: 10px; padding: 16px; min-height: 90px;'>
        <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;'>
            <span style='font-size: 11px; color: #64748B; text-transform: uppercase; letter-spacing: 0.5px;'>Spiders Crawler</span>
            <div class='glow-dot-active'></div>
        </div>
        <div style='color: #0B0F19; font-size: 15px; font-weight: 600;'>Scrapy + Selenium</div>
        <p style='color: #475569; font-size: 10.5px; margin: 4px 0 0 0;'>Actif (3 sites surveillés)</p>
    </div>
    """, unsafe_allow_html=True)

with c_stat2:
    st.markdown(f"""
    <div style='background: #FFFFFF; border: 1.5px solid rgba(0, 0, 0, 0.08); border-radius: 10px; padding: 16px; min-height: 90px;'>
        <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;'>
            <span style='font-size: 11px; color: #64748B; text-transform: uppercase; letter-spacing: 0.5px;'>Batch Orchestration</span>
            <div class='glow-dot-active'></div>
        </div>
        <div style='color: #0B0F19; font-size: 15px; font-weight: 600;'>Apache Airflow</div>
        <p style='color: #475569; font-size: 10.5px; margin: 4px 0 0 0;'>Actif (Dag quotidien)</p>
    </div>
    """, unsafe_allow_html=True)

with c_stat3:
    st.markdown(f"""
    <div style='background: #FFFFFF; border: 1.5px solid rgba(0, 0, 0, 0.08); border-radius: 10px; padding: 16px; min-height: 90px;'>
        <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;'>
            <span style='font-size: 11px; color: #64748B; text-transform: uppercase; letter-spacing: 0.5px;'>Real-time Ingest</span>
            <div class='glow-dot-active'></div>
        </div>
        <div style='color: #0B0F19; font-size: 15px; font-weight: 600;'>Apache NiFi</div>
        <p style='color: #475569; font-size: 10.5px; margin: 4px 0 0 0;'>Actif (Polling 30s)</p>
    </div>
    """, unsafe_allow_html=True)

with c_stat4:
    if is_bigtable:
        st.markdown(f"""
        <div style='background: #FFFFFF; border: 1.5px solid rgba(0, 0, 0, 0.08); border-radius: 10px; padding: 16px; min-height: 90px;'>
            <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;'>
                <span style='font-size: 11px; color: #64748B; text-transform: uppercase; letter-spacing: 0.5px;'>NoSQL Database</span>
                <div class='glow-dot-active'></div>
            </div>
            <div style='color: #0B0F19; font-size: 15px; font-weight: 600;'>GCP Bigtable</div>
            <p style='color: #475569; font-size: 10.5px; margin: 4px 0 0 0;'>En ligne (price-intel-instance)</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style='background: #FFFFFF; border: 1.5px solid rgba(0, 0, 0, 0.08); border-radius: 10px; padding: 16px; min-height: 90px;'>
            <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;'>
                <span style='font-size: 11px; color: #64748B; text-transform: uppercase; letter-spacing: 0.5px;'>NoSQL Database</span>
                <div class='glow-dot-warning'></div>
            </div>
            <div style='color: #0B0F19; font-size: 15px; font-weight: 600;'>GCP Bigtable</div>
            <p style='color: #d97706; font-size: 10.5px; margin: 4px 0 0 0;'>Inaccessible (Fallback local)</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='margin:20px 0'></div>", unsafe_allow_html=True)

# ── Ingestion Metrics ───────────────────────────────────────
st.markdown("### Statistiques de Capture")
m1, m2, m3, m4 = st.columns(4)
with m1:
    render_kpi("Total Enregistrements", f"{len(df)}", "database", "Catalogue actif")
with m2:
    render_kpi("Amazon FR", f"{len(df[df['platform']=='amazon_fr'])}", "platforms", "Canal international (Scraping)")
with m3:
    render_kpi("Jumia MA", f"{len(df[df['platform']=='jumia_ma'])}", "platforms", "Canal national (Scraping)")
with m4:
    render_kpi("Electroplanet", f"{len(df[df['platform']=='electroplanet'])}", "platforms", "Canal national (Selenium)")

st.markdown("<div style='margin:16px 0'></div>", unsafe_allow_html=True)

# Charts Row
col1, col2 = st.columns(2)
with col1:
    st.markdown("#### Proportion de capture par plateforme")
    pie_data = df.groupby('platform').size().reset_index(name='count')
    fig = px.pie(
        pie_data,
        values='count',
        names='platform',
        color_discrete_sequence=[COLOR_CYAN, COLOR_PURPLE, COLOR_AMBER, COLOR_GREEN],
        hole=0.45
    )
    apply_plotly_theme(fig)
    fig.update_layout(margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig, use_container_width=True, theme=None)

with col2:
    st.markdown("#### Top 5 des marques les plus représentées")
    brand_data = df.groupby('brand').size().reset_index(name='count').sort_values('count', ascending=False).head(5)
    fig2 = px.bar(
        brand_data,
        x='brand',
        y='count',
        color='brand',
        color_discrete_sequence=[COLOR_CYAN, COLOR_PURPLE, COLOR_AMBER, COLOR_GREEN, COLOR_RED]
    )
    apply_plotly_theme(fig2)
    fig2.update_layout(
        showlegend=False,
        xaxis_title="Marque",
        yaxis_title="Nombre de smartphones"
    )
    st.plotly_chart(fig2, use_container_width=True, theme=None)

st.markdown("<div style='margin:20px 0'></div>", unsafe_allow_html=True)

# ── Data Quality Dashboard ──────────────────────────────────
st.markdown("### Audit de Qualité & Complétude des Données")

total = len(df)
missing_price = df['price'].isna().sum() if total > 0 else 0
missing_brand = df['brand'].isna().sum() if total > 0 else 0
has_price     = total - missing_price
completeness  = round((has_price/total)*100, 1) if total > 0 else 100
duplicates    = df.duplicated(subset=['name', 'platform']).sum() if total > 0 else 0

q1, q2, q3, q4 = st.columns(4)
with q1:
    render_kpi("Complétude Prix", f"{completeness}%", "check", "Conformité de valeur")
with q2:
    render_kpi("Prix Manquants", f"{missing_price}", "alert" if missing_price > 0 else "check", "Erreurs de parsing")
with q3:
    render_kpi("Marques Manquantes", f"{missing_brand}", "alert" if missing_brand > 0 else "check", "Erreurs d'identification")
with q4:
    render_kpi("Doublons Détectés", f"{duplicates}", "alert" if duplicates > 0 else "check", "Redondances plateforme")

st.markdown("<div style='margin:20px 0'></div>", unsafe_allow_html=True)

# ── Flow Diagram ────────────────────────────────────────────
st.markdown("### Schéma d'Architecture de l'Écosystème")

st.markdown("""<div class="flow-container"><div class="flow-grid"><div class="flow-node"><div class="flow-node-title"><span>01. CRAWLERS</span><span style='color:#00e5ff; font-family:monospace; font-size:10px;'>PYTHON</span></div><div class="flow-node-desc">Scrapers programmés avec <b>Scrapy</b> (Jumia, Amazon) et <b>Selenium</b> (Electroplanet) pour bypasser le JS.</div><div class="flow-node-sub">Output: /output/*.json</div></div><div class="flow-arrow-cell"><div style='display:flex; flex-direction:column; align-items:center; width:100%;'><div style='font-size: 11px; color: #00e5ff; margin-bottom: 4px; font-family: monospace;'>Ingest</div><div class="flow-arrow-path"></div></div></div><div class="flow-node" style="border-color: rgba(157, 78, 221, 0.4);"><div class="flow-node-title"><span style="color:#a78bfa;">02. PIPELINES PARALLÈLES</span><span style='color:#a78bfa; font-family:monospace; font-size:10px;'>HYBRID</span></div><div class="flow-node-desc"><b>Streaming:</b> Apache NiFi détecte chaque JSON en 30s et le pousse en micro-transactions vers Bigtable.<br><b>Batch:</b> Apache Airflow charge les données brutes dans BigQuery pour analyses historiques.</div><div class="flow-node-sub">NoSQL & Data Warehouse</div></div><div class="flow-arrow-cell"><div style='display:flex; flex-direction:column; align-items:center; width:100%;'><div style='font-size: 11px; color: #00e5ff; margin-bottom: 4px; font-family: monospace;'>Transform</div><div class="flow-arrow-path"></div></div></div><div class="flow-node" style="border-color: rgba(0, 230, 118, 0.4);"><div class="flow-node-title"><span style="color:#00e676;">03. ANALYTICS & APP</span><span style='color:#00e676; font-family:monospace; font-size:10px;'>DBT + APPS</span></div><div class="flow-node-desc"><b>dbt</b> exécute 8 modèles & 53 tests dans BigQuery (staging → marts).<br><b>Streamlit</b> expose les métriques et les tests statistiques en temps réel.</div><div class="flow-node-sub">Query: Bigtable / BigQuery</div></div></div></div>""", unsafe_allow_html=True)