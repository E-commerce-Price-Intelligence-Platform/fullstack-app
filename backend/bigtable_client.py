import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID  = "regal-unfolding-490222-g5"
INSTANCE_ID = "price-intel-instance"
TABLE_ID    = "smartphones"

def get_latest_prices():
    try:
        from google.cloud import bigtable
        from google.cloud.bigtable import row_filters

        client   = bigtable.Client(project=PROJECT_ID, admin=True)
        instance = client.instance(INSTANCE_ID)
        table    = instance.table(TABLE_ID)

        rows = table.read_rows(filter_=row_filters.CellsColumnLimitFilter(1))
        rows.consume_all()

        data = []
        for row_key, row in rows.rows.items():
            try:
                key_parts = row_key.decode().split("#")
                product_id = key_parts[0]
                timestamp  = key_parts[1] if len(key_parts) > 1 else ""

                price = row.cells["price_cf"][b"price"][0].value.decode()
                name  = row.cells["metadata_cf"][b"name"][0].value.decode()

                brand    = ""
                platform = ""
                try:
                    brand    = row.cells["metadata_cf"][b"brand"][0].value.decode()
                    platform = row.cells["metadata_cf"][b"source_site"][0].value.decode()
                except:
                    pass

                data.append({
                    "product_id": product_id,
                    "name":       name,
                    "brand":      brand,
                    "model":      "",
                    "price":      float(price),
                    "old_price":  None,
                    "currency":   "MAD",
                    "discount":   None,
                    "rating":     None,
                    "platform":   platform,
                    "timestamp":  timestamp
                })
            except:
                continue

        if data:
            df = pd.DataFrame(data)
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            df['price']     = pd.to_numeric(df['price'], errors='coerce')
            return df.dropna(subset=['price'])

    except Exception as e:
        print(f"Bigtable error: {e} — falling back to CSV")

    # Fallback CSV si Bigtable pas accessible
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    dfs = []
    for filename in ['amazon.csv', 'jumia.csv', 'electroplanet.csv']:
        filepath = os.path.join(DATA_DIR, filename)
        if os.path.exists(filepath):
            dfs.append(pd.read_csv(filepath))

    if not dfs:
        return pd.DataFrame()

    df = pd.concat(dfs, ignore_index=True)
    df = df[df['price'].notna() & (df['price'] != '')]
    df['price']     = pd.to_numeric(df['price'], errors='coerce')
    df['timestamp'] = pd.to_datetime(df['scraped_at'], errors='coerce')
    df['platform']  = df['source_site']
    return df[['name','brand','model','price','old_price',
               'currency','discount','rating','platform','timestamp']].dropna(subset=['price'])