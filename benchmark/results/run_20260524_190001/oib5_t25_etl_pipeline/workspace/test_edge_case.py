#!/usr/bin/env python3
"""Test the ETL pipeline with edge cases"""

import pandas as pd
import json
import os
import shutil

# Create test data with edge case: same sale_id, first invalid, then valid
test_sales = """sale_id,product_id,region_code,amount,date
S001,P01,R1,,2024-03-01  # Invalid amount
S001,P01,R1,150.00,2024-03-01  # Valid amount - should be kept
S002,P02,R2,89.50,03/02/2024
S003,P01,R1,150.00,2024-03-01
"""

# Create test directory
os.makedirs('test_output', exist_ok=True)

# Save test data
with open('test_raw_sales.csv', 'w') as f:
    f.write(test_sales)

# Copy other files for test
shutil.copy('raw_products.csv', 'test_raw_products.csv')
shutil.copy('raw_regions.json', 'test_raw_regions.json')

# Modify etl.py to use test files temporarily
with open('etl.py', 'r') as f:
    etl_content = f.read()

# Create a test version
etl_content = etl_content.replace("raw_sales.csv", "test_raw_sales.csv")
etl_content = etl_content.replace("raw_products.csv", "test_raw_products.csv")
etl_content = etl_content.replace("raw_regions.json", "test_raw_regions.json")
etl_content = etl_content.replace("output/clean_sales.csv", "test_output/clean_sales.csv")
etl_content = etl_content.replace("output/quality_report.json", "test_output/quality_report.json")

with open('test_etl.py', 'w') as f:
    f.write(etl_content)

# Run test
print("Running test with edge case: same sale_id with invalid then valid amount")
os.system("python test_etl.py")

# Check result
print("\nTest output:")
df = pd.read_csv('test_output/clean_sales.csv')
print(df)

# Check if S001 has valid amount
s001_row = df[df['sale_id'] == 'S001']
if len(s001_row) > 0:
    amount = s001_row['amount'].iloc[0]
    print(f"\nS001 amount: {amount}")
    if pd.notna(amount) and float(amount) == 150.0:
        print("✓ PASS: S001 kept the valid record with amount 150.00")
    else:
        print("✗ FAIL: S001 does not have the valid amount")
else:
    print("✗ FAIL: S001 not found in output")

# Cleanup
os.remove('test_raw_sales.csv')
os.remove('test_raw_products.csv')
os.remove('test_raw_regions.json')
os.remove('test_etl.py')
shutil.rmtree('test_output')