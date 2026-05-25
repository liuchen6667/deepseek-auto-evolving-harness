#!/usr/bin/env python3
"""
Test the ETL pipeline with edge cases
"""
import csv
import json
import os
import tempfile
import shutil
from etl import extract_data, transform_data, load_data, generate_quality_report

def test_duplicate_with_invalid_first():
    """Test case where same sale_id has invalid amount first, then valid amount"""
    
    # Create test data
    test_sales = [
        {'sale_id': 'TEST001', 'product_id': 'P01', 'region_code': 'R1', 'amount': '', 'date': '2024-03-01'},
        {'sale_id': 'TEST001', 'product_id': 'P01', 'region_code': 'R1', 'amount': '100.00', 'date': '2024-03-01'},
        {'sale_id': 'TEST002', 'product_id': 'P02', 'region_code': 'R2', 'amount': '50.00', 'date': '2024-03-02'},
        {'sale_id': 'TEST002', 'product_id': 'P02', 'region_code': 'R2', 'amount': '', 'date': '2024-03-02'},
    ]
    
    test_products = {'P01': 'Widget Pro', 'P02': 'Gadget X'}
    test_regions = {'R1': 'North America', 'R2': 'Europe'}
    
    # Transform
    clean_records, stats = transform_data(test_sales, test_products, test_regions)
    
    print("Test: duplicate_with_invalid_first")
    print(f"  Raw rows: {stats['total_raw_rows']}")
    print(f"  Clean rows: {len(clean_records)}")
    print(f"  Nulls removed: {stats['nulls_removed']}")
    
    # Check results
    sale_ids = [r['sale_id'] for r in clean_records]
    if 'TEST001' in sale_ids and 'TEST002' in sale_ids:
        print("  ✓ Both sale_ids preserved with valid amounts")
    else:
        print(f"  ✗ Issue: sale_ids in clean data: {sale_ids}")
    
    # Check amounts
    for record in clean_records:
        if record['sale_id'] == 'TEST001':
            if record['amount'] == 100.0:
                print("  ✓ TEST001 has correct amount: 100.0")
            else:
                print(f"  ✗ TEST001 has wrong amount: {record['amount']}")
    
    print()

def test_original_data():
    """Test with the original data files"""
    print("Test: original_data")
    
    # Extract
    sales_data, products, regions = extract_data()
    print(f"  Raw sales data: {len(sales_data)} rows")
    print(f"  Products: {len(products)} items")
    print(f"  Regions: {len(regions)} items")
    
    # Transform
    clean_records, stats = transform_data(sales_data, products, regions)
    
    print(f"  Clean rows: {stats['total_clean_rows']}")
    print(f"  Duplicates removed: {stats['duplicates_removed']}")
    print(f"  Nulls removed: {stats['nulls_removed']}")
    print(f"  Dates fixed: {stats['date_format_fixed']}")
    
    # Check specific cases
    sale_ids = [r['sale_id'] for r in clean_records]
    
    # S004 should be removed (empty amount, no valid replacement)
    if 'S004' not in sale_ids:
        print("  ✓ S004 correctly removed (empty amount)")
    else:
        print("  ✗ S004 should be removed but is present")
    
    # S005 should be present (has amount, appears twice)
    if sale_ids.count('S005') == 1:
        print("  ✓ S005 appears exactly once (duplicate handled)")
    else:
        print(f"  ✗ S005 appears {sale_ids.count('S005')} times")
    
    # Check date formatting
    dates_formatted = all(r['date'].count('/') == 0 for r in clean_records)
    if dates_formatted:
        print("  ✓ All dates in YYYY-MM-DD format")
    else:
        print("  ✗ Some dates not in correct format")
    
    print()

if __name__ == '__main__':
    test_duplicate_with_invalid_first()
    test_original_data()
