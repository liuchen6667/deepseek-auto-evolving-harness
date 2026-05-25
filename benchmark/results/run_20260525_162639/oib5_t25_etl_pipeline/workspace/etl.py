#!/usr/bin/env python3
"""
ETL Pipeline for Sales Data Cleaning
"""

import pandas as pd
import json
import os
from datetime import datetime
import sys


def extract_data():
    """Extract raw data from all source files"""
    print("Extracting data from source files...")
    
    try:
        # Read sales data
        sales_df = pd.read_csv('raw_sales.csv')
        
        # Read products data
        products_df = pd.read_csv('raw_products.csv')
        
        # Read regions data
        with open('raw_regions.json', 'r') as f:
            regions_dict = json.load(f)
        
        print(f"  - raw_sales.csv: {len(sales_df)} rows")
        print(f"  - raw_products.csv: {len(products_df)} rows")
        print(f"  - raw_regions.json: {len(regions_dict)} regions")
        
        return sales_df, products_df, regions_dict
    
    except FileNotFoundError as e:
        print(f"Error: Source file not found - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading source files: {e}")
        sys.exit(1)


def transform_data(sales_df, products_df, regions_dict):
    """Transform and clean the sales data"""
    print("\nTransforming data...")
    
    # Create quality metrics dictionary
    quality_metrics = {
        'total_raw_rows': len(sales_df),
        'duplicates_removed': 0,
        'nulls_removed': 0,
        'date_format_fixed': 0
    }
    
    # Step 1: Handle duplicates - keep last occurrence (to handle invalid->valid scenario)
    # First mark rows with invalid amount
    sales_df['amount_valid'] = pd.notna(sales_df['amount']) & (sales_df['amount'].astype(str).str.strip() != '')
    
    # Sort by sale_id and amount_valid (valid amounts first, then invalid)
    # This ensures that when we keep last occurrence, valid records win over invalid ones
    sales_df = sales_df.sort_values(['sale_id', 'amount_valid'], ascending=[True, False])
    
    # Remove duplicates, keeping the last occurrence (which will be valid if available)
    before_dedup = len(sales_df)
    sales_df = sales_df.drop_duplicates(subset=['sale_id'], keep='last')
    quality_metrics['duplicates_removed'] = before_dedup - len(sales_df)
    
    # Remove the temporary column
    sales_df = sales_df.drop(columns=['amount_valid'])
    
    # Step 2: Handle null/empty values in amount
    before_null_clean = len(sales_df)
    # Remove rows where amount is NaN or empty string
    sales_df = sales_df[pd.notna(sales_df['amount'])]
    sales_df = sales_df[sales_df['amount'].astype(str).str.strip() != '']
    quality_metrics['nulls_removed'] = before_null_clean - len(sales_df)
    
    # Convert amount to float
    sales_df['amount'] = pd.to_numeric(sales_df['amount'], errors='coerce')
    
    # Step 3: Standardize date format
    def standardize_date(date_str):
        """Convert date to YYYY-MM-DD format"""
        if pd.isna(date_str):
            return None
        
        date_str = str(date_str).strip()
        
        # Try different date formats
        date_formats = ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d']
        
        for fmt in date_formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        # If no format matches, return original
        return date_str
    
    # Apply date standardization
    original_dates = sales_df['date'].copy()
    sales_df['date'] = sales_df['date'].apply(standardize_date)
    
    # Count how many dates were fixed
    date_fixed_count = 0
    for orig, new in zip(original_dates, sales_df['date']):
        if pd.notna(orig) and pd.notna(new) and str(orig) != str(new):
            date_fixed_count += 1
    quality_metrics['date_format_fixed'] = date_fixed_count
    
    # Remove rows with invalid dates
    sales_df = sales_df[pd.notna(sales_df['date'])]
    
    # Step 4: Join with product data
    sales_df = pd.merge(sales_df, products_df[['product_id', 'product_name']], 
                        on='product_id', how='left')
    
    # Step 5: Map region codes to region names
    # Create region mapping DataFrame
    regions_df = pd.DataFrame(list(regions_dict.items()), 
                             columns=['region_code', 'region_name'])
    sales_df = pd.merge(sales_df, regions_df, on='region_code', how='left')
    
    # Reorder columns for clean output
    column_order = ['sale_id', 'product_id', 'product_name', 'region_code', 
                   'region_name', 'amount', 'date']
    sales_df = sales_df[column_order]
    
    # Sort by sale_id for consistent output
    sales_df = sales_df.sort_values('sale_id')
    
    quality_metrics['total_clean_rows'] = len(sales_df)
    
    return sales_df, quality_metrics


