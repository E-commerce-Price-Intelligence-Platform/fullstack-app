import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys, os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, 'backend'))
from bigtable_client import get_latest_prices

st.markdown("""
<style>
[data-testid="stAppViewContainer"]{background:#0f1117}
[data-testid="stSidebar"]{background:#161b2e;border-right:1px solid #1e2a40}
[data-testid="stSidebar"] label,[data-testid="stSidebar"] p{color:#9ca3af!important}
[data-testid="metric-container"]{background:#161b2e;border:1px solid #1e2a40;border-radius:10px;padding:14px}
[data-testid="stMetricLabel"]{color:#6b7280!important;font-size:11px!important;text-transform:uppercase;letter-spacing:.5px}
[data-testid="stMetricValue"]{color:#fff!important;font-size:22px!important}
h1,h2,h3,h4{color:#fff!important;font-weight:500!important}
p{color:#9ca3af}
.block-container{padding-top:2rem}
</style>
""", unsafe_allow_html=True)

COLORS = ['#60a5fa','#4ade80','#a78bfa','#f87171','#fbbf24']
DARK = dict(
    paper_bgcolor='#161b2e', plot_bgcolor='#161b2e',
    font=dict(color='#9ca3af',size=12),
    title_font=dict(color='#fff',size=14),
    xaxis=dict(gridcolor='#1e2a40',color='#6b7280'),
    yaxis=dict(gridcolor='#1e2a40',color='#6b7280'),
    legend=dict(bgcolor='#161b2e',bordercolor='#1e2a40'),
    margin=dict(l=40,r=20,t=40,b=40)
)

st.markdown("<h1 style='font-size:26px;margin-bottom:2px'>Comparaison Produits</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#6b7280;font-size:13px;margin-bottom:20px'>Recherche et compare un produit sur toutes les plateformes</p>", unsafe_allow_html=True)

df = get_latest_prices()
if df.empty:
    st.error("Aucune donnée.")
    st.stop()

# Recherche
search = st.text_input("Rechercher un produit", placeholder="ex: Samsung Galaxy S25, iPhone...")

if search:
    results = df[df['name'].str.contains(search, case=False, na=False)]
    if results.empty:
        st.warning(f"Aucun produit trouvé pour '{search}'")
    else:
        st.markdown(f"<p style='color:#4ade80;font-size:13px'>{len(results)} produits trouvés</p>", unsafe_allow_html=True)

        # KPIs
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Prix moyen",  f"€{results['price'].mean():,.0f}")
        c2.metric("Prix min",    f"€{results['price'].min():,.0f}")
        c3.metric("Prix max",    f"€{results['price'].max():,.0f}")
        c4.metric("Résultats",   len(results))

        st.markdown("<div style='margin:16px 0'></div>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            avg = results.groupby('platform')['price'].mean().reset_index()
            fig = px.bar(avg, x='platform', y='price', color='platform',
                         color_discrete_sequence=COLORS,
                         title=f"Prix moyen pour '{search}' par plateforme")
            fig.update_layout(**DARK, showlegend=False)
            fig.update_traces(marker_line_width=0)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig2 = px.box(results, x='platform', y='price', color='platform',
                          color_discrete_sequence=COLORS,
                          title="Distribution des prix")
            fig2.update_layout(**DARK, showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("#### Résultats détaillés")
        st.dataframe(
            results[['name','brand','model','price','currency','platform','timestamp']]
            .sort_values('price'),
            use_container_width=True
        )
else:
    # Top produits par défaut
    st.markdown("#### Top 10 produits les plus chers")
    top = df.nlargest(10, 'price')[['name','brand','price','platform','currency']]
    fig = px.bar(top, x='price', y='name', color='platform',
                 orientation='h', color_discrete_sequence=COLORS)
    fig.update_layout(**DARK)
    fig.update_traces(marker_line_width=0)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Top 10 produits les moins chers")
    bottom = df.nsmallest(10, 'price')[['name','brand','price','platform','currency']]
    fig2 = px.bar(bottom, x='price', y='name', color='platform',
                  orientation='h', color_discrete_sequence=COLORS)
    fig2.update_layout(**DARK)
    fig2.update_traces(marker_line_width=0)
    st.plotly_chart(fig2, use_container_width=True)