#!/usr/bin/env python3
"""
Simple Dataset Processor for ReAct Multi-Agent Benchmarking System

Consolidates all labeled datasets into a single randomized benchmark.
"""

import json
import jsonlines
from pathlib import Path
from datetime import datetime
import random

# Set random seed for reproducible results
random.seed(42)


def load_json_dataset(filepath: str):
    """Load dataset from JSON file."""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        print(f"✅ Loaded {len(data)} claims from {filepath}")
        return data
    except FileNotFoundError:
        print(f"❌ File not found: {filepath}")
        return []


def load_jsonl_dataset(filepath: str):
    """Load dataset from JSONL file."""
    try:
        data = []
        with jsonlines.open(filepath, 'r') as reader:
            for item in reader:
                data.append(item)
        print(f"✅ Loaded {len(data)} claims from {filepath}")
        return data
    except FileNotFoundError:
        print(f"❌ File not found: {filepath}")
        return []


def separate_inputs_outputs(claims):
    """Separate claim inputs from expected outputs."""
    inputs = []
    expected = []
    
    for claim in claims:
        # Skip invalid claims
        if not all(field in claim for field in ['claim_id', 'incident_date', 'report_date']):
            continue
        
        # Extract expected fields
        expected_status = claim.pop('expected_status', None)
        expected_reason = claim.pop('expected_reason', None)
        
        if expected_status:
            # Clean input claim
            input_claim = {k: v for k, v in claim.items() if not k.startswith('expected_')}
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


def main():
    """Process and consolidate all datasets."""
    print("🔄 Consolidating labeled datasets")
    print("=" * 40)
    
    # Set up output directory
    output_dir = Path("benchmarks/datasets")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    (output_dir / "inputs").mkdir(exist_ok=True)
    (output_dir / "expected").mkdir(exist_ok=True)
    (output_dir / "splits").mkdir(exist_ok=True)
    
    # Load all datasets
    all_claims = []
    
    datasets = [
        ('dataset/auto_claim_sample_inputs_450.json', 'json'),
        ('dataset/auto_claim_sample_inputs.json', 'json'),
        ('dataset/eval_combo_claims_labeled.jsonl', 'jsonl'),
        ('dataset/eval_nl_claims_labeled.jsonl', 'jsonl')
    ]
    
    for filepath, format_type in datasets:
        if format_type == 'json':
            claims = load_json_dataset(filepath)
        else:
            claims = load_jsonl_dataset(filepath)
        
        all_claims.extend(claims)
    
    print(f"\n📊 Total claims loaded: {len(all_claims)}")
    
    # Randomize and separate
    random.shuffle(all_claims)
    inputs, expected = separate_inputs_outputs(all_claims)
    
    print(f"✅ Processed {len(inputs)} valid claims")
    
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
        
        print(f"✅ {split_name}: {len(split_inputs)} claims")
    
    # Show distribution
    status_counts = {}
    for exp in expected:
        status = exp['expected_status']
        status_counts[status] = status_counts.get(status, 0) + 1
    
    print(f"\n📈 Distribution:")
    for status, count in sorted(status_counts.items()):
        percentage = (count / total) * 100
        print(f"  {status}: {count} ({percentage:.1f}%)")
    
    print(f"\n🎯 Done! Ready for benchmarking.")
    print(f"Usage: python3 benchmarks/scripts/benchmark_runner.py consolidated")


if __name__ == "__main__":
    main() 