#!/usr/bin/env python3
"""
ETL Pipeline for Sales Data

Extracts data from raw_sales.csv, raw_products.csv, and raw_regions.json
Transforms data by cleaning, deduplicating, and enriching
Loads cleaned data to output/clean_sales.csv
Generates quality report in output/quality_report.json
"""

import pandas as pd
import json
import os
from datetime import datetime
import re
from pathlib import Path


def extract_data():
    """Extract data from all source files"""
    print("Extracting data from source files...")
    
    # Read raw sales data
    sales_df = pd.read_csv('raw_sales.csv')
    
    # Read products data
    products_df = pd.read_csv('raw_products.csv')
    
    # Read regions data
    with open('raw_regions.json', 'r') as f:
        regions_dict = json.load(f)
    
    return sales_df, products_df, regions_dict


def transform_data(sales_df, products_df, regions_dict):
    """Transform and clean the sales data"""
    print("Transforming data...")
    
    # Initialize quality metrics
    quality_metrics = {
        'total_raw_rows': len(sales_df),
        'duplicates_removed': 0,
        'nulls_removed': 0,
        'date_format_fixed': 0,
        'total_clean_rows': 0
    }
    
    # Create a copy to avoid modifying original
    clean_df = sales_df.copy()
    
    # Step 1: Remove completely empty rows (all columns empty or whitespace)
    initial_rows = len(clean_df)
    clean_df = clean_df.dropna(how='all')
    # Check for rows where all values are empty strings
    mask = clean_df.apply(lambda row: row.apply(lambda x: isinstance(x, str) and x.strip() == '').all(), axis=1)
    clean_df = clean_df[~mask]
    
    # Step 2: Handle amount column - keep only rows with valid amount
    # First convert amount to numeric, errors='coerce' will turn invalid to NaN
    clean_df['amount'] = pd.to_numeric(clean_df['amount'], errors='coerce')
    
    # Track rows with null amount before deduplication
    null_amount_before = clean_df['amount'].isna().sum()
    
    # Step 3: Remove duplicates by sale_id, keeping the last occurrence
    # This ensures if same sale_id appears with invalid amount first and valid amount later,
    # we keep the valid one (last occurrence)
    initial_len = len(clean_df)
    clean_df = clean_df.sort_values('sale_id').drop_duplicates(subset=['sale_id'], keep='last')
    quality_metrics['duplicates_removed'] = initial_len - len(clean_df)
    
    # Step 4: Now remove rows with null amount (after deduplication)
    rows_before_null_removal = len(clean_df)
    clean_df = clean_df.dropna(subset=['amount'])
    quality_metrics['nulls_removed'] = null_amount_before - (rows_before_null_removal - len(clean_df))
    
    # Step 5: Fix date format
    def normalize_date(date_str):
        """Convert date to YYYY-MM-DD format"""
        if pd.isna(date_str):
            return None
        
        date_str = str(date_str).strip()
        
        # Try different date formats
        date_formats = [
            '%Y-%m-%d',      # YYYY-MM-DD
            '%m/%d/%Y',      # MM/DD/YYYY
            '%d/%m/%Y',      # DD/MM/YYYY
            '%Y/%m/%d',      # YYYY/MM/DD
        ]
        
        for fmt in date_formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        # If no format matches, return original
        return date_str
    
    # Apply date normalization
    original_dates = clean_df['date'].copy()
    clean_df['date'] = clean_df['date'].apply(normalize_date)
    
    # Count how many dates were fixed (changed from original)
    date_fixed_count = (clean_df['date'] != original_dates).sum()
    quality_metrics['date_format_fixed'] = int(date_fixed_count)
    
    # Step 6: Remove rows with invalid dates
    clean_df = clean_df.dropna(subset=['date'])
    
    # Step 7: Enrich data with product names
    # Create product mapping dictionary
    product_map = pd.Series(products_df['product_name'].values, index=products_df['product_id']).to_dict()
    clean_df['product_name'] = clean_df['product_id'].map(product_map)
    
    # Step 8: Enrich data with region names
    clean_df['region_name'] = clean_df['region_code'].map(regions_dict)
    
    # Step 9: Reorder columns for final output
    column_order = ['sale_id', 'product_id', 'product_name', 'region_code', 'region_name', 
                    'amount', 'date']
    clean_df = clean_df[column_order]
    
    # Step 10: Sort by sale_id for consistent output
    clean_df = clean_df.sort_values('sale_id')
    
    # Update final clean rows count
    quality_metrics['total_clean_rows'] = len(clean_df)
    
    # Convert all values to Python native types for JSON serialization
    for key in quality_metrics:
        if hasattr(quality_metrics[key], 'item'):  # For numpy types
            quality_metrics[key] = quality_metrics[key].item()
        else:
            quality_metrics[key] = int(quality_metrics[key])
    
    return clean_df, quality_metrics


def load_data(clean_df, quality_metrics):
    """Load cleaned data to output files"""
    print("Loading data to output files...")
    
    # Create output directory if it doesn't exist
    output_dir = Path('output')
    output_dir.mkdir(exist_ok=True)
    
    # Save cleaned data to CSV
    output_csv = output_dir / 'clean_sales.csv'
    clean_df.to_csv(output_csv, index=False)
    print(f"Cleaned data saved to: {output_csv}")
    
    # Save quality report to JSON
    output_json = output_dir / 'quality_report.json'
    with open(output_json, 'w') as f:
        json.dump(quality_metrics, f, indent=2)
    print(f"Quality report saved to: {output_json}")
    
    return output_csv, output_json


def run_etl_pipeline():
    """Main ETL pipeline execution function"""
    print("=" * 50)
    print("Starting ETL Pipeline")
    print("=" * 50)
    
    try:
        # Extract
        sales_df, products_df, regions_dict = extract_data()
        
        # Transform
        clean_df, quality_metrics = transform_data(sales_df, products_df, regions_dict)
        
        # Load
        output_csv, output_json = load_data(clean_df, quality_metrics)
        
        print("=" * 50)
        print("ETL Pipeline Completed Successfully!")
        print(f"Original rows: {quality_metrics['total_raw_rows']}")
        print(f"Cleaned rows: {quality_metrics['total_clean_rows']}")
        print(f"Duplicates removed: {quality_metrics['duplicates_removed']}")
        print(f"Null rows removed: {quality_metrics['nulls_removed']}")
        print(f"Dates fixed: {quality_metrics['date_format_fixed']}")
        print("=" * 50)
        
        # Display first few rows of cleaned data
        print("\nFirst 5 rows of cleaned data:")
        print(clean_df.head().to_string())
        
    except Exception as e:
        print(f"Error in ETL pipeline: {e}")
        raise


if __name__ == "__main__":
    run_etl_pipeline()
