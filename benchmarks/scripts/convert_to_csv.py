#!/usr/bin/env python3
"""
Convert consolidated JSONL datasets to CSV and XLSX formats for easier analysis.
"""

import json
import pandas as pd
from pathlib import Path
import sys

def convert_jsonl_to_dataframe(jsonl_file_path):
    """Convert a JSONL file to a pandas DataFrame."""
    data = []
    with open(jsonl_file_path, 'r') as file:
        for line in file:
            data.append(json.loads(line.strip()))
    return pd.DataFrame(data)

def main():
    """Convert the consolidated JSONL files to CSV and XLSX."""
    print("🔄 Converting JSONL files to CSV and XLSX formats...")
    
    # Define file paths
    datasets_dir = Path("benchmarks/datasets")
    inputs_file = datasets_dir / "inputs" / "consolidated_inputs.jsonl"
    expected_file = datasets_dir / "expected" / "consolidated_expected.jsonl"
    
    # Create output directory
    output_dir = datasets_dir / "csv_exports"
    output_dir.mkdir(exist_ok=True)
    
    # Check if input files exist
    if not inputs_file.exists():
        print(f"❌ Input file not found: {inputs_file}")
        sys.exit(1)
    
    if not expected_file.exists():
        print(f"❌ Expected file not found: {expected_file}")
        sys.exit(1)
    
    try:
        # Convert inputs file
        print(f"📂 Processing {inputs_file.name}...")
        inputs_df = convert_jsonl_to_dataframe(inputs_file)
        
        # Save inputs as CSV
        inputs_csv = output_dir / "consolidated_inputs.csv"
        inputs_df.to_csv(inputs_csv, index=False)
        print(f"   ✅ Saved CSV: {inputs_csv}")
        
        # Save inputs as XLSX
        inputs_xlsx = output_dir / "consolidated_inputs.xlsx"
        inputs_df.to_excel(inputs_xlsx, index=False, engine='openpyxl')
        print(f"   ✅ Saved XLSX: {inputs_xlsx}")
        
        # Convert expected file
        print(f"📂 Processing {expected_file.name}...")
        expected_df = convert_jsonl_to_dataframe(expected_file)
        
        # Save expected as CSV
        expected_csv = output_dir / "consolidated_expected.csv"
        expected_df.to_csv(expected_csv, index=False)
        print(f"   ✅ Saved CSV: {expected_csv}")
        
        # Save expected as XLSX
        expected_xlsx = output_dir / "consolidated_expected.xlsx"
        expected_df.to_excel(expected_xlsx, index=False, engine='openpyxl')
        print(f"   ✅ Saved XLSX: {expected_xlsx}")
        
        # Create a combined file with both inputs and expected
        print("📊 Creating combined dataset...")
        
        # Merge on claim_id (assuming both have this column)
        if 'claim_id' in inputs_df.columns and 'claim_id' in expected_df.columns:
            combined_df = inputs_df.merge(expected_df, on='claim_id', how='left', suffixes=('', '_expected'))
            
            # Save combined as CSV
            combined_csv = output_dir / "consolidated_combined.csv"
            combined_df.to_csv(combined_csv, index=False)
            print(f"   ✅ Saved combined CSV: {combined_csv}")
            
            # Save combined as XLSX
            combined_xlsx = output_dir / "consolidated_combined.xlsx"
            combined_df.to_excel(combined_xlsx, index=False, engine='openpyxl')
            print(f"   ✅ Saved combined XLSX: {combined_xlsx}")
            
        # Print summary statistics
        print(f"\n📊 SUMMARY")
        print(f"   Inputs records: {len(inputs_df):,}")
        print(f"   Expected records: {len(expected_df):,}")
        if 'claim_id' in inputs_df.columns and 'claim_id' in expected_df.columns:
            print(f"   Combined records: {len(combined_df):,}")
        print(f"   Inputs columns: {len(inputs_df.columns)}")
        print(f"   Expected columns: {len(expected_df.columns)}")
        
        # Show column names
        print(f"\n📋 INPUT COLUMNS:")
        for i, col in enumerate(inputs_df.columns, 1):
            print(f"   {i:2d}. {col}")
        
        print(f"\n📋 EXPECTED COLUMNS:")
        for i, col in enumerate(expected_df.columns, 1):
            print(f"   {i:2d}. {col}")
        
        print(f"\n🎯 All files saved to: {output_dir}")
        print("✅ Conversion completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during conversion: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 