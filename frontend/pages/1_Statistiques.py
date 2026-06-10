import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np 
from scipy import stats
import statsmodels.api as sm
import sys
import os

# Inject path to backend
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))
from bigtable_client import get_latest_prices

# Import design tokens and helper functions
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from theme import (
    inject_custom_css, apply_plotly_theme, standardize_currency,
    render_kpi, render_alert, ICONS, COLOR_CYAN, COLOR_PURPLE,
    COLOR_AMBER, COLOR_GREEN, COLOR_RED
)

# Page configuration
st.set_page_config(page_title="Statistiques", layout="wide")

# Inject CSS styles
inject_custom_css()

# Fetch raw data
df_raw = get_latest_prices()
if df_raw.empty:
    st.error("Aucune donnée disponible pour l'analyse.")
    st.stop()

# ── Sidebar Filter & Currency ──────────────────────────────────
st.sidebar.markdown("""
<div style='padding: 10px 0; border-bottom: 1px solid rgba(0, 0, 0, 0.08); margin-bottom: 20px;'>
    <h2 style='color:#0B0F19; font-size:18px; margin:0; font-weight:700; letter-spacing:1px;'>STATISTIQUES</h2>
    <p style='color:#64748B; font-size:11px; margin:4px 0 0 0;'>Analysis Control Center</p>
</div>
""", unsafe_allow_html=True)

currency_choice = st.sidebar.selectbox(
    "Devise d'affichage",
    ["Moroccan Dirham (MAD)", "Euro (EUR)"]
)
target_currency = "EUR" if "EUR" in currency_choice else "MAD"
currency_symbol = "€" if target_currency == "EUR" else "DH"

# Standardize currency
df = standardize_currency(df_raw, target_currency)

# ── Header ──────────────────────────────────────────────────
st.markdown(f"""
<div style='background: linear-gradient(135deg, #FFFFFF 0%, #F3F4F6 100%); border: 1.5px solid rgba(0, 0, 0, 0.08); border-radius: 12px; padding: 24px; margin-bottom: 24px; box-shadow: 0 4px 20px rgba(0,0,0,0.05);'>
    <h1 style='font-size:28px; margin:0; font-weight:700; color:#0B0F19; background: linear-gradient(90deg, #0B0F19, #7c3aed); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>ANALYSE STATISTIQUE INFERENTIELLE</h1>
    <p style='color:#64748B; font-size:13px; margin:8px 0 0 0; line-height: 1.5;'>
        Tests d'hypothèses · Intervalles de confiance · ANOVA · Analyse de régression linéaire multi-factorielle.
    </p>
</div>
""", unsafe_allow_html=True)

# ── 1. Descriptive Stats ────────────────────────────────────
st.markdown("### 1. Statistiques Descriptives Globales")
c1, c2, c3, c4 = st.columns(4)
with c1:
    render_kpi("Moyenne Globale", f"{df['price'].mean():,.0f} {currency_symbol}", "price", "Indicateur central")
with c2:
    render_kpi("Médiane", f"{df['price'].median():,.0f} {currency_symbol}", "platforms", "50% de la distribution")
with c3:
    render_kpi("Écart-type", f"{df['price'].std():,.0f} {currency_symbol}", "max_price", "Dispersion des prix")
with c4:
    render_kpi("Variance", f"{df['price'].var():,.0f} {currency_symbol}²", "min_price", "Variabilité globale")

st.markdown("<div style='margin:16px 0'></div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    fig = px.histogram(
        df,
        x='price',
        color='platform',
        nbins=40,
        color_discrete_sequence=[COLOR_CYAN, COLOR_PURPLE, COLOR_AMBER, COLOR_GREEN, COLOR_RED],
        title="Distribution des Prix"
    )
    apply_plotly_theme(fig)
    fig.update_layout(
        xaxis_title=f"Prix ({currency_symbol})",
        yaxis_title="Nombre de produits",
        legend_title="Plateforme"
    )
    st.plotly_chart(fig, use_container_width=True, theme=None)

