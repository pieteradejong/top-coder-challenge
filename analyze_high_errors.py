#!/usr/bin/env python3

import json
from calculate_reimbursement import calculate_reimbursement

def analyze_high_error_cases():
    """Analyze the highest error cases to understand missing patterns"""
    
    with open('public_cases.json', 'r') as f:
        data = json.load(f)
    
    # Calculate errors for all cases
    cases_with_errors = []
    for i, case in enumerate(data):
        duration = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        expected = case['expected_output']
        
        predicted = calculate_reimbursement(duration, miles, receipts)
        error = abs(predicted - expected)
        
        cases_with_errors.append({
            'case_id': i + 1,
            'duration': duration,
            'miles': miles,
            'receipts': receipts,
            'expected': expected,
            'predicted': predicted,
            'error': error,
            'miles_per_day': miles / duration,
            'receipts_per_day': receipts / duration,
            'expected_per_day': expected / duration,
            'predicted_per_day': predicted / duration,
            'receipt_ratio': expected / receipts if receipts > 0 else 0,
            'over_under': 'OVER' if predicted > expected else 'UNDER'
        })
    
    # Sort by error
    cases_with_errors.sort(key=lambda x: x['error'], reverse=True)
    
    print("🔍 HIGH-ERROR CASE ANALYSIS")
    print("=" * 60)
    
    # Analyze top 20 error cases
    top_errors = cases_with_errors[:20]
    
    print(f"\nTop 20 Highest Error Cases:")
    print("-" * 60)
    for i, case in enumerate(top_errors):
        print(f"{i+1:2d}. Case {case['case_id']:3d}: {case['duration']}d, {case['miles']:4.0f}mi, ${case['receipts']:7.2f}")
        print(f"    Expected: ${case['expected']:7.2f} | Predicted: ${case['predicted']:7.2f} | Error: ${case['error']:7.2f} ({case['over_under']})")
        print(f"    Per-day: ${case['expected_per_day']:6.2f} vs ${case['predicted_per_day']:6.2f} | Ratio: {case['receipt_ratio']:.3f}")
        print()
    
    # Pattern analysis
    print("\n📊 PATTERN ANALYSIS")
    print("-" * 60)
    
    # Over vs Under predictions
    over_predictions = [c for c in top_errors if c['over_under'] == 'OVER']
    under_predictions = [c for c in top_errors if c['over_under'] == 'UNDER']
    
    print(f"Over-predictions: {len(over_predictions)}")
    print(f"Under-predictions: {len(under_predictions)}")
    
    # Duration patterns
    duration_errors = {}
    for case in top_errors:
        duration = case['duration']
        if duration not in duration_errors:
            duration_errors[duration] = []
        duration_errors[duration].append(case)
    
    print(f"\nError patterns by duration:")
    for duration in sorted(duration_errors.keys()):
        cases = duration_errors[duration]
        avg_error = sum(c['error'] for c in cases) / len(cases)
        over_count = sum(1 for c in cases if c['over_under'] == 'OVER')
        print(f"  {duration} days: {len(cases)} cases, avg error ${avg_error:.2f}, {over_count}/{len(cases)} over-predictions")
    
    # Receipt range analysis
    print(f"\nReceipt range analysis (top errors):")
    receipt_ranges = [
        (0, 500, "$0-500"),
        (500, 1000, "$500-1K"),
        (1000, 1500, "$1K-1.5K"),
        (1500, 2000, "$1.5K-2K"),
        (2000, 2500, "$2K-2.5K"),
        (2500, float('inf'), "$2.5K+")
    ]
    
    for min_r, max_r, label in receipt_ranges:
        range_cases = [c for c in top_errors if min_r <= c['receipts'] < max_r]
        if range_cases:
            avg_error = sum(c['error'] for c in range_cases) / len(range_cases)
            over_count = sum(1 for c in range_cases if c['over_under'] == 'OVER')
            avg_ratio = sum(c['receipt_ratio'] for c in range_cases) / len(range_cases)
            print(f"  {label}: {len(range_cases)} cases, avg error ${avg_error:.2f}, {over_count}/{len(range_cases)} over, avg ratio {avg_ratio:.3f}")
    
    # Efficiency analysis
    print(f"\nEfficiency analysis (top errors):")
    efficiency_ranges = [
        (0, 100, "Low (<100 mi/day)"),
        (100, 180, "Medium (100-180 mi/day)"),
        (180, 220, "Sweet Spot (180-220 mi/day)"),
        (220, 300, "High (220-300 mi/day)"),
        (300, float('inf'), "Very High (>300 mi/day)")
    ]
    
    for min_e, max_e, label in efficiency_ranges:
        range_cases = [c for c in top_errors if min_e <= c['miles_per_day'] < max_e]
        if range_cases:
            avg_error = sum(c['error'] for c in range_cases) / len(range_cases)
            over_count = sum(1 for c in range_cases if c['over_under'] == 'OVER')
            print(f"  {label}: {len(range_cases)} cases, avg error ${avg_error:.2f}, {over_count}/{len(range_cases)} over")
    
    # Specific problematic patterns
    print(f"\n🚨 SPECIFIC PROBLEMATIC PATTERNS")
    print("-" * 60)
    
    # Long trips with high receipts (over-predicting)
    long_high_receipt = [c for c in top_errors if c['duration'] >= 7 and c['receipts'] > 1500 and c['over_under'] == 'OVER']
    if long_high_receipt:
        print(f"Long trips + high receipts (over-predicting): {len(long_high_receipt)} cases")
        avg_error = sum(c['error'] for c in long_high_receipt) / len(long_high_receipt)
        print(f"  Average error: ${avg_error:.2f}")
        print(f"  Pattern: We're not penalizing long trips with high spending enough")
    
    # Short trips with very high receipts (under-predicting)
    short_very_high_receipt = [c for c in top_errors if c['duration'] <= 4 and c['receipts'] > 2000 and c['over_under'] == 'UNDER']
    if short_very_high_receipt:
        print(f"Short trips + very high receipts (under-predicting): {len(short_very_high_receipt)} cases")
        avg_error = sum(c['error'] for c in short_very_high_receipt) / len(short_very_high_receipt)
        print(f"  Average error: ${avg_error:.2f}")
        print(f"  Pattern: We're over-penalizing some legitimate high-receipt short trips")
    
    # 1-day trips with high mileage (mixed)
    one_day_high_miles = [c for c in top_errors if c['duration'] == 1 and c['miles'] > 800]
    if one_day_high_miles:
        print(f"1-day trips + high mileage: {len(one_day_high_miles)} cases")
        over_count = sum(1 for c in one_day_high_miles if c['over_under'] == 'OVER')
        print(f"  {over_count}/{len(one_day_high_miles)} over-predictions")
        print(f"  Pattern: Inconsistent handling of 1-day high-mileage trips")
    
    return cases_with_errors