def load_data(clean_df, quality_metrics):
    """Load cleaned data to output files"""
    print("\nLoading data to output files...")
    
    # Ensure output directory exists
    os.makedirs('output', exist_ok=True)
    
    # Save cleaned sales data
    output_path = 'output/clean_sales.csv'
    clean_df.to_csv(output_path, index=False)
    print(f"  - Cleaned data saved to: {output_path} ({len(clean_df)} rows)")
    
    # Save quality report
    quality_path = 'output/quality_report.json'
    with open(quality_path, 'w') as f:
        json.dump(quality_metrics, f, indent=2)
    print(f"  - Quality report saved to: {quality_path}")
    
    # Print quality summary
    print("\nQuality Report Summary:")
    print(f"  - Total raw rows: {quality_metrics['total_raw_rows']}")
    print(f"  - Total clean rows: {quality_metrics['total_clean_rows']}")
    print(f"  - Duplicates removed: {quality_metrics['duplicates_removed']}")
    print(f"  - Nulls removed: {quality_metrics['nulls_removed']}")
    print(f"  - Date format fixed: {quality_metrics['date_format_fixed']}")
    
    return output_path, quality_path


def validate_output(clean_df):
    """Validate the cleaned data"""
    print("\nValidating cleaned data...")
    
    # Check for required columns
    required_columns = ['sale_id', 'product_id', 'product_name', 
                       'region_code', 'region_name', 'amount', 'date']
    
    missing_columns = [col for col in required_columns if col not in clean_df.columns]
    if missing_columns:
        print(f"  WARNING: Missing columns: {missing_columns}")
    else:
        print("  ✓ All required columns present")
    
    # Check for duplicates in sale_id
    duplicate_ids = clean_df['sale_id'].duplicated().sum()
    if duplicate_ids == 0:
        print("  ✓ No duplicate sale_id found")
    else:
        print(f"  WARNING: Found {duplicate_ids} duplicate sale_id(s)")
    
    # Check for null values
    null_counts = clean_df.isnull().sum()
    columns_with_nulls = null_counts[null_counts > 0]
    if len(columns_with_nulls) == 0:
        print("  ✓ No null values found")
    else:
        print(f"  WARNING: Null values found in: {list(columns_with_nulls.index)}")
    
    # Check date format consistency
    date_format_ok = True
    for date_str in clean_df['date']:
        if pd.isna(date_str):
            continue
        try:
            datetime.strptime(str(date_str), '%Y-%m-%d')
        except ValueError:
            date_format_ok = False
            break
    
    if date_format_ok:
        print("  ✓ All dates in YYYY-MM-DD format")
    else:
        print("  WARNING: Some dates not in YYYY-MM-DD format")
    
    return len(missing_columns) == 0 and duplicate_ids == 0


def main():
    """Main ETL pipeline function"""
    print("=" * 60)
    print("ETL Pipeline: Sales Data Cleaning")
    print("=" * 60)
    
    # Extract
    sales_df, products_df, regions_dict = extract_data()
    
    # Transform
    clean_df, quality_metrics = transform_data(sales_df, products_df, regions_dict)
    
    # Load
    output_path, quality_path = load_data(clean_df, quality_metrics)
    
    # Validate
    validation_passed = validate_output(clean_df)
    
    print("\n" + "=" * 60)
    if validation_passed:
        print("ETL Pipeline completed successfully!")
    else:
        print("ETL Pipeline completed with warnings.")
    print("=" * 60)
    
    return 0 if validation_passed else 1


if __name__ == "__main__":
    sys.exit(main())