with col2:
    fig2 = px.violin(
        df,
        x='platform',
        y='price',
        color='platform',
        color_discrete_sequence=[COLOR_CYAN, COLOR_PURPLE, COLOR_AMBER, COLOR_GREEN, COLOR_RED],
        box=True,
        title="Violin Plot par Plateforme"
    )
    apply_plotly_theme(fig2)
    fig2.update_layout(
        showlegend=False,
        yaxis_title=f"Prix ({currency_symbol})",
        xaxis_title="Plateforme"
    )
    st.plotly_chart(fig2, use_container_width=True, theme=None)

st.markdown("<div style='margin:20px 0'></div>", unsafe_allow_html=True)

# ── 2. T-Test ───────────────────────────────────────────────
st.markdown("### 2. Test de Student (T-test) — Comparaison Bivariée")
platforms = sorted(df['platform'].dropna().unique().tolist())

tc1, tc2 = st.columns(2)
with tc1:
    p1 = st.selectbox("Plateforme A (Référence)", platforms, index=0)
with tc2:
    p2 = st.selectbox("Plateforme B (Comparaison)", platforms, index=min(1, len(platforms)-1))

g1 = df[df['platform'] == p1]['price'].dropna()
g2 = df[df['platform'] == p2]['price'].dropna()

if p1 == p2:
    render_alert("Veuillez sélectionner deux plateformes différentes pour exécuter le test de Student.", type="warning", icon="alert")
elif len(g1) <= 1 or len(g2) <= 1:
    render_alert("Données insuffisantes pour exécuter le T-test sur l'une des plateformes sélectionnées.", type="warning", icon="alert")
else:
    t_stat, p_val = stats.ttest_ind(g1, g2)
    ci1 = stats.t.interval(0.95, len(g1)-1, loc=g1.mean(), scale=stats.sem(g1))
    ci2 = stats.t.interval(0.95, len(g2)-1, loc=g2.mean(), scale=stats.sem(g2))

    r1, r2, r3, r4 = st.columns(4)
    with r1:
        render_kpi("T-statistic", f"{t_stat:.4f}", "activity", "Force de l'écart")
    with r2:
        render_kpi("P-value", f"{p_val:.4f}", "platforms", "Seuil de décision")
    with r3:
        render_kpi(f"IC 95% {p1}", f"[{ci1[0]:,.0f} – {ci1[1]:,.0f}] {currency_symbol}", "price", "Intervalle Plateforme A")
    with r4:
        render_kpi(f"IC 95% {p2}", f"[{ci2[0]:,.0f} – {ci2[1]:,.0f}] {currency_symbol}", "price", "Intervalle Plateforme B")

    if p_val < 0.05:
        render_alert(
            f"**Différence Statistiquement Significative (p = {p_val:.4f} < 0.05)** : Nous rejetons l'hypothèse nulle (H0). Les prix moyens entre {p1} (m={g1.mean():,.0f} {currency_symbol}) et {p2} (m={g2.mean():,.0f} {currency_symbol}) sont structurellement différents dans notre marché.",
            type="success", icon="check"
        )
    else:
        render_alert(
            f"**Différence Non Significative (p = {p_val:.4f} >= 0.05)** : Nous ne pouvons pas rejeter l'hypothèse nulle (H0). La différence observée entre {p1} (m={g1.mean():,.0f} {currency_symbol}) et {p2} (m={g2.mean():,.0f} {currency_symbol}) peut s'expliquer par de simples fluctuations aléatoires.",
            type="warning", icon="alert"
        )

    fig3 = go.Figure()
    fig3.add_trace(go.Box(y=g1, name=p1, marker_color=COLOR_CYAN, boxmean=True))
    fig3.add_trace(go.Box(y=g2, name=p2, marker_color=COLOR_PURPLE, boxmean=True))
    apply_plotly_theme(fig3)
    fig3.update_layout(
        title=f"Comparaison de Distribution des Prix : {p1} vs {p2}",
        yaxis_title=f"Prix ({currency_symbol})"
    )
    st.plotly_chart(fig3, use_container_width=True, theme=None)

st.markdown("<div style='margin:20px 0'></div>", unsafe_allow_html=True)