def analyze_exact_matches():
    """Analyze cases that are close to exact matches to understand what makes them work"""
    
    with open('public_cases.json', 'r') as f:
        data = json.load(f)
    
    close_cases = []
    for i, case in enumerate(data):
        duration = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        expected = case['expected_output']
        
        predicted = calculate_reimbursement(duration, miles, receipts)
        error = abs(predicted - expected)
        
        if error < 5.0:  # Close cases
            close_cases.append({
                'case_id': i + 1,
                'duration': duration,
                'miles': miles,
                'receipts': receipts,
                'expected': expected,
                'predicted': predicted,
                'error': error,
                'miles_per_day': miles / duration,
                'receipts_per_day': receipts / duration
            })
    
    close_cases.sort(key=lambda x: x['error'])
    
    print(f"\n🎯 CLOSE MATCHES ANALYSIS")
    print("=" * 60)
    print(f"Cases within $5.00 error: {len(close_cases)}")
    
    if close_cases:
        print(f"\nClosest matches:")
        for i, case in enumerate(close_cases[:10]):
            print(f"{i+1:2d}. Case {case['case_id']:3d}: {case['duration']}d, {case['miles']:4.0f}mi, ${case['receipts']:7.2f}")
            print(f"    Expected: ${case['expected']:7.2f} | Predicted: ${case['predicted']:7.2f} | Error: ${case['error']:6.2f}")
        
        # Pattern analysis for close matches
        print(f"\nPatterns in close matches:")
        avg_duration = sum(c['duration'] for c in close_cases) / len(close_cases)
        avg_miles_per_day = sum(c['miles_per_day'] for c in close_cases) / len(close_cases)
        avg_receipts_per_day = sum(c['receipts_per_day'] for c in close_cases) / len(close_cases)
        
        print(f"  Average duration: {avg_duration:.1f} days")
        print(f"  Average miles/day: {avg_miles_per_day:.1f}")
        print(f"  Average receipts/day: ${avg_receipts_per_day:.2f}")

if __name__ == "__main__":
    cases_with_errors = analyze_high_error_cases()
    analyze_exact_matches() 