import pytest
import pandas as pd
import numpy as np
import sys
import os

# Add root directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from clean_data import custom_date_parser, clean_customers, clean_orders

def test_custom_date_parser():
    assert pd.isna(custom_date_parser("invalid"))
    assert custom_date_parser("2023-01-01") == pd.Timestamp("2023-01-01")
    assert custom_date_parser("01/12/2023") == pd.Timestamp("2023-12-01")
    assert custom_date_parser("12-01-2023") == pd.Timestamp("2023-12-01")

def test_clean_customers_email():
    df = pd.DataFrame({
        'customer_id': ['C001', 'C002', 'C003'],
        'name': ['Test1', 'Test2', 'Test3'],
        'email': ['TEST@EXAMPLE.com', 'malformed', None],
        'region': ['North', 'South', None],
        'signup_date': ['2023-01-01', '2023-01-01', '2023-01-01']
    })
    cleaned_df, report = clean_customers(df)
    
    assert cleaned_df.loc[cleaned_df['customer_id'] == 'C001', 'email'].iloc[0] == 'test@example.com'
    assert cleaned_df.loc[cleaned_df['customer_id'] == 'C001', 'is_valid_email'].iloc[0] == True
    assert cleaned_df.loc[cleaned_df['customer_id'] == 'C002', 'is_valid_email'].iloc[0] == False
    assert cleaned_df.loc[cleaned_df['customer_id'] == 'C003', 'is_valid_email'].iloc[0] == False
    assert cleaned_df.loc[cleaned_df['customer_id'] == 'C003', 'region'].iloc[0] == 'Unknown'

def test_clean_orders_status():
    df = pd.DataFrame({
        'order_id': ['ORD1', 'ORD2'],
        'customer_id': ['C001', 'C001'],
        'product': ['P1', 'P1'],
        'amount': [100.0, None],
        'order_date': ['2023-01-01', '2023-01-01'],
        'status': ['done', 'canceled']
    })
    cleaned_df, report = clean_orders(df)
    
    assert cleaned_df.loc[cleaned_df['order_id'] == 'ORD1', 'status'].iloc[0] == 'completed'
    assert cleaned_df.loc[cleaned_df['order_id'] == 'ORD2', 'status'].iloc[0] == 'cancelled'
    # Check median fill if multiple P1 exist
    # (Simplified for this unit test)
