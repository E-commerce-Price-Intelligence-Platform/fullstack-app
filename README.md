# Smartphone Price Intelligence Platform — Fullstack Dashboard

A production-grade, interactive analytics dashboard designed to monitor and analyze real-time smartphone price data extracted from Amazon.fr, Jumia.ma, and Electroplanet.ma. This dashboard leverages Google Cloud Bigtable as its high-speed storage backend and performs advanced statistical analysis on pricing distributions.

---

## Core Features

### 1. Real-Time Price Ingestion & Connectivity
- **Dual-Mode Data Source**: Supports real-time streaming data from GCP Bigtable or automated fallback to local CSV records in offline environments.
- **System Monitoring**: Live connection status indicator on the sidebar displaying state updates for Bigtable.

### 2. Inferential Statistical Analysis
- **Student's T-Test (Bivariate Comparison)**: Statistically validates price differences between any two marketplaces with confidence intervals (95%).
- **Analysis of Variance (ANOVA)**: Evaluates the impact of brands on smartphone pricing to determine if pricing differences are structurally significant.
- **Multi-Factorial Linear Regression (OLS)**: Fits a predictive and explanatory Ordinary Least Squares model (`price ~ brand + platform`) using statsmodels to evaluate coefficients and coefficient significance.

### 3. Search & Comparison Interface
- **Cross-Market Comparison**: Multi-platform search tool allowing instant comparison of specific models (e.g., "iPhone", "S24").
- **Pricing Indicators**: Displays detailed statistical metrics (mean, median, standard deviation, variance) and lists all matching offers sorted by price.

### 4. Professional Light Mode UI
- **Outfit Typography**: High-fidelity interface utilizing modern sans-serif typography.
- **Polished Data Visualizations**: Fully custom Plotly figures styled with high-contrast dark axis labels, ticks, and legends (`theme=None` overrides to ensure visibility), using curated, professional color palettes.

---

## Architecture Flow

The dashboard represents the presentation layer of the wider data engineering pipeline:
1. **Scrapy + Selenium**: Scrapes raw prices and product details.
2. **Apache Airflow & Apache NiFi**: Orchestrates batch runs and streams raw rows into GCP Bigtable.
3. **Google Cloud Bigtable**: Real-time high-speed storage.
4. **Google BigQuery & dbt**: Runs analytical transformations.
5. **Streamlit + Plotly**: Provides the interactive analytical dashboard.

---

## Installation & Local Execution

### Prerequisites
- Python 3.10+
- Docker & Docker Compose
- GCP Service Account credentials (saved as `gcp-credentials.json` at the root of the project to authenticate Bigtable client)

### Setup Instructions

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/E-commerce-Price-Intelligence-Platform/fullstack-app.git
   cd fullstack-app
   ```

2. **Configure GCP Credentials**:
   Place your GCP Service Account JSON key as `gcp-credentials.json` in the root of the directory to enable automated GCP Bigtable data fetching.

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch the Dashboard**:
   ```bash
   cd frontend
   python -m streamlit run dashboard.py
   ```

Alternatively, run the containerized deployment using:
```bash
docker compose up --build -d
```

---

## Technologies Used
- **Frontend**: Streamlit, HTML5/CSS3 Custom Styling
- **Visualization**: Plotly Express & Graph Objects
- **Statistics**: SciPy, Statsmodels, Pandas, NumPy
- **Database Backend**: Google Cloud Bigtable (via `google-cloud-bigtable` SDK)