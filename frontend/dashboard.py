import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys, os
from scipy import stats

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
from bigtable_client import get_latest_prices

st.set_page_config(page_title="Price Intelligence", layout="wide", page_icon=None)

st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background-color: #0f1117; }
[data-testid="stSidebar"] { background-color: #161b2e; border-right: 1px solid #1e2a40; }
[data-testid="stSidebar"] * { color: #9ca3af !important; }
[data-testid="metric-container"] { background: #161b2e; border: 1px solid #1e2a40; border-radius: 10px; padding: 14px; }
[data-testid="stMetricLabel"] { color: #6b7280 !important; font-size: 11px !important; text-transform: uppercase; letter-spacing: 0.5px; }
[data-testid="stMetricValue"] { color: #ffffff !important; font-size: 22px !important; }
h1, h2, h3 { color: #ffffff !important; font-weight: 500 !important; }
.stDataFrame { background: #161b2e; border: 1px solid #1e2a40; border-radius: 10px; }
.block-container { padding-top: 2rem; }
div[data-testid="stHorizontalBlock"] { gap: 12px; }
[data-testid="stPlotlyChart"] { background: #161b2e; border: 1px solid #1e2a40; border-radius: 10px; padding: 12px; }
</style>
""", unsafe_allow_html=True)

DARK_LAYOUT = dict(
    paper_bgcolor='#161b2e',
    plot_bgcolor='#161b2e',
    font=dict(color='#9ca3af', size=12),
    title_font=dict(color='#ffffff', size=14),
    xaxis=dict(gridcolor='#1e2a40', color='#6b7280'),
    yaxis=dict(gridcolor='#1e2a40', color='#6b7280'),
    legend=dict(bgcolor='#161b2e', bordercolor='#1e2a40', font=dict(color='#9ca3af')),
    margin=dict(l=40, r=20, t=40, b=40)
)
COLORS = ['#60a5fa', '#4ade80', '#a78bfa', '#f87171', '#fbbf24']

st.markdown("<h1 style='font-size:24px;margin-bottom:4px'>Price Intelligence Platform</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#6b7280;font-size:13px;margin-bottom:24px'>E-commerce price monitoring — Amazon FR · Jumia MA · Electroplanet</p>", unsafe_allow_html=True)

df = get_latest_prices()

if df.empty:
    st.error("Aucune donnée trouvée.")
    st.stop()

# Sidebar
st.sidebar.markdown("### Filtres")
platforms = ["Tous"] + sorted(df['platform'].dropna().unique().tolist())
selected_platform = st.sidebar.selectbox("Plateforme", platforms)
brands = ["Tous"] + sorted(df['brand'].dropna().unique().tolist())
selected_brand = st.sidebar.selectbox("Marque", brands)

filtered = df.copy()
if selected_platform != "Tous":
    filtered = filtered[filtered['platform'] == selected_platform]
if selected_brand != "Tous":
    filtered = filtered[filtered['brand'] == selected_brand]

# KPIs
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Prix moyen",   f"€{filtered['price'].mean():,.0f}")
c2.metric("Prix min",     f"€{filtered['price'].min():,.2f}")
c3.metric("Prix max",     f"€{filtered['price'].max():,.0f}")
c4.metric("Produits",     len(filtered))
c5.metric("Plateformes",  filtered['platform'].nunique())

st.markdown("<div style='margin:24px 0 0'></div>", unsafe_allow_html=True)

# Charts row 1
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Distribution des prix par plateforme")
    fig = px.box(filtered, x='platform', y='price', color='platform',
                 color_discrete_sequence=COLORS)
    fig.update_layout(**DARK_LAYOUT)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("#### Prix moyen par marque")
    avg = filtered.groupby('brand')['price'].mean().reset_index().sort_values('price', ascending=False).head(10)
    fig2 = px.bar(avg, x='brand', y='price', color='brand',
                  color_discrete_sequence=COLORS)
    fig2.update_layout(**DARK_LAYOUT, showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

# Charts row 2
st.markdown("#### Comparaison prix par marque et plateforme")
pivot = filtered.groupby(['brand', 'platform'])['price'].mean().reset_index()
fig3 = px.bar(pivot, x='brand', y='price', color='platform',
              barmode='group', color_discrete_sequence=COLORS)
fig3.update_layout(**DARK_LAYOUT)
st.plotly_chart(fig3, use_container_width=True)

# Stats descriptives
st.markdown("#### Statistiques descriptives")
col_s1, col_s2 = st.columns(2)
with col_s1:
    st.markdown("<p style='color:#60a5fa;font-size:12px;text-transform:uppercase;letter-spacing:0.5px'>Par plateforme</p>", unsafe_allow_html=True)
    st.dataframe(filtered.groupby('platform')['price'].describe().round(2), use_container_width=True)
with col_s2:
    st.markdown("<p style='color:#a78bfa;font-size:12px;text-transform:uppercase;letter-spacing:0.5px'>Par marque</p>", unsafe_allow_html=True)
    st.dataframe(filtered.groupby('brand')['price'].describe().round(2), use_container_width=True)

# Données brutes
st.markdown("#### Données brutes")
st.dataframe(
    filtered[['name','brand','model','price','currency','platform','timestamp']]
    .sort_values('price', ascending=False),
    use_container_width=True
)