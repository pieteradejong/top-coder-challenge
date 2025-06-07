#!/usr/bin/env python3

import json
import numpy as np
from collections import defaultdict

def analyze_inverse_relationship():
    """Analyze the inverse relationship between trip duration and per-day rates"""
    
    with open('public_cases.json', 'r') as f:
        data = json.load(f)
    
    # Group by trip duration
    by_duration = defaultdict(list)
    
    for case in data:
        duration = case['input']['trip_duration_days']
        reimbursement = case['expected_output']
        per_day_rate = reimbursement / duration
        
        by_duration[duration].append({
            'per_day_rate': per_day_rate,
            'miles': case['input']['miles_traveled'],
            'receipts': case['input']['total_receipts_amount'],
            'reimbursement': reimbursement,
            'miles_per_day': case['input']['miles_traveled'] / duration,
            'receipts_per_day': case['input']['total_receipts_amount'] / duration
        })
    
    print("=== INVERSE RELATIONSHIP ANALYSIS ===")
    print()
    
    # Calculate statistics for each duration
    duration_stats = {}
    for duration in sorted(by_duration.keys()):
        cases = by_duration[duration]
        per_day_rates = [c['per_day_rate'] for c in cases]
        
        stats = {
            'count': len(cases),
            'mean': np.mean(per_day_rates),
            'median': np.median(per_day_rates),
            'std': np.std(per_day_rates),
            'min': np.min(per_day_rates),
            'max': np.max(per_day_rates),
            'q25': np.percentile(per_day_rates, 25),
            'q75': np.percentile(per_day_rates, 75)
        }
        
        duration_stats[duration] = stats
        
        print(f"Duration {duration} days ({stats['count']} cases):")
        print(f"  Mean per-day rate: ${stats['mean']:.2f}")
        print(f"  Median per-day rate: ${stats['median']:.2f}")
        print(f"  Range: ${stats['min']:.2f} - ${stats['max']:.2f}")
        print(f"  Q25-Q75: ${stats['q25']:.2f} - ${stats['q75']:.2f}")
        print()
    
    # Try to fit a mathematical model
    print("=== MATHEMATICAL MODEL FITTING ===")
    print()
    
    durations = sorted(duration_stats.keys())
    mean_rates = [duration_stats[d]['mean'] for d in durations]
    
    # Try different models
    print("Duration -> Mean Per-Day Rate:")
    for i, duration in enumerate(durations):
        print(f"  {duration} days -> ${mean_rates[i]:.2f}/day")
    
    print()
    
    # Try inverse relationship: rate = a / duration + b
    # Using least squares to fit
    X = np.array([[1/d, 1] for d in durations])
    y = np.array(mean_rates)
    
    try:
        coeffs = np.linalg.lstsq(X, y, rcond=None)[0]
        a, b = coeffs
        
        print(f"Inverse model: rate = {a:.2f} / duration + {b:.2f}")
        print("Predictions vs Actual:")
        for duration in durations:
            predicted = a / duration + b
            actual = duration_stats[duration]['mean']
            error = abs(predicted - actual)
            print(f"  {duration} days: Predicted ${predicted:.2f}, Actual ${actual:.2f}, Error ${error:.2f}")
        
        print()
        
        # Calculate R-squared
        y_pred = X @ coeffs
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot)
        print(f"R-squared: {r_squared:.4f}")
        
    except Exception as e:
        print(f"Error fitting inverse model: {e}")
    
    print()
    
    # Analyze patterns within each duration
    print("=== PATTERNS WITHIN EACH DURATION ===")
    print()
    
    for duration in [1, 2, 3, 4, 5]:
        if duration not in by_duration:
            continue
            
        cases = by_duration[duration]
        print(f"Duration {duration} days - Pattern Analysis:")
        
        # Look at extreme cases
        sorted_cases = sorted(cases, key=lambda x: x['per_day_rate'])
        
        print(f"  Lowest per-day rates:")
        for case in sorted_cases[:3]:
            print(f"    ${case['per_day_rate']:.2f}/day: {case['miles']} miles, ${case['receipts']:.2f} receipts, ${case['reimbursement']:.2f} total")
        
        print(f"  Highest per-day rates:")
        for case in sorted_cases[-3:]:
            print(f"    ${case['per_day_rate']:.2f}/day: {case['miles']} miles, ${case['receipts']:.2f} receipts, ${case['reimbursement']:.2f} total")
        
        print()
    
    # Look for 5-day bonus pattern
    print("=== 5-DAY BONUS ANALYSIS ===")
    print()
    
    if 5 in by_duration:
        five_day_cases = by_duration[5]
        
        # Compare 5-day cases to 4-day and 6-day
        four_day_mean = duration_stats.get(4, {}).get('mean', 0)
        five_day_mean = duration_stats[5]['mean']
        six_day_mean = duration_stats.get(6, {}).get('mean', 0)
        
        print(f"4-day mean: ${four_day_mean:.2f}/day")
        print(f"5-day mean: ${five_day_mean:.2f}/day")
        print(f"6-day mean: ${six_day_mean:.2f}/day")
        
        # Check if 5-day is higher than expected from inverse trend
        if four_day_mean > 0 and six_day_mean > 0:
            expected_five_day = (four_day_mean + six_day_mean) / 2
            bonus = five_day_mean - expected_five_day
            print(f"Expected 5-day (interpolated): ${expected_five_day:.2f}/day")
            print(f"Actual 5-day: ${five_day_mean:.2f}/day")
            print(f"Potential bonus: ${bonus:.2f}/day")
        
        print()
    
    return duration_stats

if __name__ == "__main__":
    analyze_inverse_relationship() 