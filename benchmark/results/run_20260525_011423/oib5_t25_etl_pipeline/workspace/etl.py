#!/usr/bin/env python3
"""
ETL Pipeline for Sales Data Processing
Extracts data from CSV and JSON files, transforms and cleans it,
then loads to output CSV with quality report.
"""

import pandas as pd
import numpy as np
import json
import os
import sys
from datetime import datetime
from pathlib import Path


class ETLSalesPipeline:
    def __init__(self, input_dir=".", output_dir="output"):
        """Initialize ETL pipeline with input and output directories."""
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        
        # File paths
        self.sales_file = self.input_dir / "raw_sales.csv"
        self.products_file = self.input_dir / "raw_products.csv"
        self.regions_file = self.input_dir / "raw_regions.json"
        
        # Output files
        self.output_file = self.output_dir / "clean_sales.csv"
        self.report_file = self.output_dir / "quality_report.json"
        
        # Initialize dataframes
        self.raw_sales = None
        self.products = None
        self.regions = None
        self.clean_sales = None
        
        # Quality metrics
        self.quality_metrics = {
            "total_raw_rows": 0,
            "total_clean_rows": 0,
            "duplicates_removed": 0,
            "nulls_removed": 0,
            "date_format_fixed": 0
        }
    
    def extract(self):
        """Extract data from all source files."""
        print("Extracting data from source files...")
        
        try:
            # Read sales data
            self.raw_sales = pd.read_csv(self.sales_file)
            self.quality_metrics["total_raw_rows"] = len(self.raw_sales)
            print(f"  - Loaded {len(self.raw_sales)} sales records")
            
            # Read products data
            self.products = pd.read_csv(self.products_file)
            print(f"  - Loaded {len(self.products)} product records")
            
            # Read regions data
            with open(self.regions_file, 'r') as f:
                regions_dict = json.load(f)
            # Convert to DataFrame for easier merging
            self.regions = pd.DataFrame(
                list(regions_dict.items()), 
                columns=['region_code', 'region_name']
            )
            print(f"  - Loaded {len(self.regions)} region mappings")
            
        except FileNotFoundError as e:
            print(f"Error: File not found - {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Error during extraction: {e}")
            sys.exit(1)
    
    def transform(self):
        """Transform and clean the sales data."""
        print("Transforming and cleaning data...")
        
        if self.raw_sales is None:
            print("Error: No sales data loaded. Run extract() first.")
            return
        
        # Create a copy for transformation
        df = self.raw_sales.copy()
        
        # Step 1: Handle amount nulls and blanks
        # Remove rows where amount is NaN or empty string
        initial_rows = len(df)
        
        # Convert amount to string first to handle both NaN and empty strings
        df['amount'] = df['amount'].astype(str)
        
        # Remove rows where amount is NaN, empty string, or whitespace only
        df = df[~df['amount'].isna() & (df['amount'].str.strip() != '')]
        
        # Convert amount back to float for numeric operations
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
        
        # Remove any rows where conversion failed
        df = df[~df['amount'].isna()]
        
        nulls_removed = initial_rows - len(df)
        self.quality_metrics["nulls_removed"] = nulls_removed
        print(f"  - Removed {nulls_removed} rows with null/empty amounts")
        
        # Step 2: Standardize date format
        # Count how many dates need formatting
        date_format_fixed = 0
        
        def standardize_date(date_str):
            """Convert date to YYYY-MM-DD format."""
            nonlocal date_format_fixed
            
            if pd.isna(date_str):
                return None
            
            date_str = str(date_str).strip()
            
            # Try different date formats
            for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y']:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    if fmt != '%Y-%m-%d':
                        date_format_fixed += 1
                    return dt.strftime('%Y-%m-%d')
                except ValueError:
                    continue
            
            # If no format matches, return original (will be filtered out later)
            return date_str
        
        df['date'] = df['date'].apply(standardize_date)
        self.quality_metrics["date_format_fixed"] = date_format_fixed
        print(f"  - Fixed date format for {date_format_fixed} records")
        
        # Remove rows with invalid dates
        initial_date_rows = len(df)
        df = df[df['date'].notna()]
        invalid_dates_removed = initial_date_rows - len(df)
        if invalid_dates_removed > 0:
            print(f"  - Removed {invalid_dates_removed} rows with invalid dates")
            self.quality_metrics["nulls_removed"] += invalid_dates_removed
        
        # Step 3: Remove duplicates, keeping the last occurrence
        # This handles the requirement: if same sale_id has invalid then valid record,
        # keep the valid one (last occurrence in original order)
        initial_duplicate_check = len(df)
        
        # Sort by sale_id to ensure consistent ordering
        df = df.sort_values('sale_id')
        
        # Remove duplicates, keeping the last occurrence
        df = df.drop_duplicates(subset=['sale_id'], keep='last')
        
        duplicates_removed = initial_duplicate_check - len(df)
        self.quality_metrics["duplicates_removed"] = duplicates_removed
        print(f"  - Removed {duplicates_removed} duplicate records")
        
        # Step 4: Merge with product data
        print("  - Merging with product data...")
        df = pd.merge(
            df,
            self.products[['product_id', 'product_name']],
            on='product_id',
            how='left'
        )
        
        # Step 5: Merge with region data
        print("  - Merging with region data...")
        df = pd.merge(
            df,
            self.regions,
            on='region_code',
            how='left'
        )
        
        # Step 6: Reorder columns for final output
        column_order = [
            'sale_id', 'product_id', 'product_name', 
            'region_code', 'region_name', 'amount', 'date'
        ]
        df = df[column_order]
        
        # Step 7: Sort by date and sale_id for clean output
        df = df.sort_values(['date', 'sale_id'])
        
        # Reset index
        df = df.reset_index(drop=True)
        
        self.clean_sales = df
        self.quality_metrics["total_clean_rows"] = len(df)
        
        print(f"  - Transformation complete. Clean records: {len(df)}")
    
    def load(self):
        """Load cleaned data to output file."""
        print("Loading cleaned data to output file...")
        
        if self.clean_sales is None:
            print("Error: No cleaned data available. Run transform() first.")
            return
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(exist_ok=True)
        
        try:
            # Save to CSV
            self.clean_sales.to_csv(self.output_file, index=False)
            print(f"  - Clean data saved to {self.output_file}")
            
            # Generate quality report
            self._generate_quality_report()
            print(f"  - Quality report saved to {self.report_file}")
            
        except Exception as e:
            print(f"Error during loading: {e}")
            sys.exit(1)
    
    def _generate_quality_report(self):
        """Generate JSON quality report with metrics."""
        report_data = {
            "pipeline_run_timestamp": datetime.now().isoformat(),
            "source_files": {
                "sales": str(self.sales_file),
                "products": str(self.products_file),
                "regions": str(self.regions_file)
            },
            "output_file": str(self.output_file),
            "quality_metrics": self.quality_metrics,
            "data_quality_score": self._calculate_quality_score()
        }
        
        with open(self.report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
    
    def _calculate_quality_score(self):
        """Calculate a simple data quality score (0-100)."""
        if self.quality_metrics["total_raw_rows"] == 0:
            return 0
        
        clean_ratio = self.quality_metrics["total_clean_rows"] / self.quality_metrics["total_raw_rows"]
        score = int(clean_ratio * 100)
        
        # Penalize for high duplicate rate
        duplicate_ratio = self.quality_metrics["duplicates_removed"] / max(1, self.quality_metrics["total_raw_rows"])
        if duplicate_ratio > 0.2:  # More than 20% duplicates
            score = max(0, score - 10)
        
        return min(100, max(0, score))
    
    def run(self):
        """Run the complete ETL pipeline."""
        print("=" * 60)
        print("Starting ETL Pipeline for Sales Data")
        print("=" * 60)
        
        # Run pipeline steps
        self.extract()
        self.transform()
        self.load()
        
        print("=" * 60)
        print("ETL Pipeline Completed Successfully")
        print("=" * 60)
        
        # Print summary
        print("\nSummary:")
        print(f"  Raw records: {self.quality_metrics['total_raw_rows']}")
        print(f"  Clean records: {self.quality_metrics['total_clean_rows']}")
        print(f"  Duplicates removed: {self.quality_metrics['duplicates_removed']}")
        print(f"  Nulls/Invalid removed: {self.quality_metrics['nulls_removed']}")
        print(f"  Date formats fixed: {self.quality_metrics['date_format_fixed']}")
        print(f"  Data quality score: {self._calculate_quality_score()}/100")
        
        return self.clean_sales


def main():
    """Main function to run the ETL pipeline."""
    # Create and run pipeline
    pipeline = ETLSalesPipeline()
    
    try:
        clean_data = pipeline.run()
        
        # Print first few rows of cleaned data
        print("\nFirst 5 rows of cleaned data:")
        print(clean_data.head().to_string(index=False))
        
    except Exception as e:
        print(f"Pipeline failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()