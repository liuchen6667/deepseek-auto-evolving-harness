#!/usr/bin/env python3
"""
ETL Pipeline for Sales Data Processing

This script performs ETL (Extract, Transform, Load) operations on sales data:
1. Extract: Read raw sales, products, and regions data
2. Transform: Clean, deduplicate, and enrich sales data
3. Load: Save cleaned data to CSV
4. Quality Check: Generate quality report

Requirements:
- Python 3.6+
- pandas library
"""

import pandas as pd
import json
import os
from datetime import datetime
from typing import Dict, Tuple, Any


class ETLSalesPipeline:
    """ETL Pipeline for sales data processing."""
    
    def __init__(self):
        """Initialize the ETL pipeline."""
        self.quality_metrics = {
            'total_raw_rows': 0,
            'total_clean_rows': 0,
            'duplicates_removed': 0,
            'nulls_removed': 0,
            'date_format_fixed': 0
        }
        
    def extract(self) -> Tuple[pd.DataFrame, pd.DataFrame, Dict]:
        """
        Extract data from source files.
        
        Returns:
            Tuple containing:
            - sales_df: Raw sales DataFrame
            - products_df: Products DataFrame
            - regions_dict: Regions mapping dictionary
        """
        print("Extracting data from source files...")
        
        # Read sales data
        sales_df = pd.read_csv('raw_sales.csv')
        
        # Read products data
        products_df = pd.read_csv('raw_products.csv')
        
        # Read regions data
        with open('raw_regions.json', 'r') as f:
            regions_dict = json.load(f)
        
        print(f"  - Sales data: {len(sales_df)} rows")
        print(f"  - Products data: {len(products_df)} rows")
        print(f"  - Regions data: {len(regions_dict)} regions")
        
        return sales_df, products_df, regions_dict
    
    def transform(self, sales_df: pd.DataFrame, products_df: pd.DataFrame, 
                  regions_dict: Dict) -> pd.DataFrame:
        """
        Transform and clean the sales data.
        
        Args:
            sales_df: Raw sales DataFrame
            products_df: Products DataFrame
            regions_dict: Regions mapping dictionary
            
        Returns:
            Cleaned and enriched sales DataFrame
        """
        print("\nTransforming data...")
        
        # Store original row count for quality metrics
        self.quality_metrics['total_raw_rows'] = len(sales_df)
        
        # Step 1: Handle missing values
        # Remove rows where amount is NaN or empty string
        initial_rows = len(sales_df)
        
        # Convert empty strings to NaN for amount column
        sales_df['amount'] = pd.to_numeric(sales_df['amount'], errors='coerce')
        
        # Remove rows where amount is NaN (null)
        sales_df = sales_df.dropna(subset=['amount'])
        nulls_removed = initial_rows - len(sales_df)
        self.quality_metrics['nulls_removed'] = nulls_removed
        print(f"  - Removed {nulls_removed} rows with null/empty amount values")
        
        # Step 2: Standardize date format
        # Count rows with non-standard date format (contains '/')
        date_format_fixed = 0
        for idx, date_str in enumerate(sales_df['date']):
            if isinstance(date_str, str) and '/' in date_str:
                try:
                    # Try parsing as MM/DD/YYYY format
                    date_obj = datetime.strptime(date_str, '%m/%d/%Y')
                    sales_df.at[idx, 'date'] = date_obj.strftime('%Y-%m-%d')
                    date_format_fixed += 1
                except ValueError:
                    # Try parsing as DD/MM/YYYY format
                    try:
                        date_obj = datetime.strptime(date_str, '%d/%m/%Y')
                        sales_df.at[idx, 'date'] = date_obj.strftime('%Y-%m-%d')
                        date_format_fixed += 1
                    except ValueError:
                        # Keep original if cannot parse
                        pass
        
        self.quality_metrics['date_format_fixed'] = date_format_fixed
        print(f"  - Fixed date format for {date_format_fixed} rows")
        
        # Step 3: Remove duplicates while keeping the last valid record
        # This ensures that if a sale_id appears first with invalid data
        # and later with valid data, we keep the valid one
        initial_dedup_rows = len(sales_df)
        
        # Sort by sale_id to ensure consistent ordering
        sales_df = sales_df.sort_values('sale_id').reset_index(drop=True)
        
        # Remove duplicates, keeping the last occurrence
        # This handles the case where invalid records appear before valid ones
        sales_df = sales_df.drop_duplicates(subset=['sale_id'], keep='last')
        
        duplicates_removed = initial_dedup_rows - len(sales_df)
        self.quality_metrics['duplicates_removed'] = duplicates_removed
        print(f"  - Removed {duplicates_removed} duplicate rows (keeping last valid record)")
        
        # Step 4: Enrich data with product names
        print("  - Enriching with product names...")
        # Create product mapping dictionary
        product_map = dict(zip(products_df['product_id'], products_df['product_name']))
        sales_df['product_name'] = sales_df['product_id'].map(product_map)
        
        # Step 5: Enrich data with region names
        print("  - Enriching with region names...")
        sales_df['region_name'] = sales_df['region_code'].map(regions_dict)
        
        # Step 6: Reorder columns for better readability
        column_order = ['sale_id', 'product_id', 'product_name', 'region_code', 
                       'region_name', 'amount', 'date']
        sales_df = sales_df[column_order]
        
        # Step 7: Sort by date and sale_id
        sales_df = sales_df.sort_values(['date', 'sale_id']).reset_index(drop=True)
        
        # Update clean rows count
        self.quality_metrics['total_clean_rows'] = len(sales_df)
        
        print(f"  - Final clean data: {len(sales_df)} rows")
        
        return sales_df
    
    def load(self, clean_df: pd.DataFrame) -> None:
        """
        Load cleaned data to output file.
        
        Args:
            clean_df: Cleaned and transformed DataFrame
        """
        print("\nLoading cleaned data to output file...")
        
        # Ensure output directory exists
        os.makedirs('output', exist_ok=True)
        
        # Save to CSV
        output_path = 'output/clean_sales.csv'
        clean_df.to_csv(output_path, index=False)
        print(f"  - Saved to {output_path}")
        print(f"  - File size: {os.path.getsize(output_path):,} bytes")
    
    def generate_quality_report(self) -> None:
        """
        Generate quality report JSON file.
        """
        print("\nGenerating quality report...")
        
        # Ensure output directory exists
        os.makedirs('output', exist_ok=True)
        
        # Calculate additional metrics
        quality_data = {
            'pipeline_run_timestamp': datetime.now().isoformat(),
            'quality_metrics': self.quality_metrics,
            'data_quality_score': round(
                (self.quality_metrics['total_clean_rows'] / 
                 max(self.quality_metrics['total_raw_rows'], 1)) * 100, 2
            ),
            'summary': {
                'raw_data_quality': {
                    'duplicate_rate': round(
                        (self.quality_metrics['duplicates_removed'] / 
                         max(self.quality_metrics['total_raw_rows'], 1)) * 100, 2
                    ),
                    'null_rate': round(
                        (self.quality_metrics['nulls_removed'] / 
                         max(self.quality_metrics['total_raw_rows'], 1)) * 100, 2
                    )
                }
            }
        }
        
        # Save quality report
        output_path = 'output/quality_report.json'
        with open(output_path, 'w') as f:
            json.dump(quality_data, f, indent=2)
        
        print(f"  - Saved to {output_path}")
        
        # Print summary
        print("\n" + "="*50)
        print("QUALITY REPORT SUMMARY")
        print("="*50)
        print(f"Total raw rows: {self.quality_metrics['total_raw_rows']}")
        print(f"Total clean rows: {self.quality_metrics['total_clean_rows']}")
        print(f"Duplicates removed: {self.quality_metrics['duplicates_removed']}")
        print(f"Nulls removed: {self.quality_metrics['nulls_removed']}")
        print(f"Date format fixed: {self.quality_metrics['date_format_fixed']}")
        print(f"Data quality score: {quality_data['data_quality_score']}%")
        print("="*50)
    
    def run(self) -> None:
        """
        Run the complete ETL pipeline.
        """
        print("="*60)
        print("STARTING ETL PIPELINE")
        print("="*60)
        
        try:
            # Extract
            sales_df, products_df, regions_dict = self.extract()
            
            # Transform
            clean_df = self.transform(sales_df, products_df, regions_dict)
            
            # Load
            self.load(clean_df)
            
            # Quality Check
            self.generate_quality_report()
            
            print("\n" + "="*60)
            print("ETL PIPELINE COMPLETED SUCCESSFULLY")
            print("="*60)
            
        except FileNotFoundError as e:
            print(f"\nERROR: Required file not found - {e}")
            print("Please ensure all input files exist:")
            print("  - raw_sales.csv")
            print("  - raw_products.csv")
            print("  - raw_regions.json")
            raise
            
        except Exception as e:
            print(f"\nERROR: Pipeline failed - {e}")
            raise


def main():
    """Main function to run the ETL pipeline."""
    # Check if required files exist
    required_files = ['raw_sales.csv', 'raw_products.csv', 'raw_regions.json']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"ERROR: Missing required files: {missing_files}")
        return
    
    # Run the pipeline
    pipeline = ETLSalesPipeline()
    pipeline.run()


if __name__ == "__main__":
    main()