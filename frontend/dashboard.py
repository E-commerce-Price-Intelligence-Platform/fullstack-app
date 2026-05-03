import streamlit as st
import plotly.express as px
import pandas as pd
import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
from bigtable_client import get_latest_prices

st.set_page_config(page_title="Price Intelligence", layout="wide", page_icon=None)

st.markdown("""
<style>
[data-testid="stAppViewContainer"]{background:#0f1117}
[data-testid="stSidebar"]{background:#161b2e;border-right:1px solid #1e2a40}
[data-testid="stSidebar"] label,[data-testid="stSidebar"] p{color:#9ca3af!important}
[data-testid="stSidebar"] .stSelectbox div{background:#1e2a40;color:#e0e0e0}
[data-testid="metric-container"]{background:#161b2e;border:1px solid #1e2a40;border-radius:10px;padding:14px}
[data-testid="stMetricLabel"]{color:#6b7280!important;font-size:11px!important;text-transform:uppercase;letter-spacing:.5px}
[data-testid="stMetricValue"]{color:#fff!important;font-size:22px!important}
h1,h2,h3,h4{color:#fff!important;font-weight:500!important}
p{color:#9ca3af}
.block-container{padding-top:2rem}
iframe{border-radius:10px}
</style>
""", unsafe_allow_html=True)

COLORS = ['#60a5fa','#4ade80','#a78bfa','#f87171','#fbbf24']
DARK = dict(
    paper_bgcolor='#161b2e', plot_bgcolor='#161b2e',
    font=dict(color='#9ca3af',size=12),
    title_font=dict(color='#fff',size=14),
    xaxis=dict(gridcolor='#1e2a40',color='#6b7280',linecolor='#1e2a40'),
    yaxis=dict(gridcolor='#1e2a40',color='#6b7280',linecolor='#1e2a40'),
    legend=dict(bgcolor='#161b2e',bordercolor='#1e2a40',font=dict(color='#9ca3af')),
    margin=dict(l=40,r=20,t=40,b=40)
)

st.markdown("<h1 style='font-size:26px;margin-bottom:2px'>Price Intelligence Platform</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#6b7280;font-size:13px;margin-bottom:20px'>Amazon FR &nbsp;·&nbsp; Jumia MA &nbsp;·&nbsp; Electroplanet</p>", unsafe_allow_html=True)

df = get_latest_prices()
if df.empty:
    st.error("Aucune donnée trouvée.")
    st.stop()

# Sidebar
st.sidebar.markdown("<h3 style='color:#fff!important'>Filtres</h3>", unsafe_allow_html=True)
platforms = ["Tous"] + sorted(df['platform'].dropna().unique().tolist())
brands    = ["Tous"] + sorted(df['brand'].dropna().unique().tolist())
sel_p = st.sidebar.selectbox("Plateforme", platforms)
sel_b = st.sidebar.selectbox("Marque", brands)

f = df.copy()
if sel_p != "Tous": f = f[f['platform']==sel_p]
if sel_b != "Tous": f = f[f['brand']==sel_b]

# Badge LIVE
st.sidebar.markdown("<br><div style='background:#1a2a1a;border:1px solid #2a4a2a;border-radius:20px;padding:4px 12px;display:inline-block;color:#4ade80;font-size:11px'>LIVE</div>", unsafe_allow_html=True)

# KPIs
c1,c2,c3,c4,c5 = st.columns(5)
c1.metric("Prix moyen",  f"€{f['price'].mean():,.0f}")
c2.metric("Prix min",    f"€{f['price'].min():,.2f}")
c3.metric("Prix max",    f"€{f['price'].max():,.0f}")
c4.metric("Produits",    f"{len(f)}")
c5.metric("Plateformes", f"{f['platform'].nunique()}")

st.markdown("<div style='margin:20px 0'></div>", unsafe_allow_html=True)

# Row 1 charts
col1, col2 = st.columns(2)
with col1:
    st.markdown("#### Prix moyen par plateforme")
    avg_p = f.groupby('platform')['price'].mean().reset_index()
    fig = px.bar(avg_p, x='platform', y='price', color='platform',
                 color_discrete_sequence=COLORS)
    fig.update_layout(**DARK, showlegend=False)
    fig.update_traces(marker_line_width=0)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("#### Prix moyen par marque")
    avg_b = f.groupby('brand')['price'].mean().reset_index().sort_values('price',ascending=False).head(10)
    fig2 = px.bar(avg_b, x='brand', y='price', color='brand',
                  color_discrete_sequence=COLORS)
    fig2.update_layout(**DARK, showlegend=False)
    fig2.update_traces(marker_line_width=0)
    st.plotly_chart(fig2, use_container_width=True)

# Row 2
col3, col4 = st.columns(2)
with col3:
    st.markdown("#### Distribution des prix")
    fig3 = px.box(f, x='platform', y='price', color='platform',
                  color_discrete_sequence=COLORS)
    fig3.update_layout(**DARK, showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.markdown("#### Comparaison par marque et plateforme")
    pivot = f.groupby(['brand','platform'])['price'].mean().reset_index()
    fig4 = px.bar(pivot, x='brand', y='price', color='platform',
                  barmode='group', color_discrete_sequence=COLORS)
    fig4.update_layout(**DARK)
    fig4.update_traces(marker_line_width=0)
    st.plotly_chart(fig4, use_container_width=True)

# Stats + Table
st.markdown("#### Statistiques descriptives")
cs1, cs2 = st.columns(2)
with cs1:
    st.markdown("<p style='color:#60a5fa;font-size:11px;text-transform:uppercase;letter-spacing:.5px'>Par plateforme</p>", unsafe_allow_html=True)
    st.dataframe(f.groupby('platform')['price'].describe().round(2), use_container_width=True)
with cs2:
    st.markdown("<p style='color:#a78bfa;font-size:11px;text-transform:uppercase;letter-spacing:.5px'>Par marque</p>", unsafe_allow_html=True)
    st.dataframe(f.groupby('brand')['price'].describe().round(2), use_container_width=True)

st.markdown("#### Données brutes")
st.dataframe(f[['name','brand','model','price','currency','platform','timestamp']].sort_values('price',ascending=False), use_container_width=True)
import time
time.sleep(30)
st.rerun()