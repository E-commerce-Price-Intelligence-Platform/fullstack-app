import pandas as pd
import os

# Chemin absolu vers data/ peu importe d'où on lance
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')

def get_latest_prices():
    dfs = []
    for filename in ['amazon.csv', 'jumia.csv', 'electroplanet.csv']:
        filepath = os.path.join(DATA_DIR, filename)
        if os.path.exists(filepath):
            df = pd.read_csv(filepath)
            dfs.append(df)

    if not dfs:
        return pd.DataFrame()

    df = pd.concat(dfs, ignore_index=True)
    df = df[df['price'].notna() & (df['price'] != '')]
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df = df.dropna(subset=['price'])
    df['timestamp'] = pd.to_datetime(df['scraped_at'], errors='coerce')
    df['platform'] = df['source_site']

    return df[['name','brand','model','price','old_price',
               'currency','discount','rating','platform','timestamp']]