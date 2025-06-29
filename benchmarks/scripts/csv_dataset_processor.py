#!/usr/bin/env python3
"""
CSV Dataset Processor for ReAct Multi-Agent Benchmarking System

Processes CSV datasets and converts them to JSONL format for benchmarking.
"""

import csv
import jsonlines
from pathlib import Path
from datetime import datetime
import random

# Set random seed for reproducible results
random.seed(42)


def load_csv_dataset(filepath: str):
    """Load dataset from CSV file."""
    try:
        data = []
        with open(filepath, 'r', encoding='utf-8-sig') as f:  # utf-8-sig handles BOM
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
        print(f"✅ Loaded {len(data)} claims from {filepath}")
        return data
    except FileNotFoundError:
        print(f"❌ File not found: {filepath}")
        return []


def clean_and_convert_claim(claim):
    """Clean and convert claim data types."""
    cleaned = {}
    
    # String fields
    string_fields = [
        'claim_id', 'state', 'cancellation_reason', 'driver_name', 
        'driver_license_status', 'driver_use_type', 'vin', 'damage_description', 
        'damage_type', 'loss_location_flood_zone', 'cat_event_code', 
        'at_fault_party', 'third_party_insurer', 'primary_med_provider',
        '_source_dataset', 'narrative', 'expected_status', 'expected_reason'
    ]
    
    # Date fields
    date_fields = [
        'incident_date', 'report_date', 'policy_start_date', 'policy_end_date',
        'coverage_suspension_start', 'coverage_suspension_end'
    ]
    
    # Integer fields
    integer_fields = [
        'per_claim_limit', 'annual_aggregate_limit', 'remaining_aggregate_limit',
        'endorsement_rental_days_allowed', 'endorsement_rental_daily_cap',
        'odometer_at_loss', 'telematics_odometer', 'repair_estimate',
        'actual_cash_value', 'rental_days_claimed', 'loss_of_use_daily_rate',
        'insured_liability_percent', 'policy_max_reporting_days',
        'days_since_policy_start', 'days_since_incident'
    ]
    
    # Boolean fields
    boolean_fields = [
        'endorsement_um_uim', 'endorsement_diminished_value', 'endorsement_rideshare_use',
        'driver_listed_on_policy', 'driver_excluded', 'driver_under_influence',
        'aftermarket_mods', 'recall_active', 'police_report_attached', 'injuries_reported'
    ]
    
    for key, value in claim.items():
        if not value or value.strip() == '':
            cleaned[key] = None
            continue
            
        if key in string_fields:
            cleaned[key] = value.strip()
        elif key in date_fields:
            try:
                # Handle MM/DD/YY format
                if '/' in value:
                    parts = value.split('/')
                    if len(parts) == 3:
                        month, day, year = parts
                        # Convert YY to 20YY if needed
                        if len(year) == 2:
                            year = '20' + year
                        cleaned[key] = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                    else:
                        cleaned[key] = value.strip()
                else:
                    # Already in YYYY-MM-DD format
                    cleaned[key] = value.strip()
            except:
                cleaned[key] = value.strip()
        elif key in integer_fields:
            try:
                cleaned[key] = int(float(value))
            except:
                cleaned[key] = 0
        elif key in boolean_fields:
            cleaned[key] = value.strip().upper() in ['TRUE', '1', 'YES']
        else:
            # Default to string
            cleaned[key] = value.strip()
    
    return cleaned


def separate_inputs_outputs(claims):
    """Separate claim inputs from expected outputs."""
    inputs = []
    expected = []
    
    for claim in claims:
        # Skip invalid claims
        if not all(field in claim for field in ['claim_id', 'incident_date', 'report_date']):
            continue
        
        # Extract expected fields (make a copy to avoid modifying original)
        expected_status = claim.get('expected_status', None)
        expected_reason = claim.get('expected_reason', None)
        
        if expected_status:
            # Remove fields not needed for processing
            fields_to_remove = [
                '_source_dataset', 'policy_max_reporting_days', 
                'days_since_policy_start', 'days_since_incident', 'narrative',
                'expected_status', 'expected_reason'
            ]
            
            # Clean input claim
            input_claim = {k: v for k, v in claim.items() 
                          if k not in fields_to_remove}
            inputs.append(input_claim)
            
            # Store expected output
            expected.append({
                'claim_id': claim['claim_id'],
                'expected_status': expected_status,
                'expected_reason': expected_reason
            })
    
    return inputs, expected