# ── 3. ANOVA ────────────────────────────────────────────────
st.markdown("### 3. Analyse de Variance (ANOVA) — Effet de la Marque")
groups = [g['price'].dropna().values for _, g in df.groupby('brand') if len(g) > 2]

if len(groups) < 2:
    render_alert("Données de marque insuffisantes (au moins 2 marques avec plus de 2 smartphones) pour effectuer l'ANOVA.", type="warning", icon="alert")
else:
    f_stat, p_anova = stats.f_oneway(*groups)
    a1, a2 = st.columns(2)
    with a1:
        render_kpi("F-statistic", f"{f_stat:.4f}", "activity", "Ratio des variances")
    with a2:
        render_kpi("P-value ANOVA", f"{p_anova:.4f}", "platforms", "Seuil de décision")

    if p_anova < 0.05:
        render_alert(
            f"**Effet Marque Significatif (p = {p_anova:.4f} < 0.05)** : La marque a un impact statistiquement significatif sur le prix des smartphones. Les moyennes des prix diffèrent d'une marque à l'autre.",
            type="success", icon="check"
        )
    else:
        render_alert(
            f"**Effet Marque Non Significatif (p = {p_anova:.4f} >= 0.05)** : Les prix moyens des smartphones ne présentent pas de variations significatives selon les marques collectées.",
            type="warning", icon="alert"
        )

    avg_brand = df.groupby('brand')['price'].mean().reset_index().sort_values('price', ascending=False)
    fig4 = px.bar(
        avg_brand,
        x='brand',
        y='price',
        color='brand',
        color_discrete_sequence=[COLOR_CYAN, COLOR_PURPLE, COLOR_AMBER, COLOR_GREEN, COLOR_RED],
        title="Prix Moyen par Marque"
    )
    apply_plotly_theme(fig4)
    fig4.update_layout(
        showlegend=False,
        yaxis_title=f"Prix Moyen ({currency_symbol})",
        xaxis_title="Marque"
    )
    st.plotly_chart(fig4, use_container_width=True, theme=None)

st.markdown("<div style='margin:20px 0'></div>", unsafe_allow_html=True)

# ── 4. Confidence Intervals ─────────────────────────────────
st.markdown("### 4. Intervalles de Confiance à 95% par Plateforme")
ci_data = []
for platform, grp in df.groupby('platform'):
    prices = grp['price'].dropna()
    if len(prices) > 1:
        ci = stats.t.interval(0.95, len(prices)-1, loc=prices.mean(), scale=stats.sem(prices))
        ci_data.append({
            'Plateforme': platform,
            'Moyenne': prices.mean(),
            'IC_bas': ci[0],
            'IC_haut': ci[1]
        })

if not ci_data:
    render_alert("Aucun intervalle de confiance disponible (données insuffisantes par plateforme).", type="warning", icon="alert")
else:
    ci_df = pd.DataFrame(ci_data)
    fig5 = go.Figure()
    colors_list = [COLOR_CYAN, COLOR_PURPLE, COLOR_AMBER, COLOR_GREEN]
    for i, row in ci_df.iterrows():
        color = colors_list[i % len(colors_list)]
        fig5.add_trace(go.Scatter(
            x=[row['IC_bas'], row['Moyenne'], row['IC_haut']],
            y=[row['Plateforme']]*3,
            mode='lines+markers',
            name=row['Plateforme'],
            marker=dict(size=[8, 14, 8], color=color),
            line=dict(color=color, width=2)
        ))
    apply_plotly_theme(fig5)
    fig5.update_layout(
        title="Estimation de la Moyenne Vraie & Intervalle de Confiance à 95%",
        xaxis_title=f"Prix ({currency_symbol})",
        yaxis_title="",
        showlegend=False
    )
    st.plotly_chart(fig5, use_container_width=True, theme=None)

st.markdown("<div style='margin:20px 0'></div>", unsafe_allow_html=True)

# ── 5. Linear Regression ────────────────────────────────────
st.markdown("### 5. Régression Linéaire Multi-factorielle (OLS)")
st.markdown("<p style='color:#475569; font-size:13px; margin-bottom:15px;'>Modèle explicatif : <code>prix ~ marque + plateforme</code>. Ce modèle évalue la contribution de chaque facteur sur le prix final.</p>", unsafe_allow_html=True)

