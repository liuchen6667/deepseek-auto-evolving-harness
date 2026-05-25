#!/usr/bin/env python3
"""Test script to verify ETL pipeline logic."""

import pandas as pd
import json

def test_etl_logic():
    """Test the ETL logic with the provided data."""
    
    print("Testing ETL pipeline logic...")
    
    # Read original data
    raw_sales = pd.read_csv('raw_sales.csv')
    print(f"1. Raw sales data: {len(raw_sales)} rows")
    print("   Sample data:")
    print(raw_sales.head())
    
    # Read cleaned data
    clean_sales = pd.read_csv('output/clean_sales.csv')
    print(f"\n2. Cleaned sales data: {len(clean_sales)} rows")
    print("   Sample data:")
    print(clean_sales.head())
    
    # Read quality report
    with open('output/quality_report.json', 'r') as f:
        quality_report = json.load(f)
    
    print(f"\n3. Quality report:")
    for key, value in quality_report.items():
        if key != 'run_timestamp':
            print(f"   - {key}: {value}")
    
    # Test 1: Check for duplicates in cleaned data
    duplicate_count = clean_sales.duplicated(subset=['sale_id']).sum()
    print(f"\n4. Duplicate check: {duplicate_count} duplicates found (should be 0)")
    
    # Test 2: Check for null values
    null_counts = clean_sales.isnull().sum()
    total_nulls = null_counts.sum()
    print(f"5. Null value check: {total_nulls} null values found (should be 0)")
    
    # Test 3: Check date format
    date_format_valid = clean_sales['date'].str.match(r'^\d{4}-\d{2}-\d{2}$').all()
    print(f"6. Date format check: All dates in YYYY-MM-DD format? {date_format_valid}")
    
    # Test 4: Check product_name mapping
    products = pd.read_csv('raw_products.csv')
    product_dict = dict(zip(products['product_id'], products['product_name']))
    clean_sales['expected_product_name'] = clean_sales['product_id'].map(product_dict)
    product_mapping_correct = (clean_sales['product_name'] == clean_sales['expected_product_name']).all()
    print(f"7. Product mapping check: All product names correctly mapped? {product_mapping_correct}")
    
    # Test 5: Check region_name mapping
    with open('raw_regions.json', 'r') as f:
        regions = json.load(f)
    clean_sales['expected_region_name'] = clean_sales['region_code'].map(regions)
    region_mapping_correct = (clean_sales['region_name'] == clean_sales['expected_region_name']).all()
    print(f"8. Region mapping check: All region names correctly mapped? {region_mapping_correct}")
    
    # Test 6: Check which rows were removed
    raw_ids = set(raw_sales['sale_id'])
    clean_ids = set(clean_sales['sale_id'])
    removed_ids = raw_ids - clean_ids
    print(f"\n9. Removed sale_ids: {sorted(removed_ids)}")
    
    # Check why these were removed
    print("   Reasons for removal:")
    for sale_id in sorted(removed_ids):
        row = raw_sales[raw_sales['sale_id'] == sale_id]
        print(f"   - {sale_id}: amount = {row['amount'].values[0]}, duplicates of: {list(row.index)}")
    
    # Test 7: Verify duplicate handling logic
    print("\n10. Duplicate handling verification:")
    # S001 appears twice in raw data
    s001_rows = raw_sales[raw_sales['sale_id'] == 'S001']
    print(f"   - S001 appears {len(s001_rows)} times in raw data")
    print(f"   - S001 appears {len(clean_sales[clean_sales['sale_id'] == 'S001'])} times in clean data")
    
    # S005 appears twice in raw data
    s005_rows = raw_sales[raw_sales['sale_id'] == 'S005']
    print(f"   - S005 appears {len(s005_rows)} times in raw data")
    print(f"   - S005 appears {len(clean_sales[clean_sales['sale_id'] == 'S005'])} times in clean data")
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    test_etl_logic()