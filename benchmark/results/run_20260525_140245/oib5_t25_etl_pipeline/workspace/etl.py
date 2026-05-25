#!/usr/bin/env python3
"""
ETL Pipeline for Sales Data

Extract: Read raw_sales.csv, raw_products.csv, raw_regions.json
Transform: Clean, deduplicate, standardize date format, join with reference data
Load: Write cleaned data to output/clean_sales.csv
Quality Check: Generate quality report in output/quality_report.json
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
import re


def extract():
    """Extract data from all source files"""
    # Read raw sales data
    sales_df = pd.read_csv('raw_sales.csv')
    
    # Read product reference data
    products_df = pd.read_csv('raw_products.csv')
    
    # Read region reference data
    with open('raw_regions.json', 'r') as f:
        regions_dict = json.load(f)
    
    return sales_df, products_df, regions_dict


def transform(sales_df, products_df, regions_dict):
    """
    Transform the sales data:
    1. Remove duplicates (keep last occurrence for each sale_id)
    2. Handle nulls (skip rows with empty/blank amount)
    3. Standardize date format to YYYY-MM-DD
    4. Join with product and region data
    """
    # Store original row count for quality report
    total_raw_rows = len(sales_df)
    
    # 1. Remove duplicates - keep last occurrence for each sale_id
    # This ensures if same sale_id appears with invalid amount first, then valid amount later,
    # we keep the valid one (last occurrence)
    sales_df = sales_df.drop_duplicates(subset=['sale_id'], keep='last')
    duplicates_removed = total_raw_rows - len(sales_df)
    
    # 2. Handle nulls and empty values in amount column
    # First, convert empty strings to NaN
    sales_df['amount'] = sales_df['amount'].replace(r'^\s*$', np.nan, regex=True)
    
    # Store count of rows with null amount before removal
    null_rows_before = sales_df['amount'].isna().sum()
    
    # Remove rows with null amount
    sales_df = sales_df.dropna(subset=['amount'])
    nulls_removed = null_rows_before
    
    # 3. Standardize date format to YYYY-MM-DD
    def standardize_date(date_str):
        """Convert date string to YYYY-MM-DD format"""
        if pd.isna(date_str):
            return np.nan
        
        # Try different date formats
        date_formats = ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d']
        
        for fmt in date_formats:
            try:
                date_obj = datetime.strptime(str(date_str), fmt)
                return date_obj.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        # If no format matches, return original
        return str(date_str)
    
    # Count date format fixes
    date_format_fixed = 0
    for idx, date_val in enumerate(sales_df['date']):
        original = str(date_val)
        standardized = standardize_date(date_val)
        if original != standardized and standardized != 'nan':
            date_format_fixed += 1
        sales_df.at[sales_df.index[idx], 'date'] = standardized
    
    # 4. Join with product data
    sales_df = pd.merge(sales_df, products_df[['product_id', 'product_name']], 
                        on='product_id', how='left')
    
    # 5. Join with region data
    # Convert region dict to DataFrame
    regions_df = pd.DataFrame(list(regions_dict.items()), 
                              columns=['region_code', 'region_name'])
    sales_df = pd.merge(sales_df, regions_df, on='region_code', how='left')
    
    # Reorder columns for output
    column_order = ['sale_id', 'product_id', 'product_name', 'region_code', 
                    'region_name', 'amount', 'date']
    sales_df = sales_df[column_order]
    
    # Calculate final clean rows
    total_clean_rows = len(sales_df)
    
    # Prepare quality metrics
    quality_metrics = {
        'total_raw_rows': int(total_raw_rows),
        'total_clean_rows': int(total_clean_rows),
        'duplicates_removed': int(duplicates_removed),
        'nulls_removed': int(nulls_removed),
        'date_format_fixed': int(date_format_fixed)
    }
    
    return sales_df, quality_metrics


def load(sales_df, output_dir='output'):
    """Load cleaned data to CSV file"""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Write cleaned data to CSV
    output_path = os.path.join(output_dir, 'clean_sales.csv')
    sales_df.to_csv(output_path, index=False)
    
    return output_path


def generate_quality_report(quality_metrics, output_dir='output'):
    """Generate quality report as JSON"""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Write quality report to JSON
    report_path = os.path.join(output_dir, 'quality_report.json')
    with open(report_path, 'w') as f:
        json.dump(quality_metrics, f, indent=2)
    
    return report_path


def main():
    """Main ETL pipeline execution"""
    print("Starting ETL pipeline...")
    
    # Extract
    print("1. Extracting data from source files...")
    sales_df, products_df, regions_dict = extract()
    print(f"   - Loaded {len(sales_df)} sales records")
    print(f"   - Loaded {len(products_df)} product records")
    print(f"   - Loaded {len(regions_dict)} region mappings")
    
    # Transform
    print("2. Transforming data...")
    cleaned_sales_df, quality_metrics = transform(sales_df, products_df, regions_dict)
    
    # Load
    print("3. Loading cleaned data...")
    output_path = load(cleaned_sales_df)
    print(f"   - Cleaned data saved to {output_path}")
    print(f"   - Cleaned records: {len(cleaned_sales_df)}")
    
    # Quality Report
    print("4. Generating quality report...")
    report_path = generate_quality_report(quality_metrics)
    print(f"   - Quality report saved to {report_path}")
    
    # Print quality metrics
    print("\nQuality Metrics:")
    for key, value in quality_metrics.items():
        print(f"   - {key}: {value}")
    
    print("\nETL pipeline completed successfully!")


if __name__ == '__main__':
    main()
