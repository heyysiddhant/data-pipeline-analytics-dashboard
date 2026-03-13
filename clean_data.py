import pandas as pd
import numpy as np
import logging
from pathlib import Path

# Set up logging for unparseable dates
logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')

# Constants based on Pathlib
BASE_DIR = Path(__file__).parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"

def custom_date_parser(date_str):
    if pd.isna(date_str):
        return pd.NaT
    
    formats = ['%Y-%m-%d', '%d/%m/%Y', '%m-%d-%Y']
    for fmt in formats:
        try:
            return pd.to_datetime(date_str, format=fmt)
        except (ValueError, TypeError):
            continue
    
    logging.warning(f"Unparseable date encountered: {date_str}")
    return pd.NaT

def clean_customers(df):
    report = {}
    report['before_rows'] = len(df)
    report['before_nulls'] = df.isnull().sum().to_dict()
    
    # Remove duplicates based on customer_id, keeping most recent signup_date
    df['signup_date_dt'] = df['signup_date'].apply(custom_date_parser)
    df = df.sort_values(by=['customer_id', 'signup_date_dt'], ascending=[True, False])
    
    before_dups = len(df)
    df = df.drop_duplicates(subset='customer_id', keep='first')
    report['dups_removed'] = before_dups - len(df)
    
    # Standardize email to lowercase; flag invalid/missing
    df['email'] = df['email'].str.lower()
    df['is_valid_email'] = df['email'].apply(
        lambda x: bool(x and isinstance(x, str) and '@' in x and '.' in x)
    )
    
    # Parse signup_date
    df['signup_date'] = df['signup_date_dt'].dt.strftime('%Y-%m-%d')
            
    # Strip whitespace from name and region
    for col in ['name', 'region']:
        df[col] = df[col].astype(str).str.strip()
    
    # Fill missing region with 'Unknown'
    df['region'] = df['region'].replace(['nan', 'None'], np.nan).fillna('Unknown')
    
    # Drop temp column
    df = df.drop(columns=['signup_date_dt'])
    
    report['after_rows'] = len(df)
    report['after_nulls'] = df.isnull().sum().to_dict()
    
    return df, report

def clean_orders(df):
    report = {}
    report['before_rows'] = len(df)
    report['before_nulls'] = df.isnull().sum().to_dict()
    
    # 1.2 orders.csv Cleaning
    # Parse order_date supporting multiple formats
    df['order_date'] = df['order_date'].apply(custom_date_parser)
    
    # Drop rows where both customer_id and order_id are null
    df = df.dropna(subset=['customer_id', 'order_id'], how='all')
    
    # Fill missing amount with median amount grouped by product
    df['amount'] = df['amount'].astype(float)
    df['amount'] = df.groupby('product')['amount'].transform(lambda x: x.fillna(x.median()))
    
    # Normalize status column
    status_map = {
        'done': 'completed',
        'completed': 'completed',
        'pending': 'pending',
        'Pending': 'pending',
        'cancelled': 'cancelled',
        'canceled': 'cancelled',
        'refunded': 'refunded'
    }
    df['status'] = df['status'].map(status_map).fillna('pending')
    
    # Add derived order_year_month (format: YYYY-MM)
    df['order_year_month'] = df['order_date'].dt.strftime('%Y-%m')
    
    report['after_rows'] = len(df)
    report['after_nulls'] = df.isnull().sum().to_dict()
    
    return df, report

def print_report(name, report):
    print(f"\n--- Cleaning Report: {name} ---")
    print(f"Rows Before: {report['before_rows']}")
    print(f"Rows After:  {report['after_rows']}")
    print(f"Duplicates Removed: {report.get('dups_removed', 'N/A')}")
    print("\nNull Counts Before:")
    for col, count in report['before_nulls'].items():
        print(f"  {col}: {count}")
    print("\nNull Counts After:")
    for col, count in report['after_nulls'].items():
        print(f"  {col}: {count}")

if __name__ == "__main__":
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    customers_path = RAW_DATA_DIR / "customers.csv"
    orders_path = RAW_DATA_DIR / "orders.csv"
    
    if not customers_path.exists() or not orders_path.exists():
        print(f"Error: Raw data files not found in {RAW_DATA_DIR}. Please generate data first.")
    else:
        customers_df = pd.read_csv(customers_path)
        orders_df = pd.read_csv(orders_path)
        
        cleaned_customers, cust_report = clean_customers(customers_df)
        cleaned_orders, ord_report = clean_orders(orders_df)
        
        cleaned_customers.to_csv(PROCESSED_DATA_DIR / "customers_clean.csv", index=False)
        cleaned_orders.to_csv(PROCESSED_DATA_DIR / "orders_clean.csv", index=False)
        
        print_report('customers.csv', cust_report)
        print_report('orders.csv', ord_report)
        print(f"\nCleaned files saved in {PROCESSED_DATA_DIR}")
