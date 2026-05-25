#!/usr/bin/env python3
"""
ETL Pipeline for Sales Data Processing

This script performs the following steps:
1. Extract: Read raw_sales.csv, raw_products.csv, and raw_regions.json
2. Transform:
   - Remove duplicates from sales data (keep last valid record per sale_id)
   - Handle null values (skip rows with empty/blank amount)
   - Standardize date format to YYYY-MM-DD
   - Join product_name from products data
   - Join region_name from regions data
3. Load: Write cleaned data to output/clean_sales.csv
4. Quality Check: Generate output/quality_report.json with metrics
"""

import pandas as pd
import json
import os
from datetime import datetime
import sys


def extract():
    """Extract data from all source files."""
    try:
        # Read sales data
        sales_df = pd.read_csv('raw_sales.csv')
        
        # Read products data
        products_df = pd.read_csv('raw_products.csv')
        
        # Read regions data
        with open('raw_regions.json', 'r') as f:
            regions_dict = json.load(f)
        
        return sales_df, products_df, regions_dict
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading files: {e}")
        sys.exit(1)


def transform(sales_df, products_df, regions_dict):
    """
    Transform the sales data with cleaning and enrichment.
    Returns cleaned DataFrame and quality metrics.
    """
    # Initialize quality metrics
    metrics = {
        'total_raw_rows': len(sales_df),
        'duplicates_removed': 0,
        'nulls_removed': 0,
        'date_format_fixed': 0,
        'total_clean_rows': 0
    }
    
    # Make a copy to avoid modifying the original
    df = sales_df.copy()
    
    # 1. Handle date format standardization
    def standardize_date(date_str):
        """Convert date to YYYY-MM-DD format."""
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
                date_obj = datetime.strptime(date_str, fmt)
                return date_obj.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        # If no format matches, return original
        return date_str
    
    # Apply date standardization
    original_dates = df['date'].copy()
    df['date'] = df['date'].apply(standardize_date)
    
    # Count date format fixes
    for orig, new in zip(original_dates, df['date']):
        if pd.notna(orig) and pd.notna(new) and str(orig) != str(new):
            metrics['date_format_fixed'] += 1
    
    # 2. Handle null/empty values in amount column
    # First, ensure amount is string for processing
    df['amount'] = df['amount'].astype(str)
    
    # Create a boolean mask for rows to keep
    # Keep rows where amount is not empty, not NaN, and not just whitespace
    valid_amount_mask = (
        df['amount'].notna() & 
        (df['amount'].str.strip() != '') & 
        (df['amount'].str.strip() != 'nan')
    )
    
    # Count nulls removed
    metrics['nulls_removed'] = len(df) - valid_amount_mask.sum()
    
    # Filter out invalid amount rows
    df = df[valid_amount_mask].copy()
    
    # Convert amount back to float for valid rows
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    
    # 3. Remove duplicates - keep last occurrence per sale_id
    # This handles the requirement: if same sale_id appears with invalid amount first,
    # and valid amount later, we keep the valid one (last occurrence)
    initial_count = len(df)
    df = df.drop_duplicates(subset=['sale_id'], keep='last')
    metrics['duplicates_removed'] = initial_count - len(df)
    
    # 4. Join product_name from products data
    # Create product_id to product_name mapping
    product_map = dict(zip(products_df['product_id'], products_df['product_name']))
    df['product_name'] = df['product_id'].map(product_map)
    
    # 5. Join region_name from regions data
    df['region_name'] = df['region_code'].map(regions_dict)
    
    # Reorder columns for better readability
    column_order = [
        'sale_id', 'product_id', 'product_name', 
        'region_code', 'region_name', 'amount', 'date'
    ]
    df = df[column_order]
    
    # Update final clean rows count
    metrics['total_clean_rows'] = len(df)
    
    return df, metrics


def load(cleaned_df, output_dir='output'):
    """Load cleaned data to CSV file."""
    output_path = os.path.join(output_dir, 'clean_sales.csv')
    cleaned_df.to_csv(output_path, index=False)
    print(f"Cleaned data saved to: {output_path}")
    return output_path


def generate_quality_report(metrics, output_dir='output'):
    """Generate quality report JSON file."""
    output_path = os.path.join(output_dir, 'quality_report.json')
    
    # Convert metrics values to Python native types for JSON serialization
    serializable_metrics = {}
    for key, value in metrics.items():
        # Convert numpy/pandas types to Python native types
        if hasattr(value, 'item'):  # For numpy/pandas scalar types
            serializable_metrics[key] = value.item()
        else:
            serializable_metrics[key] = value
    
    # Add timestamp to report
    report = {
        'etl_run_timestamp': datetime.now().isoformat(),
        'quality_metrics': serializable_metrics
    }
    
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"Quality report saved to: {output_path}")
    return output_path


def print_quality_summary(metrics):
    """Print a summary of quality metrics to console."""
    print("\n=== ETL Quality Summary ===")
    print(f"Total raw rows: {metrics['total_raw_rows']}")
    print(f"Duplicates removed: {metrics['duplicates_removed']}")
    print(f"Nulls removed: {metrics['nulls_removed']}")
    print(f"Date format fixed: {metrics['date_format_fixed']}")
    print(f"Total clean rows: {metrics['total_clean_rows']}")
    print(f"Data retention rate: {metrics['total_clean_rows']/metrics['total_raw_rows']*100:.1f}%")
    print("=" * 25)


def main():
    """Main ETL pipeline execution."""
    print("Starting ETL pipeline...")
    
    # Step 1: Extract
    print("1. Extracting data from source files...")
    sales_df, products_df, regions_dict = extract()
    print(f"   - Sales data: {len(sales_df)} rows")
    print(f"   - Products data: {len(products_df)} rows")
    print(f"   - Regions data: {len(regions_dict)} regions")
    
    # Step 2: Transform
    print("2. Transforming and cleaning data...")
    cleaned_df, metrics = transform(sales_df, products_df, regions_dict)
    
    # Step 3: Load
    print("3. Loading cleaned data...")
    output_path = load(cleaned_df)
    
    # Step 4: Quality Check
    print("4. Generating quality report...")
    report_path = generate_quality_report(metrics)
    
    # Print summary
    print_quality_summary(metrics)
    
    print("\nETL pipeline completed successfully!")
    
    # Show sample of cleaned data
    print("\nSample of cleaned data (first 5 rows):")
    print(cleaned_df.head().to_string())


if __name__ == "__main__":
    main()
