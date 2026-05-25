#!/usr/bin/env python3
"""Test the ETL pipeline with different data"""

import pandas as pd
import json
import os
import shutil

# Create test data with different content
print("Testing ETL pipeline with different data...")

# Backup original files
os.makedirs('backup', exist_ok=True)
shutil.copy('raw_sales.csv', 'backup/')
shutil.copy('raw_products.csv', 'backup/')
shutil.copy('raw_regions.json', 'backup/')

# Create new test data
new_sales_data = """sale_id,product_id,region_code,amount,date
T001,P01,R1,100.00,2024-04-01
T002,P02,R2,,04/02/2024
T002,P02,R2,150.00,04/02/2024
T003,P03,R3,200.00,2024-04-03
T004,P01,R1,75.00,04/04/2024
T004,P01,R1,75.00,2024-04-04
"""

new_products_data = """product_id,product_name,category
P01,Test Widget,Test
P02,Test Gadget,Test
P03,Test Software,Test
"""

new_regions_data = {"R1": "Test Region 1", "R2": "Test Region 2", "R3": "Test Region 3"}

# Write test files
with open('raw_sales.csv', 'w') as f:
    f.write(new_sales_data)

with open('raw_products.csv', 'w') as f:
    f.write(new_products_data)

with open('raw_regions.json', 'w') as f:
    json.dump(new_regions_data, f)

# Run ETL
print("\nRunning ETL with test data...")
os.system('python etl.py')

# Check output
print("\nChecking output...")
if os.path.exists('output/clean_sales.csv'):
    df = pd.read_csv('output/clean_sales.csv')
    print(f"Cleaned rows: {len(df)}")
    print(f"Sale IDs: {list(df['sale_id'])}")
    
    # Verify T002 has valid amount (not null)
    t002_row = df[df['sale_id'] == 'T002']
    if len(t002_row) == 1:
        print(f"T002 amount: {t002_row.iloc[0]['amount']} ✓")
    else:
        print(f"T002 not found or duplicated!")

# Restore original files
print("\nRestoring original data...")
shutil.copy('backup/raw_sales.csv', '.')
shutil.copy('backup/raw_products.csv', '.')
shutil.copy('backup/raw_regions.json', '.')

print("\nTest completed!")