reg_df = df.copy()
# Drop categories with less than 2 entries to avoid singularity
reg_df = reg_df.dropna(subset=['price', 'brand', 'platform'])
reg_df['brand_code'] = pd.Categorical(reg_df['brand']).codes
reg_df['platform_code'] = pd.Categorical(reg_df['platform']).codes

if len(reg_df) < 15:
    render_alert("Données insuffisantes pour ajuster un modèle linéaire OLS.", type="warning", icon="alert")
else:
    # Build categorical model with statsmodels
    # We will use dummy variables for brand and platform to make it interpretable
    X = pd.get_dummies(reg_df[['brand', 'platform']], drop_first=True, dtype=float)
    X = sm.add_constant(X)
    y = reg_df['price']
    
    model = sm.OLS(y, X).fit()

    r1, r2, r3 = st.columns(3)
    with r1:
        render_kpi("Coefficient R²", f"{model.rsquared:.4f}", "layers", "Pouvoir explicatif du modèle")
    with r2:
        render_kpi("Statistique F", f"{model.fvalue:.4f}", "activity", "Importance globale des facteurs")
    with r3:
        render_kpi("P-value OLS", f"{model.f_pvalue:.4e}", "platforms", "Significativité globale")

    if model.rsquared > 0.4:
        render_alert(
            f"**Modèle Fortement Significatif (R² = {model.rsquared:.2%})** : La marque et la plateforme expliquent une proportion importante ({model.rsquared:.1%}) de la variation du prix des smartphones dans notre jeu de données.",
            type="success", icon="check"
        )
    else:
        render_alert(
            f"**Modèle Modéré (R² = {model.rsquared:.2%})** : Les facteurs de marque et de canal expliquent partiellement les prix. D'autres variables non observées (spécifications techniques, stockage, mémoire RAM, état du produit) influencent fortement le prix final.",
            type="info", icon="activity"
        )

    # Coef detailed table formatting
    st.markdown("#### Table des Coefficients Estimés")
    
    # Extract params and convert to dataframe
    summary_data = {
        "Facteurs & Catégories": model.params.index,
        "Coefficient (Impact)": model.params.values,
        "Erreur Standard": model.bse.values,
        "Valeur t": model.tvalues.values,
        "Probabilité P>|t|": model.pvalues.values
    }
    summary_df = pd.DataFrame(summary_data)
    
    # Beautify index labels
    summary_df['Facteurs & Catégories'] = summary_df['Facteurs & Catégories'].str.replace('brand_', 'Marque: ').str.replace('platform_', 'Plateforme: ').str.replace('const', 'Constante (Prix de base)')
    
    st.dataframe(
        summary_df,
        column_config={
            "Facteurs & Catégories": st.column_config.TextColumn("Facteurs explicatifs"),
            "Coefficient (Impact)": st.column_config.NumberColumn(f"Impact sur le prix ({currency_symbol})", format="%.2f"),
            "Erreur Standard": st.column_config.NumberColumn("Erreur Standard", format="%.2f"),
            "Valeur t": st.column_config.NumberColumn("Valeur t", format="%.3f"),
            "Probabilité P>|t|": st.column_config.NumberColumn("P-value individuelle", format="%.4e")
        },
        use_container_width=True,
        hide_index=True
    )

    col_reg1, col_reg2 = st.columns(2)
    with col_reg1:
        with st.expander("Résumé OLS Détaillé (Texte brut)"):
            st.text(model.summary().as_text())
            
    with col_reg2:
        fig_scatter = px.scatter(
            reg_df,
            x='brand',
            y='price',
            color='platform',
            color_discrete_sequence=[COLOR_CYAN, COLOR_PURPLE, COLOR_AMBER, COLOR_GREEN],
            title="Dispersion des Prix par Marque & Canal"
        )
        apply_plotly_theme(fig_scatter)
        fig_scatter.update_layout(
            yaxis_title=f"Prix ({currency_symbol})",
            xaxis_title="Marque"
        )
        st.plotly_chart(fig_scatter, use_container_width=True, theme=None)