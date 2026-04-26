import streamlit as st
import plotly.express as px
import pandas as pd
import sys, os
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))
from bigtable_client import get_latest_prices

st.set_page_config(page_title="Pipeline Status", layout="wide")

st.markdown("""
<style>
[data-testid="stAppViewContainer"]{background:#0f1117}
[data-testid="stSidebar"]{background:#161b2e;border-right:1px solid #1e2a40}
[data-testid="metric-container"]{background:#161b2e;border:1px solid #1e2a40;border-radius:10px;padding:14px}
[data-testid="stMetricLabel"]{color:#6b7280!important;font-size:11px!important;text-transform:uppercase;letter-spacing:.5px}
[data-testid="stMetricValue"]{color:#fff!important;font-size:22px!important}
h1,h2,h3,h4{color:#fff!important;font-weight:500!important}
p{color:#9ca3af}
.block-container{padding-top:2rem}
</style>
""", unsafe_allow_html=True)

COLORS = ['#60a5fa','#4ade80','#a78bfa']

st.markdown("<h1 style='font-size:26px;margin-bottom:2px'>Pipeline Status</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#6b7280;font-size:13px;margin-bottom:20px'>Architecture · Ingestion · Qualité des données</p>", unsafe_allow_html=True)

df = get_latest_prices()

# Status des composants
st.markdown("### Statut des composants")
comp = st.columns(4)
comp[0].markdown("<div style='background:#161b2e;border:1px solid #1e2a40;border-radius:10px;padding:14px;text-align:center'><div style='font-size:11px;color:#6b7280;text-transform:uppercase;letter-spacing:.5px;margin-bottom:8px'>Scrapy</div><div style='color:#4ade80;font-size:13px;font-weight:500'>Actif</div></div>", unsafe_allow_html=True)
comp[1].markdown("<div style='background:#161b2e;border:1px solid #1e2a40;border-radius:10px;padding:14px;text-align:center'><div style='font-size:11px;color:#6b7280;text-transform:uppercase;letter-spacing:.5px;margin-bottom:8px'>Airflow</div><div style='color:#4ade80;font-size:13px;font-weight:500'>Actif</div></div>", unsafe_allow_html=True)
comp[2].markdown("<div style='background:#161b2e;border:1px solid #1e2a40;border-radius:10px;padding:14px;text-align:center'><div style='font-size:11px;color:#fbbf24;text-transform:uppercase;letter-spacing:.5px;margin-bottom:8px'>NiFi</div><div style='color:#fbbf24;font-size:13px;font-weight:500'>En attente</div></div>", unsafe_allow_html=True)
comp[3].markdown("<div style='background:#161b2e;border:1px solid #1e2a40;border-radius:10px;padding:14px;text-align:center'><div style='font-size:11px;color:#6b7280;text-transform:uppercase;letter-spacing:.5px;margin-bottom:8px'>Bigtable</div><div style='color:#fbbf24;font-size:13px;font-weight:500'>En attente</div></div>", unsafe_allow_html=True)

st.markdown("<div style='margin:20px 0'></div>", unsafe_allow_html=True)

# Métriques ingestion
st.markdown("### Ingestion des données")
m1,m2,m3,m4 = st.columns(4)
m1.metric("Total enregistrements", len(df))
m2.metric("Amazon FR",      len(df[df['platform']=='amazon_fr']))
m3.metric("Jumia MA",       len(df[df['platform']=='jumia_ma']))
m4.metric("Electroplanet",  len(df[df['platform']=='electroplanet']))

st.markdown("<div style='margin:16px 0'></div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown("#### Répartition par plateforme")
    pie_data = df.groupby('platform').size().reset_index(name='count')
    fig = px.pie(pie_data, values='count', names='platform',
                 color_discrete_sequence=COLORS, hole=0.4)
    fig.update_layout(paper_bgcolor='#161b2e', plot_bgcolor='#161b2e',
                      font=dict(color='#9ca3af'),
                      legend=dict(bgcolor='#161b2e', font=dict(color='#9ca3af')),
                      margin=dict(l=20,r=20,t=20,b=20))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("#### Répartition par marque")
    brand_data = df.groupby('brand').size().reset_index(name='count').sort_values('count',ascending=False).head(5)
    fig2 = px.bar(brand_data, x='brand', y='count', color='brand',
                  color_discrete_sequence=COLORS)
    fig2.update_layout(paper_bgcolor='#161b2e', plot_bgcolor='#161b2e',
                       font=dict(color='#9ca3af'),
                       xaxis=dict(gridcolor='#1e2a40',color='#6b7280'),
                       yaxis=dict(gridcolor='#1e2a40',color='#6b7280'),
                       showlegend=False, margin=dict(l=40,r=20,t=20,b=40))
    fig2.update_traces(marker_line_width=0)
    st.plotly_chart(fig2, use_container_width=True)

# Qualité des données
st.markdown("### Qualité des données")
total = len(df)
q1,q2,q3,q4 = st.columns(4)
missing_price = df['price'].isna().sum()
missing_brand = df['brand'].isna().sum()
has_price     = total - missing_price
completeness  = round((has_price/total)*100, 1)

q1.metric("Complétude prix",   f"{completeness}%")
q2.metric("Prix manquants",    missing_price)
q3.metric("Marques manquantes",missing_brand)
q4.metric("Doublons",          df.duplicated(subset=['name','platform']).sum())

st.markdown("#### Architecture du pipeline")
st.markdown("""
<div style='background:#161b2e;border:1px solid #1e2a40;border-radius:10px;padding:20px;font-size:13px;color:#9ca3af;line-height:2'>
<span style='color:#60a5fa;font-weight:500'>Scrapy + Selenium</span>
&nbsp;→&nbsp;
<span style='color:#4ade80;font-weight:500'>Apache NiFi (streaming)</span>
&nbsp;→&nbsp;
<span style='color:#a78bfa;font-weight:500'>Apache Airflow (batch)</span>
&nbsp;→&nbsp;
<span style='color:#fbbf24;font-weight:500'>Google Bigtable</span>
&nbsp;→&nbsp;
<span style='color:#f87171;font-weight:500'>dbt (transformations)</span>
&nbsp;→&nbsp;
<span style='color:#60a5fa;font-weight:500'>Dashboard Streamlit</span>
</div>
""", unsafe_allow_html=True)