#!/usr/bin/env python3
"""
ETL Pipeline for Sales Data Processing

This script:
1. Extracts data from raw_sales.csv, raw_products.csv, and raw_regions.json
2. Transforms the data:
   - Removes duplicates (keeping the last valid record per sale_id)
   - Handles null values (skips rows with empty amount or all whitespace)
   - Standardizes date format to YYYY-MM-DD
   - Joins with product information
   - Joins with region information
3. Loads cleaned data to output/clean_sales.csv
4. Generates quality report to output/quality_report.json
"""

import pandas as pd
import json
import os
from datetime import datetime
from pathlib import Path
import sys

def extract_data():
    """Extract data from all source files."""
    print("Extracting data from source files...")
    
    # Read sales data
    sales_df = pd.read_csv('raw_sales.csv')
    
    # Read product data
    products_df = pd.read_csv('raw_products.csv')
    
    # Read region data
    with open('raw_regions.json', 'r') as f:
        region_dict = json.load(f)
    regions_df = pd.DataFrame(list(region_dict.items()), columns=['region_code', 'region_name'])
    
    return sales_df, products_df, regions_df

def transform_data(sales_df, products_df, regions_df):
    """Transform and clean the sales data."""
    print("Transforming data...")
    
    # Initialize quality metrics
    quality_metrics = {
        'total_raw_rows': len(sales_df),
        'duplicates_removed': 0,
        'nulls_removed': 0,
        'date_format_fixed': 0
    }
    
    # Make a copy to avoid modifying original
    df = sales_df.copy()
    
    # 1. Handle date format conversion
    def parse_date(date_str):
        """Parse date from various formats to YYYY-MM-DD."""
        if pd.isna(date_str):
            return None
        
        date_str = str(date_str).strip()
        
        # Try different date formats
        date_formats = ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y']
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt).strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        # If no format matches, return original
        return date_str
    
    # Apply date parsing
    original_dates = df['date'].copy()
    df['date'] = df['date'].apply(parse_date)
    
    # Count date format fixes
    date_format_fixed = (df['date'] != original_dates).sum()
    quality_metrics['date_format_fixed'] = int(date_format_fixed)
    
    # 2. Handle amount column - convert to numeric, handle empty strings
    # First, clean the amount column
    df['amount_clean'] = pd.to_numeric(df['amount'], errors='coerce')
    
    # 3. Remove rows with null amount or all whitespace
    # Create mask for valid rows
    valid_amount_mask = df['amount_clean'].notna()
    
    # Also check if original amount is empty string or whitespace
    amount_str_mask = df['amount'].apply(lambda x: str(x).strip() != '' if pd.notna(x) else False)
    valid_amount_mask = valid_amount_mask & amount_str_mask
    
    # Count rows to be removed due to null amount
    nulls_removed = (~valid_amount_mask).sum()
    quality_metrics['nulls_removed'] = int(nulls_removed)
    
    # Filter valid rows
    df = df[valid_amount_mask].copy()
    
    # 4. Remove duplicates - keep last valid record per sale_id
    # Sort by date to ensure we keep the most recent valid record
    df['date_parsed'] = pd.to_datetime(df['date'])
    df = df.sort_values('date_parsed')
    
    # Mark duplicates, keeping the last occurrence
    duplicates_mask = df.duplicated(subset=['sale_id'], keep='last')
    
    # Count duplicates to be removed
    duplicates_removed = duplicates_mask.sum()
    quality_metrics['duplicates_removed'] = int(duplicates_removed)
    
    # Remove duplicates (keeping last)
    df = df[~duplicates_mask].copy()
    
    # 5. Join with product information
    df = pd.merge(df, products_df[['product_id', 'product_name']], 
                  on='product_id', how='left')
    
    # 6. Join with region information
    df = pd.merge(df, regions_df, on='region_code', how='left')
    
    # 7. Select and order final columns
    final_columns = [
        'sale_id', 'product_id', 'product_name', 'region_code', 
        'region_name', 'amount', 'date'
    ]
    
    # Ensure all columns exist (in case of merge issues)
    for col in final_columns:
        if col not in df.columns:
            df[col] = ''
    
    df = df[final_columns]
    
    # Reset index
    df = df.reset_index(drop=True)
    
    # Update final row count
    quality_metrics['total_clean_rows'] = len(df)
    
    return df, quality_metrics

def load_data(df, output_dir='output'):
    """Load cleaned data to output file."""
    print(f"Loading data to {output_dir}/clean_sales.csv...")
    
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Save to CSV
    output_path = os.path.join(output_dir, 'clean_sales.csv')
    df.to_csv(output_path, index=False)
    
    print(f"Cleaned data saved to {output_path}")
    return output_path

def generate_quality_report(quality_metrics, output_dir='output'):
    """Generate quality report JSON file."""
    print(f"Generating quality report to {output_dir}/quality_report.json...")
    
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Save to JSON
    output_path = os.path.join(output_dir, 'quality_report.json')
    with open(output_path, 'w') as f:
        json.dump(quality_metrics, f, indent=2)
    
    print(f"Quality report saved to {output_path}")
    return output_path

def run_etl_pipeline():
    """Main ETL pipeline function."""
    print("Starting ETL pipeline...")
    
    try:
        # Step 1: Extract
        sales_df, products_df, regions_df = extract_data()
        
        # Step 2: Transform
        cleaned_df, quality_metrics = transform_data(sales_df, products_df, regions_df)
        
        # Step 3: Load
        load_data(cleaned_df)
        
        # Step 4: Generate quality report
        generate_quality_report(quality_metrics)
        
        # Print summary
        print("\n" + "="*50)
        print("ETL Pipeline Completed Successfully!")
        print("="*50)
        print(f"Raw rows processed: {quality_metrics['total_raw_rows']}")
        print(f"Clean rows output: {quality_metrics['total_clean_rows']}")
        print(f"Duplicates removed: {quality_metrics['duplicates_removed']}")
        print(f"Null rows removed: {quality_metrics['nulls_removed']}")
        print(f"Date formats fixed: {quality_metrics['date_format_fixed']}")
        print("="*50)
        
        return True
        
    except Exception as e:
        print(f"Error in ETL pipeline: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_etl_pipeline()
    sys.exit(0 if success else 1)