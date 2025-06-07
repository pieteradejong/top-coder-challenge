#!/usr/bin/env python3

import json
import numpy as np
from collections import defaultdict

def analyze_total_vs_per_day():
    """Analyze whether the inverse relationship applies to total or per-day amounts"""
    
    with open('public_cases.json', 'r') as f:
        data = json.load(f)
    
    # Group by trip duration
    by_duration = defaultdict(list)
    
    for case in data:
        duration = case['input']['trip_duration_days']
        reimbursement = case['expected_output']
        per_day_rate = reimbursement / duration
        
        by_duration[duration].append({
            'total': reimbursement,
            'per_day_rate': per_day_rate,
            'miles': case['input']['miles_traveled'],
            'receipts': case['input']['total_receipts_amount']
        })
    
    print("=== TOTAL VS PER-DAY ANALYSIS ===")
    print()
    
    # Calculate statistics for both total and per-day
    duration_stats = {}
    for duration in sorted(by_duration.keys()):
        cases = by_duration[duration]
        totals = [c['total'] for c in cases]
        per_day_rates = [c['per_day_rate'] for c in cases]
        
        stats = {
            'count': len(cases),
            'total_mean': np.mean(totals),
            'per_day_mean': np.mean(per_day_rates),
            'total_median': np.median(totals),
            'per_day_median': np.median(per_day_rates)
        }
        
        duration_stats[duration] = stats
        
        print(f"Duration {duration} days ({stats['count']} cases):")
        print(f"  Mean total: ${stats['total_mean']:.2f}")
        print(f"  Mean per-day: ${stats['per_day_mean']:.2f}")
        print(f"  Median total: ${stats['total_median']:.2f}")
        print(f"  Median per-day: ${stats['per_day_median']:.2f}")
        print()
    
    # Test both models
    durations = sorted(duration_stats.keys())
    
    print("=== MODEL COMPARISON ===")
    print()
    
    # Model 1: Inverse relationship for TOTAL amounts
    print("Model 1: total = a / duration + b")
    total_means = [duration_stats[d]['total_mean'] for d in durations]
    X = np.array([[1/d, 1] for d in durations])
    y = np.array(total_means)
    
    try:
        coeffs = np.linalg.lstsq(X, y, rcond=None)[0]
        a1, b1 = coeffs
        
        print(f"Formula: total = {a1:.2f} / duration + {b1:.2f}")
        print("Predictions vs Actual (Total):")
        for duration in durations[:5]:  # Show first 5
            predicted = a1 / duration + b1
            actual = duration_stats[duration]['total_mean']
            error = abs(predicted - actual)
            print(f"  {duration} days: Predicted ${predicted:.2f}, Actual ${actual:.2f}, Error ${error:.2f}")
        
        # Calculate R-squared
        y_pred = X @ coeffs
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot)
        print(f"R-squared: {r_squared:.4f}")
        
    except Exception as e:
        print(f"Error fitting total model: {e}")
    
    print()
    
    # Model 2: Inverse relationship for PER-DAY rates (what I used before)
    print("Model 2: per_day_rate = a / duration + b")
    per_day_means = [duration_stats[d]['per_day_mean'] for d in durations]
    y2 = np.array(per_day_means)
    
    try:
        coeffs2 = np.linalg.lstsq(X, y2, rcond=None)[0]
        a2, b2 = coeffs2
        
        print(f"Formula: per_day_rate = {a2:.2f} / duration + {b2:.2f}")
        print("Predictions vs Actual (Per-Day):")
        for duration in durations[:5]:  # Show first 5
            predicted = a2 / duration + b2
            actual = duration_stats[duration]['per_day_mean']
            error = abs(predicted - actual)
            print(f"  {duration} days: Predicted ${predicted:.2f}, Actual ${actual:.2f}, Error ${error:.2f}")
        
        # Calculate R-squared
        y_pred2 = X @ coeffs2
        ss_res2 = np.sum((y2 - y_pred2) ** 2)
        ss_tot2 = np.sum((y2 - np.mean(y2)) ** 2)
        r_squared2 = 1 - (ss_res2 / ss_tot2)
        print(f"R-squared: {r_squared2:.4f}")
        
    except Exception as e:
        print(f"Error fitting per-day model: {e}")
    
    print()
    
    # Test a few specific cases
    print("=== TESTING SPECIFIC CASES ===")
    print()
    
    test_cases = [
        (1, 55, 3.6, 126.06),
        (3, 93, 1.42, 364.51),
        (2, 13, 4.67, 203.52)
    ]
    
    for duration, miles, receipts, expected in test_cases:
        print(f"Case: {duration} days, {miles} miles, ${receipts} receipts -> Expected: ${expected}")
        
        # Model 1 prediction (total)
        if 'a1' in locals() and 'b1' in locals():
            base_total = a1 / duration + b1
            print(f"  Model 1 base (total): ${base_total:.2f}")
        
        # Model 2 prediction (per-day * days)
        if 'a2' in locals() and 'b2' in locals():
            base_per_day = a2 / duration + b2
            base_total_from_per_day = base_per_day * duration
            print(f"  Model 2 base (per-day * days): ${base_total_from_per_day:.2f}")
        
        print()

if __name__ == "__main__":
    analyze_total_vs_per_day() 