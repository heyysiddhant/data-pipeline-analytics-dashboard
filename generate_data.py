import pandas as pd
import numpy as np
import random
from pathlib import Path

# Constants based on Pathlib
BASE_DIR = Path(__file__).parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"

def generate_customers(n=100):
    regions = ['North', 'South', 'East', 'West', None]
    data = {
        'customer_id': [f'C{str(i).zfill(3)}' for i in range(1, n + 1)],
        'name': [f'Customer {i}' for i in range(1, n + 1)],
        'email': [f'cust{i}@example.com' for i in range(1, n + 1)],
        'region': [random.choice(regions) for _ in range(n)],
        'signup_date': [(pd.to_datetime('2023-01-01') + pd.to_timedelta(random.randint(0, 365), unit='D')).strftime('%Y-%m-%d') for _ in range(n)]
    }
    df = pd.DataFrame(data)
    
    # Introduce duplicates
    df = pd.concat([df, df.sample(10)], ignore_index=True)
    
    # Randomly introduce uppercase in email
    df['email'] = df['email'].apply(lambda x: x.upper() if x and random.random() < 0.2 else x)
    
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(RAW_DATA_DIR / 'customers.csv', index=False)
    print(f"Generated customers.csv in {RAW_DATA_DIR} with {len(df)} rows.")

def generate_products(n=20):
    categories = ['Electronics', 'Home', 'Clothing', 'Books', 'Toys']
    data = {
        'product_id': [f'P{str(i).zfill(3)}' for i in range(1, n + 1)],
        'product_name': [f'Product {i}' for i in range(1, n + 1)],
        'category': [random.choice(categories) for _ in range(n)],
        'unit_price': [np.round(random.uniform(10, 500), 2) for _ in range(n)]
    }
    df = pd.DataFrame(data)
    df.to_csv(RAW_DATA_DIR / 'products.csv', index=False)
    print(f"Generated products.csv in {RAW_DATA_DIR} with {len(df)} rows.")

def generate_orders(n=200):
    products = [f'Product {i}' for i in range(1, 21)]
    statuses = ['completed', 'pending', 'cancelled', 'refunded', 'done', 'Pending', 'canceled']
    
    data = {
        'order_id': [f'O{str(i).zfill(3)}' for i in range(1, n + 1)],
        'customer_id': [f'C{str(random.randint(1, 100)).zfill(3)}' for _ in range(n)],
        'product': [random.choice(products) for _ in range(n)],
        'amount': [np.round(random.uniform(20, 1000), 2) if random.random() > 0.1 else None for _ in range(n)],
        'order_date': [(pd.to_datetime('2024-01-01') + pd.to_timedelta(random.randint(0, 400), unit='D')).strftime('%Y-%m-%d') for _ in range(n)],
        'status': [random.choice(statuses) for _ in range(n)]
    }
    
    # Add some dirty dates
    def dirtify_date(d):
        if random.random() < 0.1:
            return pd.to_datetime(d).strftime('%d/%m/%Y')
        elif random.random() < 0.05:
            return pd.to_datetime(d).strftime('%m-%d-%Y')
        return d
        
    df = pd.DataFrame(data)
    df['order_date'] = df['order_date'].apply(dirtify_date)
    
    # Inject nulls for merging tests
    df.loc[0, 'order_id'] = None
    df.loc[1, 'customer_id'] = None
    
    df.to_csv(RAW_DATA_DIR / 'orders.csv', index=False)
    print(f"Generated orders.csv in {RAW_DATA_DIR} with {len(df)} rows.")

if __name__ == "__main__":
    generate_customers()
    generate_products()
    generate_orders()
