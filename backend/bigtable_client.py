import pandas as pd
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

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
    
    # Garde seulement les lignes avec un prix
    df = df[df['price'].notna() & (df['price'] != '')]
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df = df.dropna(subset=['price'])
    
    # Renomme pour le dashboard
    df['timestamp'] = pd.to_datetime(df['scraped_at'], errors='coerce')
    df['platform'] = df['source_site']
    
    return df[[
        'name', 'brand', 'model', 'price', 
        'old_price', 'currency', 'discount',
        'rating', 'platform', 'timestamp'
    ]]