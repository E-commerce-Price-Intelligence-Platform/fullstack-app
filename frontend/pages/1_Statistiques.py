import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np 
from scipy import stats
import sys, os
st.write("TEST - page chargée")
st.write(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'backend'))
from bigtable_client import get_latest_prices

st.set_page_config(page_title="Statistiques", layout="wide")
st.markdown("""
<style>
[data-testid="stAppViewContainer"]{background:#0f1117}
[data-testid="stSidebar"]{background:#161b2e;border-right:1px solid #1e2a40}
[data-testid="metric-container"]{background:#161b2e;border:1px solid #1e2a40;border-radius:10px;padding:14px}
[data-testid="stMetricLabel"]{color:#6b7280!important;font-size:11px!important;text-transform:uppercase;letter-spacing:.5px}
[data-testid="stMetricValue"]{color:#fff!important;font-size:22px!important}
h1,h2,h3,h4{color:#fff!important;font-weight:500!important}
p{color:#9ca3af}.block-container{padding-top:2rem}
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

st.markdown("<h1 style='font-size:26px;margin-bottom:2px'>Analyse Statistique</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#6b7280;font-size:13px;margin-bottom:20px'>Tests inférentiels · Intervalles de confiance · ANOVA</p>", unsafe_allow_html=True)

df = get_latest_prices()
if df.empty:
    st.error("Aucune donnée.")
    st.stop()

st.markdown("### 1. Statistiques descriptives")
c1,c2,c3,c4 = st.columns(4)
c1.metric("Moyenne globale", f"€{df['price'].mean():,.0f}")
c2.metric("Médiane",         f"€{df['price'].median():,.0f}")
c3.metric("Écart-type",      f"€{df['price'].std():,.0f}")
c4.metric("Variance",        f"€{df['price'].var():,.0f}")

st.markdown("<div style='margin:16px 0'></div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    fig = px.histogram(df, x='price', color='platform',
                       nbins=40, color_discrete_sequence=COLORS,
                       title="Distribution des prix")
    fig.update_layout(**DARK)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig2 = px.violin(df, x='platform', y='price', color='platform',
                     color_discrete_sequence=COLORS, box=True,
                     title="Violin plot par plateforme")
    fig2.update_layout(**DARK, showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("### 2. T-test — Comparaison de deux plateformes")
platforms = sorted(df['platform'].dropna().unique().tolist())
tc1, tc2 = st.columns(2)
p1 = tc1.selectbox("Plateforme A", platforms, index=0)
p2 = tc2.selectbox("Plateforme B", platforms, index=min(1,len(platforms)-1))

g1 = df[df['platform']==p1]['price'].dropna()
g2 = df[df['platform']==p2]['price'].dropna()

if len(g1) > 1 and len(g2) > 1 and p1 != p2:
    t_stat, p_val = stats.ttest_ind(g1, g2)
    ci1 = stats.t.interval(0.95, len(g1)-1, loc=g1.mean(), scale=stats.sem(g1))
    ci2 = stats.t.interval(0.95, len(g2)-1, loc=g2.mean(), scale=stats.sem(g2))

    r1,r2,r3,r4 = st.columns(4)
    r1.metric("T-statistic",  f"{t_stat:.4f}")
    r2.metric("P-value",      f"{p_val:.4f}")
    r3.metric(f"IC 95% {p1}", f"[{ci1[0]:,.0f} – {ci1[1]:,.0f}]")
    r4.metric(f"IC 95% {p2}", f"[{ci2[0]:,.0f} – {ci2[1]:,.0f}]")

    if p_val < 0.05:
        st.markdown(f"<div style='background:#1a2a1a;border:1px solid #2a4a2a;border-radius:8px;padding:12px 16px;color:#4ade80;font-size:13px'>Différence significative (p={p_val:.4f} &lt; 0.05)</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='background:#1a1a2a;border:1px solid #2a2a4a;border-radius:8px;padding:12px 16px;color:#a78bfa;font-size:13px'>Pas de différence significative (p={p_val:.4f} &gt; 0.05)</div>", unsafe_allow_html=True)

    fig3 = go.Figure()
    for grp, color, name in [(g1,'#60a5fa',p1),(g2,'#4ade80',p2)]:
        fig3.add_trace(go.Box(y=grp, name=name, marker_color=color, boxmean=True))
    fig3.update_layout(**DARK, title="Comparaison des distributions")
    st.plotly_chart(fig3, use_container_width=True)

st.markdown("### 3. ANOVA — Variation des prix par marque")
groups = [g['price'].dropna().values for _, g in df.groupby('brand') if len(g) > 2]
if len(groups) >= 2:
    f_stat, p_anova = stats.f_oneway(*groups)
    a1, a2 = st.columns(2)
    a1.metric("F-statistic",   f"{f_stat:.4f}")
    a2.metric("P-value ANOVA", f"{p_anova:.4f}")

    if p_anova < 0.05:
        st.markdown("<div style='background:#1a2a1a;border:1px solid #2a4a2a;border-radius:8px;padding:12px 16px;color:#4ade80;font-size:13px'>ANOVA significative — Différences de prix entre marques.</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='background:#1a1a2a;border:1px solid #2a2a4a;border-radius:8px;padding:12px 16px;color:#a78bfa;font-size:13px'>ANOVA non significative.</div>", unsafe_allow_html=True)

    avg_brand = df.groupby('brand')['price'].mean().reset_index().sort_values('price',ascending=False)
    fig4 = px.bar(avg_brand, x='brand', y='price', color='brand',
                  color_discrete_sequence=COLORS, title="Prix moyen par marque")
    fig4.update_layout(**DARK, showlegend=False)
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("### 4. Intervalles de confiance (95%)")
ci_data = []
for platform, grp in df.groupby('platform'):
    prices = grp['price'].dropna()
    if len(prices) > 1:
        ci = stats.t.interval(0.95, len(prices)-1, loc=prices.mean(), scale=stats.sem(prices))
        ci_data.append({'Plateforme': platform, 'Moyenne': prices.mean(), 'IC_bas': ci[0], 'IC_haut': ci[1]})

if ci_data:
    ci_df = pd.DataFrame(ci_data)
    fig5 = go.Figure()
    for i, row in ci_df.iterrows():
        fig5.add_trace(go.Scatter(
            x=[row['IC_bas'], row['Moyenne'], row['IC_haut']],
            y=[row['Plateforme']]*3,
            mode='lines+markers',
            name=row['Plateforme'],
            marker=dict(size=[8,14,8], color=COLORS[i]),
            line=dict(color=COLORS[i], width=2)
        ))
    fig5.update_layout(**DARK, title="Intervalles de confiance à 95%",
                       xaxis_title="Prix (€)", yaxis_title="")
    st.plotly_chart(fig5, use_container_width=True)
    st.markdown("### 5. Régression linéaire — price ~ brand + platform")

import statsmodels.api as sm

reg_df = df.copy()
reg_df['brand_code'] = pd.Categorical(reg_df['brand']).codes
reg_df['platform_code'] = pd.Categorical(reg_df['platform']).codes
reg_df = reg_df[['price','brand_code','platform_code']].dropna()

if len(reg_df) > 10:
    X = sm.add_constant(reg_df[['brand_code','platform_code']])
    y = reg_df['price']
    model = sm.OLS(y, X).fit()

    r1, r2, r3 = st.columns(3)
    r1.metric("R²",          f"{model.rsquared:.4f}")
    r2.metric("F-statistic", f"{model.fvalue:.4f}")
    r3.metric("P-value",     f"{model.f_pvalue:.4f}")

    if model.rsquared > 0.5:
        st.markdown("<div style='background:#1a2a1a;border:1px solid #2a4a2a;border-radius:8px;padding:12px 16px;color:#4ade80;font-size:13px'>Modèle significatif — la marque et la plateforme expliquent bien les variations de prix.</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='background:#1a1a2a;border:1px solid #2a2a4a;border-radius:8px;padding:12px 16px;color:#a78bfa;font-size:13px'>Modèle partiel — d'autres facteurs influencent les prix.</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<p style='color:#60a5fa;font-size:11px;text-transform:uppercase;letter-spacing:.5px'>Résumé du modèle</p>", unsafe_allow_html=True)
        st.text(model.summary().as_text())
    with col2:
        fig = px.scatter(reg_df, x='brand_code', y='price',
                        trendline='ols',
                        color_discrete_sequence=['#60a5fa'],
                        title="Price vs Brand")
        fig.update_layout(**DARK)
        st.plotly_chart(fig, use_container_width=True)