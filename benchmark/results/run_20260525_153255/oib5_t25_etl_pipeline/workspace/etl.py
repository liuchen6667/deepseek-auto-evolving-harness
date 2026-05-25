#!/usr/bin/env python3
"""
ETL Pipeline for Sales Data Processing
Extracts, transforms, and loads sales data from multiple sources.
"""

import pandas as pd
import json
import os
import sys
from datetime import datetime
from pathlib import Path


def extract_data():
    """Extract data from all source files."""
    print("Extracting data from source files...")
    
    try:
        # Read sales data
        sales_df = pd.read_csv('raw_sales.csv')
        print(f"  - raw_sales.csv: {len(sales_df)} rows")
        
        # Read products data
        products_df = pd.read_csv('raw_products.csv')
        print(f"  - raw_products.csv: {len(products_df)} rows")
        
        # Read regions data
        with open('raw_regions.json', 'r') as f:
            regions_data = json.load(f)
        print(f"  - raw_regions.json: {len(regions_data)} regions")
        
        return sales_df, products_df, regions_data
        
    except FileNotFoundError as e:
        print(f"Error: Source file not found - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading source files: {e}")
        sys.exit(1)


def transform_sales_data(sales_df, products_df, regions_data):
    """
    Transform sales data:
    1. Remove duplicates (keep last valid record per sale_id)
    2. Handle null values
    3. Standardize date format
    4. Enrich with product and region names
    """
    print("Transforming sales data...")
    
    # Initialize quality metrics
    quality_metrics = {
        'total_raw_rows': len(sales_df),
        'duplicates_removed': 0,
        'nulls_removed': 0,
        'date_format_fixed': 0
    }
    
    # Create a copy to avoid modifying original
    df = sales_df.copy()
    
    # 1. Handle date format - convert to YYYY-MM-DD
    def parse_date(date_str):
        """Parse date from various formats to YYYY-MM-DD."""
        if pd.isna(date_str) or str(date_str).strip() == '':
            return None
            
        date_str = str(date_str).strip()
        
        # Try different date formats
        for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d']:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        # If no format matches, return original
        return date_str
    
    df['date_parsed'] = df['date'].apply(parse_date)
    
    # Count date format fixes (comparing original vs parsed)
    date_format_fixed = df.apply(
        lambda row: 0 if pd.isna(row['date']) or pd.isna(row['date_parsed']) 
        else (1 if row['date'] != row['date_parsed'] else 0), 
        axis=1
    ).sum()
    quality_metrics['date_format_fixed'] = date_format_fixed
    
    # Replace date column with parsed dates
    df['date'] = df['date_parsed']
    df = df.drop(columns=['date_parsed'])
    
    # 2. Handle null/empty values
    # Remove rows where amount is NaN or empty string
    initial_rows = len(df)
    df = df[~df['amount'].isna()]
    df = df[df['amount'].astype(str).str.strip() != '']
    
    # Convert amount to numeric, coercing errors to NaN
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    df = df[~df['amount'].isna()]
    
    nulls_removed = initial_rows - len(df)
    quality_metrics['nulls_removed'] = nulls_removed
    
    # 3. Remove duplicates - keep last valid record per sale_id
    # Sort by date (most recent last) to ensure we keep latest
    df['date_dt'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.sort_values('date_dt')
    
    # Mark duplicates
    duplicates_mask = df.duplicated(subset=['sale_id'], keep='last')
    duplicates_removed = duplicates_mask.sum()
    
    # Remove duplicates (keeping last occurrence)
    df = df[~duplicates_mask]
    df = df.drop(columns=['date_dt'])
    
    quality_metrics['duplicates_removed'] = duplicates_removed
    
    # 4. Enrich with product names
    product_dict = dict(zip(products_df['product_id'], products_df['product_name']))
    df['product_name'] = df['product_id'].map(product_dict)
    
    # 5. Enrich with region names
    df['region_name'] = df['region_code'].map(regions_data)
    
    # Reorder columns for better readability
    column_order = [
        'sale_id', 'product_id', 'product_name', 
        'region_code', 'region_name', 'amount', 'date'
    ]
    df = df[column_order]
    
    # Final clean rows count
    quality_metrics['total_clean_rows'] = len(df)
    
    print(f"  - Removed {duplicates_removed} duplicate rows")
    print(f"  - Removed {nulls_removed} rows with null/empty values")
    print(f"  - Fixed {date_format_fixed} date formats")
    print(f"  - Clean data: {len(df)} rows")
    
    return df, quality_metrics


def load_data(clean_df, output_dir='output'):
    """Load clean data to output file."""
    print("Loading clean data...")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, 'clean_sales.csv')
    clean_df.to_csv(output_path, index=False)
    
    print(f"  - Clean data saved to: {output_path}")
    print(f"  - File size: {os.path.getsize(output_path)} bytes")
    
    return output_path


