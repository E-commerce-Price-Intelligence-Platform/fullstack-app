import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
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
st.set_page_config(page_title="Comparaison Produits", layout="wide")

# Inject CSS styles
inject_custom_css()

# Fetch raw data
df_raw = get_latest_prices()
if df_raw.empty:
    st.error("Aucune donnée disponible pour la comparaison.")
    st.stop()

# ── Sidebar Filter & Currency ──────────────────────────────────
st.sidebar.markdown("""
<div style='padding: 10px 0; border-bottom: 1px solid rgba(0, 0, 0, 0.08); margin-bottom: 20px;'>
    <h2 style='color:#0B0F19; font-size:18px; margin:0; font-weight:700; letter-spacing:1px;'>COMPARAISON</h2>
    <p style='color:#64748B; font-size:11px; margin:4px 0 0 0;'>Search & Compare Products</p>
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
    <h1 style='font-size:28px; margin:0; font-weight:700; color:#0B0F19; background: linear-gradient(90deg, #0B0F19, #0ea5e9); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>COMPARAISON DE PRODUITS</h1>
    <p style='color:#64748B; font-size:13px; margin:8px 0 0 0; line-height: 1.5;'>
        Recherchez et analysez la dispersion des prix pour un modèle spécifique sur toutes nos plateformes partenaires.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Search Input ────────────────────────────────────────────
search = st.text_input(
    "Rechercher un modèle de smartphone",
    placeholder="ex: Samsung Galaxy S25, iPhone 16, Xiaomi..."
)

if search:
    # Filter by name
    results = df[df['name'].str.contains(search, case=False, na=False)]
    
    if results.empty:
        render_alert(f"Aucun smartphone trouvé pour la recherche : '{search}'. Essayez un autre mot-clé.", type="warning", icon="alert")
        
        # Display search recommendations
        st.markdown("<p style='color:#64748b; font-size:12px; margin-top: 10px;'>Suggestions de marques disponibles :</p>", unsafe_allow_html=True)
        unique_brands = df['brand'].dropna().unique().tolist()
        st.write(", ".join([b.capitalize() for b in sorted(unique_brands)]))
    else:
        st.markdown(f"""
        <div style='display: flex; align-items: center; margin-bottom: 15px;'>
            <div style='display:inline-block; background:rgba(0, 230, 118, 0.08); border: 1px solid rgba(0, 230, 118, 0.2); border-radius:20px; padding:4px 14px; color:#00e676; font-size:12px; font-weight:600; font-family:"JetBrains Mono", monospace;'>
                {len(results)} modèles correspondants trouvés
            </div>
        </div>
        """, unsafe_allow_html=True)

        # KPIs Row
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            render_kpi("Prix Moyen", f"{results['price'].mean():,.0f} {currency_symbol}", "price", "Tarif moyen trouvé")
        with c2:
            render_kpi("Prix Minimum", f"{results['price'].min():,.0f} {currency_symbol}", "min_price", "Meilleur canal d'achat")
        with c3:
            render_kpi("Prix Maximum", f"{results['price'].max():,.0f} {currency_symbol}", "max_price", "Canal le plus cher")
        with c4:
            render_kpi("Résultats", f"{len(results)}", "database", "Nombre d'offres")

        st.markdown("<div style='margin:20px 0'></div>", unsafe_allow_html=True)

        # Visualizations
        col1, col2 = st.columns(2)
        with col1:
            avg = results.groupby('platform')['price'].mean().reset_index()
            fig = px.bar(
                avg,
                x='platform',
                y='price',
                color='platform',
                color_discrete_sequence=[COLOR_CYAN, COLOR_PURPLE, COLOR_AMBER, COLOR_GREEN],
                title=f"Prix Moyen par Plateforme pour '{search}'"
            )
            apply_plotly_theme(fig)
            fig.update_layout(
                showlegend=False,
                yaxis_title=f"Prix Moyen ({currency_symbol})",
                xaxis_title="Plateforme"
            )
            st.plotly_chart(fig, use_container_width=True, theme=None)

        with col2:
            fig2 = px.box(
                results,
                x='platform',
                y='price',
                color='platform',
                color_discrete_sequence=[COLOR_CYAN, COLOR_PURPLE, COLOR_AMBER, COLOR_GREEN],
                title="Dispersion et Écarts de Prix"
            )
            apply_plotly_theme(fig2)
            fig2.update_layout(
                showlegend=False,
                yaxis_title=f"Prix ({currency_symbol})",
                xaxis_title="Plateforme"
            )
            st.plotly_chart(fig2, use_container_width=True, theme=None)

        # Detailed results table
        st.markdown("### Offres Détaillées")
        st.dataframe(
            results[['name', 'brand', 'model', 'price', 'currency', 'platform', 'timestamp']].sort_values('price'),
            column_config={
                "name": st.column_config.TextColumn("Nom du smartphone", width="large"),
                "brand": st.column_config.TextColumn("Marque"),
                "model": st.column_config.TextColumn("Modèle"),
                "price": st.column_config.NumberColumn(f"Prix ({currency_symbol})", format="%.2f" if target_currency == "EUR" else "%.0f"),
                "currency": st.column_config.TextColumn("Devise"),
                "platform": st.column_config.TextColumn("Source"),
                "timestamp": st.column_config.DatetimeColumn("Date d'extraction")
            },
            use_container_width=True,
            hide_index=True
        )
else:
    # Default state: Show Top 10 most expensive and top 10 cheapest
    st.markdown("### Distribution Globale du Catalogue")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Top 10 des Modèles les plus Chers")
        top = df.nlargest(10, 'price')[['name', 'brand', 'price', 'platform', 'currency']]
        
        # Truncate long names for better chart display
        top['display_name'] = top['name'].apply(lambda x: x[:35] + '...' if len(x) > 35 else x)
        
        fig = px.bar(
            top,
            x='price',
            y='display_name',
            color='platform',
            orientation='h',
            color_discrete_sequence=[COLOR_CYAN, COLOR_PURPLE, COLOR_AMBER],
            category_orders={"display_name": top['display_name'].tolist()} # keep order
        )
        apply_plotly_theme(fig)
        fig.update_layout(
            xaxis_title=f"Prix ({currency_symbol})",
            yaxis_title="",
            legend_title="Plateforme"
        )
        st.plotly_chart(fig, use_container_width=True, theme=None)

    with col2:
        st.markdown("#### Top 10 des Modèles les plus Abordables")
        bottom = df.nsmallest(10, 'price')[['name', 'brand', 'price', 'platform', 'currency']]
        bottom['display_name'] = bottom['name'].apply(lambda x: x[:35] + '...' if len(x) > 35 else x)
        
        fig2 = px.bar(
            bottom,
            x='price',
            y='display_name',
            color='platform',
            orientation='h',
            color_discrete_sequence=[COLOR_CYAN, COLOR_PURPLE, COLOR_AMBER],
            category_orders={"display_name": bottom['display_name'].tolist()}
        )
        apply_plotly_theme(fig2)
        fig2.update_layout(
            xaxis_title=f"Prix ({currency_symbol})",
            yaxis_title="",
            legend_title="Plateforme"
        )
        st.plotly_chart(fig2, use_container_width=True, theme=None)
        
    # Stats details
    render_alert("Saisissez le nom d'un smartphone (ex: 'S24' ou 'iPhone') dans la zone de recherche ci-dessus pour comparer directement ses prix entre Jumia, Electroplanet et Amazon.", type="info", icon="activity")