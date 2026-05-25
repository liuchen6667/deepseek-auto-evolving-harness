#!/usr/bin/env python3
"""
Test script to verify ETL handles the scenario where same sale_id
has invalid amount first, then valid amount later.
"""

import pandas as pd
import os
from pathlib import Path

# Create test data
test_sales_data = """sale_id,product_id,region_code,amount,date
S100,P01,R1,,2024-03-01
S100,P01,R1,150.00,2024-03-01
S101,P02,R2,200.00,03/02/2024
S101,P02,R2,200.00,2024-03-02
S102,P03,R3,300.00,2024-03-03
"""

test_products_data = """product_id,product_name,category
P01,Widget Pro,Electronics
P02,Gadget X,Accessories
P03,DataHub,Software
"""

test_regions_data = '{"R1": "North America", "R2": "Europe", "R3": "Asia Pacific"}'

# Create test directory
test_dir = Path("test_scenario")
test_dir.mkdir(exist_ok=True)

# Write test files
(test_dir / "raw_sales.csv").write_text(test_sales_data)
(test_dir / "raw_products.csv").write_text(test_products_data)
(test_dir / "raw_regions.json").write_text(test_regions_data)

print("Test scenario created:")
print("1. S100: First row has empty amount, second row has valid amount (150.00)")
print("2. S101: First row has different date format, second row has same data")
print("3. S102: Single valid record")
print()

# Run ETL on test data
import etl

# Temporarily change to test directory
original_dir = os.getcwd()
os.chdir(test_dir)

try:
    # Create and run pipeline
    pipeline = etl.ETLSalesPipeline()
    clean_data = pipeline.run()
    
    print("\nTest Results:")
    print("=" * 60)
    
    # Check if S100 is in cleaned data
    s100_data = clean_data[clean_data['sale_id'] == 'S100']
    if len(s100_data) == 1:
        print("✓ S100: Correctly kept the valid record")
        print(f"  Amount: {s100_data.iloc[0]['amount']}")
    else:
        print("✗ S100: Issue - expected 1 record, got", len(s100_data))
    
    # Check if S101 is in cleaned data (should be 1 record)
    s101_data = clean_data[clean_data['sale_id'] == 'S101']
    if len(s101_data) == 1:
        print("✓ S101: Correctly deduplicated")
        print(f"  Date: {s101_data.iloc[0]['date']}")
    else:
        print("✗ S101: Issue - expected 1 record, got", len(s101_data))
    
    # Check if S102 is in cleaned data
    s102_data = clean_data[clean_data['sale_id'] == 'S102']
    if len(s102_data) == 1:
        print("✓ S102: Correctly included")
        print(f"  Amount: {s102_data.iloc[0]['amount']}")
    else:
        print("✗ S102: Issue - expected 1 record, got", len(s102_data))
    
    print("\nAll cleaned data:")
    print(clean_data.to_string(index=False))
    
finally:
    # Change back to original directory
    os.chdir(original_dir)
    
    # Clean up test directory
    import shutil
    shutil.rmtree(test_dir)
    print(f"\nCleaned up test directory: {test_dir}")