def generate_quality_report(quality_metrics, output_dir='output'):
    """Generate quality report JSON file."""
    print("Generating quality report...")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Convert numpy types to Python native types for JSON serialization
    report_metrics = {}
    for key, value in quality_metrics.items():
        # Convert numpy int64 to Python int
        if hasattr(value, 'item'):  # Check if it's a numpy scalar
            report_metrics[key] = value.item()
        else:
            report_metrics[key] = value
    
    # Calculate derived metrics
    report_metrics['clean_percentage'] = round(
        (report_metrics['total_clean_rows'] / report_metrics['total_raw_rows'] * 100), 
        2
    ) if report_metrics['total_raw_rows'] > 0 else 0
    
    report_metrics['run_timestamp'] = datetime.now().isoformat()
    
    output_path = os.path.join(output_dir, 'quality_report.json')
    
    with open(output_path, 'w') as f:
        json.dump(report_metrics, f, indent=2)
    
    print(f"  - Quality report saved to: {output_path}")
    
    return output_path


def validate_output(clean_df):
    """Validate the output data for quality."""
    print("Validating output data...")
    
    issues = []
    
    # Check for null values
    null_counts = clean_df.isnull().sum()
    for col, count in null_counts.items():
        if count > 0:
            issues.append(f"Column '{col}' has {count} null values")
    
    # Check date format
    date_format_valid = clean_df['date'].str.match(r'^\d{4}-\d{2}-\d{2}$').all()
    if not date_format_valid:
        issues.append("Not all dates are in YYYY-MM-DD format")
    
    # Check for duplicates
    duplicate_count = clean_df.duplicated(subset=['sale_id']).sum()
    if duplicate_count > 0:
        issues.append(f"Found {duplicate_count} duplicate sale_id values")
    
    # Check amount values
    negative_amounts = (clean_df['amount'] < 0).sum()
    if negative_amounts > 0:
        issues.append(f"Found {negative_amounts} negative amount values")
    
    if issues:
        print("  - Validation issues found:")
        for issue in issues:
            print(f"    * {issue}")
        return False
    else:
        print("  - All validations passed!")
        return True


def main():
    """Main ETL pipeline execution."""
    print("=" * 60)
    print("Starting ETL Pipeline")
    print("=" * 60)
    
    start_time = datetime.now()
    
    try:
        # Step 1: Extract
        sales_df, products_df, regions_data = extract_data()
        
        # Step 2: Transform
        clean_df, quality_metrics = transform_sales_data(
            sales_df, products_df, regions_data
        )
        
        # Step 3: Load
        output_file = load_data(clean_df)
        
        # Step 4: Generate quality report
        report_file = generate_quality_report(quality_metrics)
        
        # Step 5: Validate output
        is_valid = validate_output(clean_df)
        
        # Calculate execution time
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        # Read the quality report to get all metrics including clean_percentage
        with open(report_file, 'r') as f:
            final_metrics = json.load(f)
        
        print("\n" + "=" * 60)
        print("ETL Pipeline Completed Successfully!")
        print("=" * 60)
        print(f"Execution time: {execution_time:.2f} seconds")
        print(f"Output files:")
        print(f"  - Clean data: {output_file}")
        print(f"  - Quality report: {report_file}")
        print(f"Summary:")
        print(f"  - Raw rows: {final_metrics['total_raw_rows']}")
        print(f"  - Clean rows: {final_metrics['total_clean_rows']}")
        print(f"  - Clean percentage: {final_metrics['clean_percentage']}%")
        
        if not is_valid:
            print("\nWarning: Some validation issues were found.")
            return 1
            
        return 0
        
    except Exception as e:
        print(f"\nError in ETL pipeline: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())