def save_jsonl(data, filepath):
    """Save data to JSONL format."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    with jsonlines.open(filepath, 'w') as writer:
        writer.write_all(data)
    
    print(f"📁 Saved {len(data)} items to {filepath}")


def create_manifest(total_claims, splits_info, output_dir):
    """Create a manifest file with dataset information."""
    manifest = {
        "dataset_name": "insurance_dataset_v1",
        "total_claims": total_claims,
        "created_at": datetime.now().isoformat(),
        "splits": splits_info,
        "source_file": "benchmarks/datasets/raw/insurance_dataset v1.csv"
    }
    
    manifest_path = output_dir / "manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"📄 Created manifest: {manifest_path}")


def main():
    """Process and consolidate CSV dataset."""
    print("🔄 Processing CSV dataset")
    print("=" * 40)
    
    # Set up paths
    csv_file = Path("benchmarks/datasets/raw/insurance_dataset v1.csv")
    output_dir = Path("benchmarks/datasets")
    
    # Create output directories
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "inputs").mkdir(exist_ok=True)
    (output_dir / "expected").mkdir(exist_ok=True)
    (output_dir / "splits").mkdir(exist_ok=True)
    
    # Load and process CSV
    if not csv_file.exists():
        print(f"❌ CSV file not found: {csv_file}")
        return
    
    raw_claims = load_csv_dataset(csv_file)
    
    # Clean and convert data types
    print("🧹 Cleaning and converting data types...")
    cleaned_claims = []
    for claim in raw_claims:
        try:
            cleaned = clean_and_convert_claim(claim)
            cleaned_claims.append(cleaned)
        except Exception as e:
            print(f"⚠️ Skipping claim {claim.get('claim_id', 'unknown')}: {e}")
    
    print(f"✅ Processed {len(cleaned_claims)} valid claims")
    
    # Randomize and separate
    random.shuffle(cleaned_claims)
    inputs, expected = separate_inputs_outputs(cleaned_claims)
    
    print(f"✅ Separated {len(inputs)} input/output pairs")
    
    # Save full dataset
    full_inputs_path = output_dir / "inputs" / "consolidated_inputs.jsonl"
    full_expected_path = output_dir / "expected" / "consolidated_expected.jsonl"
    
    save_jsonl(inputs, full_inputs_path)
    save_jsonl(expected, full_expected_path)
    
    # Create splits (70% train, 15% val, 15% test)
    total = len(inputs)
    train_end = int(total * 0.7)
    val_end = train_end + int(total * 0.15)
    
    train_inputs = inputs[:train_end]
    train_expected = expected[:train_end]
    val_inputs = inputs[train_end:val_end]
    val_expected = expected[train_end:val_end]
    test_inputs = inputs[val_end:]
    test_expected = expected[val_end:]
    
    # Save splits
    splits_info = {}
    splits = [
        ('train', train_inputs, train_expected),
        ('val', val_inputs, val_expected),
        ('test', test_inputs, test_expected)
    ]
    
    for split_name, split_inputs, split_expected in splits:
        inputs_path = output_dir / "splits" / f"consolidated_{split_name}_inputs.jsonl"
        expected_path = output_dir / "splits" / f"consolidated_{split_name}_expected.jsonl"
        
        save_jsonl(split_inputs, inputs_path)
        save_jsonl(split_expected, expected_path)
        
        splits_info[split_name] = len(split_inputs)
        print(f"✅ {split_name}: {len(split_inputs)} claims")
    
    # Show distribution
    status_counts = {}
    for exp in expected:
        status = exp['expected_status']
        status_counts[status] = status_counts.get(status, 0) + 1
    
    print(f"\n📈 Status Distribution:")
    for status, count in sorted(status_counts.items()):
        percentage = (count / total) * 100
        print(f"  {status}: {count} ({percentage:.1f}%)")
    
    # Create manifest
    create_manifest(total, splits_info, output_dir)
    
    print(f"\n🎯 Dataset processing complete!")
    print(f"📊 Total claims: {total}")
    print(f"📁 Files saved to: {output_dir}")
    print(f"\nReady for benchmarking with:")
    print(f"  python benchmarks/scripts/quick_test.py")


if __name__ == "__main__":
    import json
    main() 