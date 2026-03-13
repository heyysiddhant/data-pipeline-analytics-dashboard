import pandas as pd
import numpy as np
import argparse
from pathlib import Path

# Constants based on Pathlib
BASE_DIR = Path(__file__).parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"

def load_csv(file_path):
    """Load CSV with error handling."""
    try:
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        df = pd.read_csv(file_path)
        if df.empty:
            print(f"Warning: {file_path} is empty.")
        return df
    except FileNotFoundError as e:
        print(f"Error: {e}")
        exit(1)
    except pd.errors.EmptyDataError:
        print(f"Error: {file_path} is empty.")
        exit(1)
    except Exception as e:
        print(f"Unexpected error loading {file_path}: {e}")
        exit(1)

def perform_analysis(config):
    # 2.1 Merging
    print("--- Merging Data ---")
    customers = load_csv(config['customers'])
    orders = load_csv(config['orders'])
    products = load_csv(config['products'])
    
    # Left-join orders onto customers
    orders_with_customers = pd.merge(
        orders, 
        customers, 
        on='customer_id', 
        how='left'
    )
    
    # Report orders with no matching customer
    no_cust = orders_with_customers['name'].isna().sum()
    print(f"Orders with no matching customer: {no_cust}")
    
    # Left-join products onto orders_with_customers
    full_data = pd.merge(
        orders_with_customers,
        products,
        left_on='product',
        right_on='product_name',
        how='left'
    )
    
    # Report orders with no matching product
    no_prod = full_data['product_id'].isna().sum()
    print(f"Orders with no matching product: {no_prod}")
    
    # 2.2 Analysis Tasks
    # 1. Monthly Revenue Trend (completed orders only)
    completed_orders = full_data[full_data['status'] == 'completed'].copy()
    
    monthly_revenue = completed_orders.groupby('order_year_month')['amount'].sum().reset_index()
    monthly_revenue.rename(columns={'amount': 'total_revenue'}, inplace=True)
    monthly_revenue.to_csv(PROCESSED_DATA_DIR / 'monthly_revenue.csv', index=False)
    print(f"Generated monthly_revenue.csv in {PROCESSED_DATA_DIR}")
    
    # 2. Top Customers (Top 10 by Spend)
    top_customers = completed_orders.groupby('customer_id').agg({
        'name': 'first',
        'region': 'first',
        'amount': 'sum'
    }).reset_index()
    top_customers.rename(columns={'amount': 'total_spend'}, inplace=True)
    top_customers = top_customers.sort_values(by='total_spend', ascending=False).head(10)
    
    # 3. Category Performance
    category_perf = completed_orders.groupby('category').agg({
        'amount': ['sum', 'mean'],
        'order_id': 'count'
    }).reset_index()
    category_perf.columns = ['category', 'total_revenue', 'average_order_value', 'number_of_orders']
    category_perf.to_csv(PROCESSED_DATA_DIR / 'category_performance.csv', index=False)
    print(f"Generated category_performance.csv in {PROCESSED_DATA_DIR}")
    
    # 4. Regional Analysis
    reg_cust_count = full_data.groupby('region')['customer_id'].nunique()
    reg_order_count = full_data.groupby('region')['order_id'].nunique()
    reg_revenue = completed_orders.groupby('region')['amount'].sum()
    
    regional_analysis = pd.DataFrame({
        'number_of_customers': reg_cust_count,
        'number_of_orders': reg_order_count,
        'total_revenue': reg_revenue
    }).reset_index()
    regional_analysis['total_revenue'] = regional_analysis['total_revenue'].fillna(0)
    regional_analysis['avg_revenue_per_customer'] = regional_analysis['total_revenue'] / regional_analysis['number_of_customers']
    regional_analysis.to_csv(PROCESSED_DATA_DIR / 'regional_analysis.csv', index=False)
    print(f"Generated regional_analysis.csv in {PROCESSED_DATA_DIR}")
    
    # 5. Churn Indicator
    full_data['order_date'] = pd.to_datetime(full_data['order_date'])
    latest_date = full_data['order_date'].max()
    churn_threshold = latest_date - pd.Timedelta(days=90)
    
    # Customers who had a completed order in the last 90 days
    recent_buyers = completed_orders[pd.to_datetime(completed_orders['order_date']) > churn_threshold]['customer_id'].unique()
    
    # Add churn flag to top_customers
    top_customers['churned'] = ~top_customers['customer_id'].isin(recent_buyers)
    top_customers.to_csv(PROCESSED_DATA_DIR / 'top_customers.csv', index=False)
    print(f"Generated top_customers.csv in {PROCESSED_DATA_DIR} (with churn indicator)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Data Analysis Script")
    parser.add_argument('--customers', type=Path, default=PROCESSED_DATA_DIR / 'customers_clean.csv', help="Path to cleaned customers CSV")
    parser.add_argument('--orders', type=Path, default=PROCESSED_DATA_DIR / 'orders_clean.csv', help="Path to cleaned orders CSV")
    parser.add_argument('--products', type=Path, default=RAW_DATA_DIR / 'products.csv', help="Path to products CSV")
    
    args = parser.parse_args()
    
    config = {
        'customers': args.customers,
        'orders': args.orders,
        'products': args.products
    }
    
    perform_analysis(config)
