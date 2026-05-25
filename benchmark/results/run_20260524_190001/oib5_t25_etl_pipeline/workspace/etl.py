#!/usr/bin/env python3
"""
ETL Pipeline for Sales Data

Extracts data from raw_sales.csv, raw_products.csv, raw_regions.json
Transforms and cleans the data
Loads to output/clean_sales.csv
Generates quality report at output/quality_report.json
"""

import pandas as pd
import json
import os
from datetime import datetime
import numpy as np
from pathlib import Path


def extract():
    """Extract data from all source files"""
    print("Extracting data from source files...")
    
    # Read sales data
    sales_df = pd.read_csv('raw_sales.csv', dtype=str)
    
    # Read products data
    products_df = pd.read_csv('raw_products.csv', dtype=str)
    
    # Read regions data
    with open('raw_regions.json', 'r') as f:
        regions_dict = json.load(f)
    
    return sales_df, products_df, regions_dict


def transform(sales_df, products_df, regions_dict):
    """Transform and clean the sales data"""
    print("Transforming and cleaning data...")
    
    # Create a copy to avoid modifying the original
    df = sales_df.copy()
    
    # Store original row count
    total_raw_rows = len(df)
    
    # Track statistics
    stats = {
        'total_raw_rows': total_raw_rows,
        'duplicates_removed': 0,
        'nulls_removed': 0,
        'date_format_fixed': 0
    }
    
    # 1. Handle amount field - convert to numeric, handle empty/whitespace
    # First, strip whitespace from amount column
    df['amount'] = df['amount'].astype(str).str.strip()
    
    # Identify rows where amount is empty, NaN, or whitespace only
    amount_mask = df['amount'].isin(['', 'nan', 'NaN', 'None', 'null']) | df['amount'].isna()
    
    # Store rows with invalid amount for potential removal
    invalid_amount_rows = df[amount_mask].copy()
    
    # Convert valid amounts to float
    df['amount_numeric'] = pd.to_numeric(df['amount'], errors='coerce')
    
    # Create a flag for valid amounts
    df['has_valid_amount'] = df['amount_numeric'].notna()
    
    # 2. Handle date format - convert to YYYY-MM-DD
    # Store original date for comparison
    df['date_original'] = df['date'].copy()
    
    # Try multiple date formats
    date_formats = ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d']
    parsed_dates = pd.Series([pd.NaT] * len(df), dtype='datetime64[ns]')
    
    for fmt in date_formats:
        mask = parsed_dates.isna()
        if mask.any():
            try:
                parsed_dates[mask] = pd.to_datetime(df.loc[mask, 'date'], format=fmt, errors='coerce')
            except:
                pass
    
    # If any dates still not parsed, try pandas auto-conversion
    if parsed_dates.isna().any():
        mask = parsed_dates.isna()
        parsed_dates[mask] = pd.to_datetime(df.loc[mask, 'date'], errors='coerce')
    
    df['date'] = parsed_dates
    
    # Count how many dates were fixed (format changed)
    valid_dates = df['date'].notna()
    if 'date_original' in df.columns:
        # Count where original date exists and was parsed successfully
        stats['date_format_fixed'] = df[valid_dates & df['date_original'].notna()].shape[0]
    
    # 3. Remove rows with invalid dates
    invalid_date_rows = df[~valid_dates]
    df = df[valid_dates].copy()
    
    # 4. Handle sale_id duplicates with priority for valid records
    # Sort by: 1) valid amount, 2) date (newer first)
    df['has_valid_amount'] = df['amount'].notna()
    
    # Create a sorting key - valid amounts first, then by date (newest first)
    df['sort_key'] = df['has_valid_amount'].astype(int) * -1  # Valid amounts first (-1 < 0)
    
    # Sort to get valid records first, then by date (newest first)
    df = df.sort_values(['sale_id', 'sort_key', 'date'], ascending=[True, True, False])
    
    # Remove duplicates, keeping first occurrence (which will be valid record if available)
    before_dedup = len(df)
    df = df.drop_duplicates(subset=['sale_id'], keep='first')
    stats['duplicates_removed'] = before_dedup - len(df)
    
    # Remove the temporary columns
    df = df.drop(columns=['date_original', 'has_valid_amount', 'sort_key'], errors='ignore')
    
    # 5. Remove rows with null amount (after deduplication)
    before_null_removal = len(df)
    df = df[df['amount'].notna()].copy()
    stats['nulls_removed'] = before_null_removal - len(df)
    
    # 6. Join with product data
    products_df = products_df[['product_id', 'product_name']].copy()
    df = pd.merge(df, products_df, on='product_id', how='left')
    
    # 7. Map region codes to region names
    regions_df = pd.DataFrame(list(regions_dict.items()), columns=['region_code', 'region_name'])
    df = pd.merge(df, regions_df, on='region_code', how='left')
    
    # 8. Format date as YYYY-MM-DD string
    df['date'] = df['date'].dt.strftime('%Y-%m-%d')
    
    # 9. Reorder columns
    column_order = ['sale_id', 'product_id', 'product_name', 'region_code', 
                    'region_name', 'amount', 'date']
    df = df[column_order]
    
    # Final row count
    stats['total_clean_rows'] = len(df)
    
    return df, stats


def load(df, output_dir='output'):
    """Load cleaned data to CSV"""
    print(f"Loading cleaned data to {output_dir}/clean_sales.csv...")
    
    # Ensure output directory exists
    Path(output_dir).mkdir(exist_ok=True)
    
    # Save to CSV
    output_path = os.path.join(output_dir, 'clean_sales.csv')
    df.to_csv(output_path, index=False)
    
    return output_path


def generate_quality_report(stats, output_dir='output'):
    """Generate quality report JSON"""
    print(f"Generating quality report to {output_dir}/quality_report.json...")
    
    # Ensure output directory exists
    Path(output_dir).mkdir(exist_ok=True)
    
    # Calculate additional metrics
    stats['clean_percentage'] = round((stats['total_clean_rows'] / stats['total_raw_rows']) * 100, 2) if stats['total_raw_rows'] > 0 else 0
    
    # Save to JSON
    report_path = os.path.join(output_dir, 'quality_report.json')
    with open(report_path, 'w') as f:
        json.dump(stats, f, indent=2)
    
    return report_path


def run_etl_pipeline():
    """Main ETL pipeline execution"""
    print("=" * 50)
    print("Starting ETL Pipeline")
    print("=" * 50)
    
    try:
        # Extract
        sales_df, products_df, regions_dict = extract()
        
        # Transform
        cleaned_df, stats = transform(sales_df, products_df, regions_dict)
        
        # Load
        output_path = load(cleaned_df)
        
        # Generate quality report
        report_path = generate_quality_report(stats)
        
        print("=" * 50)
        print("ETL Pipeline Completed Successfully!")
        print(f"Cleaned data saved to: {output_path}")
        print(f"Quality report saved to: {report_path}")
        print("=" * 50)
        
        # Print summary statistics
        print("\nQuality Metrics:")
        print(f"  Total raw rows: {stats['total_raw_rows']}")
        print(f"  Total clean rows: {stats['total_clean_rows']} ({stats['clean_percentage']}%)")
        print(f"  Duplicates removed: {stats['duplicates_removed']}")
        print(f"  Nulls removed: {stats['nulls_removed']}")
        print(f"  Date format fixed: {stats['date_format_fixed']}")
        
        return True
        
    except Exception as e:
        print(f"ETL Pipeline Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    run_etl_pipeline()