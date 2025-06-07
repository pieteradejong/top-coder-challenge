#!/usr/bin/env python3

import json
import time
import argparse
from calculate_reimbursement import calculate_reimbursement

def quick_test(cases_to_test=10):
    """Quick test on a subset of cases for rapid iteration"""
    
    with open('public_cases.json', 'r') as f:
        data = json.load(f)
    
    # Take a representative sample
    import random
    random.seed(42)  # Reproducible results
    sample = random.sample(data, min(cases_to_test, len(data)))
    
    print(f"🚀 Quick Test - {len(sample)} cases")
    print("-" * 40)
    
    total_error = 0
    close_matches = 0
    
    for i, case in enumerate(sample):
        duration = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        expected = case['expected_output']
        
        predicted = calculate_reimbursement(duration, miles, receipts)
        error = abs(predicted - expected)
        
        total_error += error
        if error < 1.0:
            close_matches += 1
        
        status = "✅" if error < 1.0 else "❌"
        print(f"{status} Case {i+1}: {duration}d, {miles}mi, ${receipts:.2f} -> "
              f"Expected: ${expected:.2f}, Got: ${predicted:.2f}, Error: ${error:.2f}")
    
    avg_error = total_error / len(sample)
    success_rate = (close_matches / len(sample)) * 100
    
    print("-" * 40)
    print(f"📊 Quick Results:")
    print(f"  Average Error: ${avg_error:.2f}")
    print(f"  Close Matches: {close_matches}/{len(sample)} ({success_rate:.1f}%)")
    print(f"  Estimated Full Score: {avg_error * 100:.0f}")
    
    return avg_error, success_rate

def benchmark_algorithm():
    """Benchmark the algorithm performance"""
    
    print("⏱️  Benchmarking algorithm performance...")
    
    # Test different input sizes
    test_sizes = [10, 100, 1000]
    
    with open('public_cases.json', 'r') as f:
        data = json.load(f)
    
    for size in test_sizes:
        if size > len(data):
            continue
            
        test_data = data[:size]
        
        start_time = time.time()
        
        for case in test_data:
            duration = case['input']['trip_duration_days']
            miles = case['input']['miles_traveled']
            receipts = case['input']['total_receipts_amount']
            calculate_reimbursement(duration, miles, receipts)
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        cases_per_sec = size / elapsed if elapsed > 0 else float('inf')
        
        print(f"  {size:4d} cases: {elapsed:.4f}s ({cases_per_sec:.0f} cases/sec)")

