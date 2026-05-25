#!/usr/bin/env python3
"""
ETL Pipeline for Sales Data Processing
"""
import csv
import json
import os
from datetime import datetime
from collections import OrderedDict
import pandas as pd


def extract_data():
    """Extract data from all source files"""
    
    # Read raw_sales.csv
    with open('raw_sales.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        sales_data = list(reader)
    
    # For debugging: print raw data count
    print(f"  Raw sales data: {len(sales_data)} rows (excluding header)")
    
    # Read raw_products.csv
    with open('raw_products.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        products = {row['product_id']: row['product_name'] for row in reader}
    
    # Read raw_regions.json
    with open('raw_regions.json', 'r', encoding='utf-8') as f:
        regions = json.load(f)
    
    return sales_data, products, regions


def transform_data(sales_data, products, regions):
    """Transform the sales data with cleaning and enrichment"""
    
    # Track statistics for quality report
    stats = {
        'total_raw_rows': len(sales_data),
        'duplicates_removed': 0,
        'nulls_removed': 0,
        'date_format_fixed': 0
    }
    
    # Step 1: Handle duplicates and invalid records
    # We'll keep the last valid record for each sale_id
    records_by_id = OrderedDict()
    
    for row in sales_data:
        sale_id = row['sale_id']
        
        # Check if amount is empty or whitespace only
        amount = row['amount'] or ''
        if amount.strip() == '':
            # This is an invalid record, but we still track it
            # It might be overwritten by a valid record later
            if sale_id not in records_by_id:
                records_by_id[sale_id] = {'row': row, 'valid': False}
            continue
        
        # This is a valid record (has amount)
        records_by_id[sale_id] = {'row': row, 'valid': True}
    
    # Count nulls removed (records that were invalid and not replaced by valid ones)
    stats['nulls_removed'] = sum(1 for record in records_by_id.values() if not record['valid'])
    
    # Filter only valid records
    valid_records = [record['row'] for record in records_by_id.values() if record['valid']]
    
    # Count duplicates removed (based on original data)
    stats['duplicates_removed'] = len(sales_data) - len(records_by_id)
    
    # Step 2: Process each valid record
    clean_records = []
    
    for row in valid_records:
        # Convert date format
        date_str = row['date']
        try:
            # Try parsing with different formats
            if '/' in date_str:
                # Format: MM/DD/YYYY
                date_obj = datetime.strptime(date_str, '%m/%d/%Y')
                formatted_date = date_obj.strftime('%Y-%m-%d')
                stats['date_format_fixed'] += 1
            else:
                # Assume YYYY-MM-DD format
                # Validate it
                datetime.strptime(date_str, '%Y-%m-%d')
                formatted_date = date_str
        except ValueError:
            # If date is invalid, skip this record
            continue
        
        # Get product name
        product_id = row['product_id']
        product_name = products.get(product_id, f"Unknown ({product_id})")
        
        # Get region name
        region_code = row['region_code']
        region_name = regions.get(region_code, f"Unknown ({region_code})")
        
        # Create clean record
        clean_record = {
            'sale_id': row['sale_id'],
            'product_id': product_id,
            'product_name': product_name,
            'region_code': region_code,
            'region_name': region_name,
            'amount': float(row['amount']),
            'date': formatted_date
        }
        
        clean_records.append(clean_record)
    
    stats['total_clean_rows'] = len(clean_records)
    
    return clean_records, stats


def load_data(clean_records, output_path='output/clean_sales.csv'):
    """Load clean data to output file"""
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Define field order
    fieldnames = ['sale_id', 'product_id', 'product_name', 
                  'region_code', 'region_name', 'amount', 'date']
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(clean_records)
    
    print(f"Clean data saved to {output_path} ({len(clean_records)} rows)")


def generate_quality_report(stats, report_path='output/quality_report.json'):
    """Generate quality report JSON file"""
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2)
    
    print(f"Quality report saved to {report_path}")


def run_etl_pipeline():
    """Main ETL pipeline execution"""
    
    print("Starting ETL Pipeline...")
    
    # Extract
    print("Extracting data from source files...")
    sales_data, products, regions = extract_data()
    
    # Transform
    print("Transforming and cleaning data...")
    clean_records, stats = transform_data(sales_data, products, regions)
    
    # Load
    print("Loading clean data...")
    load_data(clean_records)
    
    # Quality Check
    print("Generating quality report...")
    generate_quality_report(stats)
    
    # Print summary
    print("\nETL Pipeline Complete!")
    print(f"  Raw rows: {stats['total_raw_rows']}")
    print(f"  Clean rows: {stats['total_clean_rows']}")
    print(f"  Duplicates removed: {stats['duplicates_removed']}")
    print(f"  Nulls removed: {stats['nulls_removed']}")
    print(f"  Dates fixed: {stats['date_format_fixed']}")


if __name__ == '__main__':
    run_etl_pipeline()