# Simple Accuracy Benchmarking System

This document describes the benchmarking system for the ReAct Multi-Agent Auto Insurance Claim Processing System.

## Overview

The benchmarking system tests our ReAct agents against **real-world anonymized insurance claims** with known expected outcomes. We have **700 labeled claims** merged from 4 source datasets into a single unified benchmark.

### Key Features

- **📊 Consolidated Dataset**: Single unified benchmark from 4 source datasets (700 claims)
- **🔀 Randomized Data**: Eliminates dataset-specific bias through randomization
- **📈 Proper Splits**: Train (489), Validation (105), Test (106) for robust evaluation
- **🚀 Simple Tools**: Straightforward benchmarking without unnecessary complexity

## Dataset Organization

### Unified Dataset Structure
```
benchmarks/datasets/
├── inputs/                                # Clean claim inputs
│   └── consolidated_inputs.jsonl          # 700 randomized claims
├── expected/                              # Expected outcomes  
│   └── consolidated_expected.jsonl        # 700 expected answers
└── splits/                                # Train/validation/test splits
    ├── consolidated_train_inputs.jsonl    # 489 training claims (70%)
    ├── consolidated_train_expected.jsonl  # 489 training labels
    ├── consolidated_val_inputs.jsonl      # 105 validation claims (15%)
    ├── consolidated_val_expected.jsonl    # 105 validation labels  
    ├── consolidated_test_inputs.jsonl     # 106 test claims (15%)
    └── consolidated_test_expected.jsonl   # 106 test labels
```

### Dataset Statistics

**Total Claims: 700** (merged and randomized from 4 source datasets)

**Distribution:**
- **REJECTED**: 311 claims (44.4%)
- **APPROVED**: 177 claims (25.3%)
- **PARTIAL**: 122 claims (17.4%)
- **ESCALATE**: 90 claims (12.9%)

**Splits:**
- **Training**: 489 claims (70%)
- **Validation**: 105 claims (15%)
- **Test**: 106 claims (15%)

## Benchmark Tools

### 1. Dataset Processor (`benchmarks/scripts/dataset_processor.py`)

**Purpose**: Merge all labeled datasets into a unified benchmark.

```bash
# Consolidate all datasets (one-time setup)
make process-datasets
```

**What it does**:
- Merges 4 labeled datasets into one
- Randomizes combined dataset
- Creates train/validation/test splits
- Saves as JSONL files

### 2. Quick Test (`benchmarks/scripts/quick_test.py`)

**Purpose**: Fast testing for development.

```bash
# Quick test with 5 claims
make quick-benchmark

# Custom claim count
python3 benchmarks/scripts/quick_test.py consolidated 10
```

**Features**:
- Fast execution (< 1 minute)
- Configurable claim count
- Perfect for prompt development

### 3. Benchmark Runner (`benchmarks/scripts/benchmark_runner.py`)

**Purpose**: Full benchmarking with all claims.

```bash
# Benchmark all 700 claims
make benchmark

# Benchmark specific splits
make benchmark-train  # 489 claims
make benchmark-val    # 105 claims  
make benchmark-test   # 106 claims

# Custom benchmarks
python3 benchmarks/scripts/benchmark_runner.py consolidated
python3 benchmarks/scripts/benchmark_runner.py consolidated_test
```

**Features**:
- Processes all claims in dataset
- Shows progress every 50 claims
- Saves results to file
- Memory efficient

## Usage Examples

### Quick Development Testing
```bash
# Test 5 claims from consolidated dataset
python3 benchmarks/scripts/quick_test.py consolidated 5

# Test 10 claims from validation split
python3 benchmarks/scripts/quick_test.py consolidated_val 10
```

### Full Benchmarking
```bash
# Setup (one-time)
make process-datasets

# Quick test
make quick-benchmark

# Full benchmark
make benchmark

# Test specific splits
make benchmark-test   # Final evaluation
```

## Sample Output

### Quick Test Output
```
🔍 Quick Test - consolidated dataset (5 claims)
==================================================

📋 Claim 1/5: CLM-2024-001234
   Expected: APPROVED
   ✅ Actual: APPROVED

📋 Claim 2/5: CLM-2024-001235
   Expected: REJECTED
   ❌ Actual: PARTIAL

...

🎯 Results: 4/5 correct (80.0%)
```

### Benchmark Output
```
🎯 Benchmark Runner - consolidated
==================================================
📂 Loading claims from consolidated...
✅ Loaded 700 claims from benchmarks/datasets/inputs/consolidated_inputs.jsonl
✅ Loaded 700 claims from benchmarks/datasets/expected/consolidated_expected.jsonl
📊 Processing 700 claims...

   Progress: 50/700 (78.0% accurate)
   Progress: 100/700 (81.0% accurate)
   ...

🎯 BENCHMARK RESULTS
==============================
Dataset: consolidated
Total claims: 700
Correct: 595
Errors: 3
Accuracy: 85.0%
Total time: 92.3 minutes
Avg per claim: 7.9 seconds

📄 Results saved to: benchmarks/results/results_consolidated_20240628_143012.txt
```

## Performance Estimates

### Processing Time
- **Quick Test (5 claims)**: ~30-60 seconds
- **Validation Split (105 claims)**: ~20-30 minutes  
- **Test Split (106 claims)**: ~20-30 minutes
- **Full Consolidated (700 claims)**: ~1.5-3 hours

### Cost Estimates (GPT-4)
- **Quick Test**: ~$2-5
- **Validation/Test Split**: ~$50-100
- **Full Consolidated**: ~$350-700

## Integration with Development

### Continuous Integration
```bash
# Add to CI pipeline
make process-datasets  # One-time setup
make quick-benchmark   # Fast validation
```

### A/B Testing Different Prompts
```bash
# Test baseline prompts
make benchmark-val

# Update prompts, then test again
make benchmark-val

# Compare accuracy results
```

## Tips

1. **Start Small**: Always use `make quick-benchmark` before running full benchmarks
2. **Use Splits**: Test on validation split during development, save test split for final evaluation
3. **Monitor Costs**: Keep track of API usage during full benchmarks
4. **Save Results**: Results are automatically saved to `benchmarks/results/`
5. **Check Progress**: Benchmark runner shows progress every 50 claims 