def analyze_specific_case(case_id):
    """Analyze a specific test case in detail"""
    
    with open('public_cases.json', 'r') as f:
        data = json.load(f)
    
    if case_id < 1 or case_id > len(data):
        print(f"❌ Invalid case ID. Must be between 1 and {len(data)}")
        return
    
    case = data[case_id - 1]
    duration = case['input']['trip_duration_days']
    miles = case['input']['miles_traveled']
    receipts = case['input']['total_receipts_amount']
    expected = case['expected_output']
    
    print(f"🔍 Analyzing Case {case_id}")
    print("=" * 50)
    print(f"Inputs:")
    print(f"  Trip Duration: {duration} days")
    print(f"  Miles Traveled: {miles}")
    print(f"  Receipt Amount: ${receipts:.2f}")
    print(f"  Receipts per day: ${receipts/duration:.2f}")
    print(f"  Miles per day: {miles/duration:.1f}")
    print()
    
    # Step through algorithm
    print("Algorithm Breakdown:")
    
    # Base calculation
    if duration == 1:
        base_per_day = 120
    elif duration == 2:
        base_per_day = 105
    elif duration <= 5:
        base_per_day = 100
    else:
        base_per_day = 95
    
    base_amount = base_per_day * duration
    print(f"  Base amount: ${base_per_day}/day × {duration} days = ${base_amount:.2f}")
    
    # Mileage calculation
    if miles <= 500:
        mileage_amount = miles * 0.65
        print(f"  Mileage: {miles} miles × $0.65 = ${mileage_amount:.2f}")
    elif miles <= 1000:
        mileage_amount = 500 * 0.65 + (miles - 500) * 0.45
        print(f"  Mileage: 500×$0.65 + {miles-500}×$0.45 = ${mileage_amount:.2f}")
    else:
        mileage_amount = 500 * 0.65 + 500 * 0.45 + (miles - 1000) * 0.25
        print(f"  Mileage: 500×$0.65 + 500×$0.45 + {miles-1000}×$0.25 = ${mileage_amount:.2f}")
    
    # Receipt calculation
    if receipts <= 200:
        receipt_amount = receipts * 0.8
        print(f"  Receipts: ${receipts:.2f} × 0.8 = ${receipt_amount:.2f}")
    elif receipts <= 500:
        receipt_amount = 200 * 0.8 + (receipts - 200) * 0.6
        print(f"  Receipts: $200×0.8 + ${receipts-200:.2f}×0.6 = ${receipt_amount:.2f}")
    else:
        receipt_amount = 200 * 0.8 + 300 * 0.6 + (receipts - 500) * 0.4
        print(f"  Receipts: $200×0.8 + $300×0.6 + ${receipts-500:.2f}×0.4 = ${receipt_amount:.2f}")
    
    subtotal = base_amount + mileage_amount + receipt_amount
    print(f"  Subtotal: ${base_amount:.2f} + ${mileage_amount:.2f} + ${receipt_amount:.2f} = ${subtotal:.2f}")
    
    # Caps
    caps = {1: 1475, 2: 1667, 3: 1588, 4: 1700, 5: 1811}
    if duration <= 5:
        cap = caps[duration]
    else:
        cap = 1811 + (duration - 5) * 100
    
    after_cap = min(subtotal, cap)
    if after_cap < subtotal:
        print(f"  Cap applied: ${subtotal:.2f} → ${after_cap:.2f} (cap: ${cap:.2f})")
    else:
        print(f"  No cap applied (cap: ${cap:.2f})")
    
    # Penalties
    final_amount = after_cap
    receipts_per_day = receipts / duration
    
    penalty_applied = False
    
    if (duration == 4 and receipts > 2300 and miles < 100):
        final_amount *= 0.2
        penalty_applied = True
        print(f"  Penalty: 4-day + high receipts + low miles: ×0.2 = ${final_amount:.2f}")
    elif (duration == 1 and miles > 1000 and receipts > 1500):
        final_amount *= 0.3
        penalty_applied = True
        print(f"  Penalty: 1-day + high miles + high receipts: ×0.3 = ${final_amount:.2f}")
    elif (duration <= 2 and receipts > 2400):
        final_amount *= 0.6
        penalty_applied = True
        print(f"  Penalty: Short trip + very high receipts: ×0.6 = ${final_amount:.2f}")
    
    if receipts_per_day < 10 and miles < 100:
        final_amount *= 0.8
        penalty_applied = True
        print(f"  Penalty: Low spending + low miles: ×0.8 = ${final_amount:.2f}")
    
    if duration >= 8:
        final_amount *= 0.9
        penalty_applied = True
        print(f"  Penalty: Long trip (vacation): ×0.9 = ${final_amount:.2f}")
    
    if not penalty_applied:
        print(f"  No penalties applied")
    
    predicted = round(final_amount, 2)
    error = abs(predicted - expected)
    
    print()
    print("Results:")
    print(f"  Expected: ${expected:.2f}")
    print(f"  Predicted: ${predicted:.2f}")
    print(f"  Error: ${error:.2f}")
    print(f"  Status: {'✅ GOOD' if error < 1.0 else '❌ NEEDS WORK'}")

def compare_algorithms():
    """Compare different algorithm variations"""
    
    print("🔄 Comparing algorithm variations...")
    print("(This would test different parameter sets)")
    
    # This could test different base rates, mileage rates, etc.
    # For now, just show the concept
    
    variations = [
        {"name": "Current", "base_1day": 120, "mileage_rate1": 0.65},
        {"name": "Higher Base", "base_1day": 130, "mileage_rate1": 0.65},
        {"name": "Lower Mileage", "base_1day": 120, "mileage_rate1": 0.60},
    ]
    
    print("Variation comparison would go here...")
    print("This could test different parameter combinations quickly")

def main():
    """Main CLI interface"""
    
    parser = argparse.ArgumentParser(description='Development tools for reimbursement algorithm')
    parser.add_argument('command', choices=['quick', 'benchmark', 'analyze', 'compare', 'viz'],
                       help='Command to run')
    parser.add_argument('--cases', type=int, default=10, 
                       help='Number of cases for quick test (default: 10)')
    parser.add_argument('--case-id', type=int, 
                       help='Specific case ID to analyze')
    
    args = parser.parse_args()
    
    if args.command == 'quick':
        quick_test(args.cases)
    elif args.command == 'benchmark':
        benchmark_algorithm()
    elif args.command == 'analyze':
        if args.case_id:
            analyze_specific_case(args.case_id)
        else:
            print("❌ Please specify --case-id for analyze command")
    elif args.command == 'compare':
        compare_algorithms()
    elif args.command == 'viz':
        print("🎨 Starting visualization...")
        try:
            from visualize_analysis import main as viz_main
            viz_main()
        except ImportError:
            print("❌ Visualization requires matplotlib and seaborn")
            print("Install with: pip install matplotlib seaborn")

if __name__ == "__main__":
    main() 