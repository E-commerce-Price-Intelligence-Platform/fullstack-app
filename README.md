# E-commerce Price Intelligence Platform

Real-time price monitoring across Amazon FR, Jumia MA and Electroplanet.

## Architecture

Scrapy + Selenium → Apache Airflow → Apache NiFi → Google Cloud Bigtable → dbt → Streamlit Dashboard

## Pages

- Dashboard : KPIs, prix par plateforme, comparaisons
- Statistiques : T-test, ANOVA, intervalles de confiance
- Comparaison : Recherche produit multi-plateforme
- Pipeline : Statut ingestion, qualite des donnees

## Installation

git clone https://github.com/E-commerce-Price-Intelligence-Platform/fullstack-app.git
cd fullstack-app
pip install -r requirements.txt
cd frontend
python -m streamlit run dashboard.py

## Technologies

Scraping : Scrapy, Selenium
Streaming : Apache NiFi
Batch : Apache Airflow
Storage : Google Cloud Bigtable
Transformation : dbt
Frontend : Streamlit, Plotly
Statistiques : SciPy, statsmodels