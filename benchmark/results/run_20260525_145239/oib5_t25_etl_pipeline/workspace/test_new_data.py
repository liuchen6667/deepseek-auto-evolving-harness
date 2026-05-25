#!/usr/bin/env python3
"""
Test ETL with different data
"""
import csv
import json
import os
import shutil

# Create test directory
test_dir = "test_run"
if os.path.exists(test_dir):
    shutil.rmtree(test_dir)
os.makedirs(test_dir)

# Create test sales data with various edge cases
test_sales_content = """sale_id,product_id,region_code,amount,date
T001,P01,R1,100.00,2024-01-01
T001,P01,R1,,2024-01-01  # Duplicate with empty amount first
T002,P02,R2,,2024-01-02  # Empty amount, no valid replacement
T003,P01,R3,75.00,01/03/2024  # Different date format
T003,P01,R3,75.00,01/03/2024  # Exact duplicate
T004,P03,R1,200.00,2024-01-04
T004,P03,R1,250.00,2024-01-04  # Same ID, different amount (should keep last)
T005,P02,R2,150.00,01/05/2024
T006,P01,R3,,2024-01-06
T006,P01,R3,180.00,2024-01-06  # Empty then valid
T007,P03,R1,95.00,2024-01-07
"""

# Create test products
test_products_content = """product_id,product_name,category
P01,Test Widget,TestCat
P02,Test Gadget,TestCat
P03,Test Software,TestCat
"""

# Create test regions
test_regions = {"R1": "Test Region 1", "R2": "Test Region 2", "R3": "Test Region 3"}

# Write test files
with open(os.path.join(test_dir, "raw_sales.csv"), "w") as f:
    f.write(test_sales_content)

with open(os.path.join(test_dir, "raw_products.csv"), "w") as f:
    f.write(test_products_content)

with open(os.path.join(test_dir, "raw_regions.json"), "w") as f:
    json.dump(test_regions, f)

print(f"Test files created in {test_dir}/")
print("\nTest sales data analysis:")
print("Total rows (including header):", test_sales_content.count('\n'))
print("Unique sale_ids in test data: T001, T002, T003, T004, T005, T006, T007")
print("Expected behavior:")
print("- T001: Has valid then invalid, should keep valid")
print("- T002: Only invalid, should be removed")
print("- T003: Duplicate valid, should keep one")
print("- T004: Two different valid amounts, should keep last (250)")
print("- T005: Single valid record")
print("- T006: Invalid then valid, should keep valid")
print("- T007: Single valid record")
print("\nExpected clean rows: 6 (T001, T003, T004, T005, T006, T007)")
