#!/usr/bin/env python3

import json
from calculate_reimbursement import calculate_reimbursement

def analyze_exact_match_potential():
    """Analyze the closest cases to understand what makes them work"""
    
    with open('public_cases.json', 'r') as f:
        data = json.load(f)
    
    # Find the closest cases
    closest_cases = []
    for i, case in enumerate(data):
        duration = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        expected = case['expected_output']
        
        predicted = calculate_reimbursement(duration, miles, receipts)
        error = abs(predicted - expected)
        
        closest_cases.append({
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
            'ratio_diff': (predicted - expected) / expected if expected > 0 else 0
        })
    
    # Sort by error (closest first)
    closest_cases.sort(key=lambda x: x['error'])
    
    print("🎯 EXACT MATCH POTENTIAL ANALYSIS")
    print("=" * 60)
    
    # Analyze the top 20 closest cases
    top_20 = closest_cases[:20]
    
    print(f"Top 20 Closest Cases (potential for exact matches):")
    print("-" * 60)
    
    for i, case in enumerate(top_20):
        print(f"{i+1:2d}. Case {case['case_id']:3d}: {case['duration']}d, {case['miles']:4.0f}mi, ${case['receipts']:7.2f}")
        print(f"    Expected: ${case['expected']:7.2f} | Predicted: ${case['predicted']:7.2f} | Error: ${case['error']:6.2f}")
        print(f"    Per-day: ${case['expected_per_day']:6.2f} vs ${case['predicted_per_day']:6.2f}")
        print(f"    Ratio diff: {case['ratio_diff']:+.3f}")
        print()
    
    # Pattern analysis for closest cases
    print("\n📊 PATTERN ANALYSIS FOR CLOSEST CASES")
    print("-" * 60)
    
    # Duration patterns
    duration_groups = {}
    for case in top_20:
        duration = case['duration']
        if duration not in duration_groups:
            duration_groups[duration] = []
        duration_groups[duration].append(case)
    
    print("Duration patterns in closest cases:")
    for duration in sorted(duration_groups.keys()):
        cases = duration_groups[duration]
        avg_error = sum(c['error'] for c in cases) / len(cases)
        print(f"  {duration} days: {len(cases)} cases, avg error ${avg_error:.2f}")
    
    # Efficiency patterns
    print(f"\nEfficiency patterns in closest cases:")
    efficiency_ranges = [
        (0, 100, "Low (<100 mi/day)"),
        (100, 200, "Medium (100-200 mi/day)"),
        (200, 300, "High (200-300 mi/day)"),
        (300, float('inf'), "Very High (>300 mi/day)")
    ]
    
    for min_e, max_e, label in efficiency_ranges:
        range_cases = [c for c in top_20 if min_e <= c['miles_per_day'] < max_e]
        if range_cases:
            avg_error = sum(c['error'] for c in range_cases) / len(range_cases)
            print(f"  {label}: {len(range_cases)} cases, avg error ${avg_error:.2f}")
    
    # Receipt patterns
    print(f"\nReceipt patterns in closest cases:")
    receipt_ranges = [
        (0, 100, "$0-100"),
        (100, 500, "$100-500"),
        (500, 1000, "$500-1K"),
        (1000, 2000, "$1K-2K"),
        (2000, float('inf'), "$2K+")
    ]
    
    for min_r, max_r, label in receipt_ranges:
        range_cases = [c for c in top_20 if min_r <= c['receipts'] < max_r]
        if range_cases:
            avg_error = sum(c['error'] for c in range_cases) / len(range_cases)
            print(f"  {label}: {len(range_cases)} cases, avg error ${avg_error:.2f}")
    
    return top_20

def reverse_engineer_closest_cases():
    """Try to reverse engineer the exact formulas for the closest cases"""
    
    with open('public_cases.json', 'r') as f:
        data = json.load(f)
    
    # Get the 5 closest cases
    closest_cases = []
    for i, case in enumerate(data):
        duration = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        expected = case['expected_output']
        
        predicted = calculate_reimbursement(duration, miles, receipts)
        error = abs(predicted - expected)
        
        closest_cases.append({
            'case_id': i + 1,
            'duration': duration,
            'miles': miles,
            'receipts': receipts,
            'expected': expected,
            'predicted': predicted,
            'error': error
        })
    
    closest_cases.sort(key=lambda x: x['error'])
    top_5 = closest_cases[:5]
    
    print("\n🔬 REVERSE ENGINEERING CLOSEST CASES")
    print("=" * 60)
    
    for case in top_5:
        print(f"\nCase {case['case_id']}: {case['duration']}d, {case['miles']}mi, ${case['receipts']:.2f}")
        print(f"Expected: ${case['expected']:.2f} | Our prediction: ${case['predicted']:.2f}")
        print(f"Error: ${case['error']:.2f}")
        
        # Try to work backwards from expected result
        duration = case['duration']
        miles = case['miles']
        receipts = case['receipts']
        expected = case['expected']
        
        # What would the per-day rate need to be?
        implied_per_day = expected / duration
        print(f"Implied per-day rate: ${implied_per_day:.2f}")
        
        # What's the mileage component?
        if miles <= 500:
            mileage_component = miles * 0.65
        elif miles <= 1000:
            mileage_component = 500 * 0.65 + (miles - 500) * 0.45
        else:
            mileage_component = 500 * 0.65 + 500 * 0.45 + (miles - 1000) * 0.25
        
        print(f"Mileage component: ${mileage_component:.2f}")
        
        # What's the receipt component?
        if receipts <= 200:
            receipt_component = receipts * 0.8
        elif receipts <= 500:
            receipt_component = 200 * 0.8 + (receipts - 200) * 0.6
        else:
            receipt_component = 200 * 0.8 + 300 * 0.6 + (receipts - 500) * 0.4
        
        print(f"Receipt component: ${receipt_component:.2f}")
        
        # What would the base component need to be?
        implied_base = expected - mileage_component - receipt_component
        implied_base_per_day = implied_base / duration
        
        print(f"Implied base component: ${implied_base:.2f} (${implied_base_per_day:.2f}/day)")
        
        # Check if this matches any pattern
        miles_per_day = miles / duration
        receipts_per_day = receipts / duration
        
        print(f"Efficiency: {miles_per_day:.1f} mi/day, ${receipts_per_day:.2f}/day")
        
        # Look for special patterns
        if 180 <= miles_per_day <= 220:
            print("  ✅ In Kevin's efficiency sweet spot (180-220 mi/day)")
        
        if duration == 5:
            print("  ✅ 5-day trip (potential bonus)")
        
        if receipts_per_day < 50:
            print("  ⚠️ Low spending per day")
        
        if receipts_per_day > 300:
            print("  ⚠️ High spending per day")

def find_mathematical_patterns():
    """Look for mathematical relationships in the data"""
    
    with open('public_cases.json', 'r') as f:
        data = json.load(f)
    
    print("\n🧮 MATHEMATICAL PATTERN ANALYSIS")
    print("=" * 60)
    
    # Look for cases where our prediction is very close
    close_cases = []
    for case in data:
        duration = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        expected = case['expected_output']
        
        predicted = calculate_reimbursement(duration, miles, receipts)
        error = abs(predicted - expected)
        
        if error < 5.0:  # Within $5
            close_cases.append({
                'duration': duration,
                'miles': miles,
                'receipts': receipts,
                'expected': expected,
                'predicted': predicted,
                'error': error
            })
    
    print(f"Found {len(close_cases)} cases within $5.00 error")
    
    if close_cases:
        # Look for common ratios
        ratios = [case['predicted'] / case['expected'] for case in close_cases if case['expected'] > 0]
        avg_ratio = sum(ratios) / len(ratios)
        print(f"Average prediction ratio: {avg_ratio:.3f}")
        
        # Look for rounding patterns
        print(f"\nRounding analysis:")
        for case in close_cases[:5]:
            expected = case['expected']
            predicted = case['predicted']
            
            # Check if expected has specific decimal patterns
            decimal_part = expected - int(expected)
            print(f"Expected: ${expected:.2f} (decimal: {decimal_part:.2f})")
            
            # Check for common endings
            if str(expected).endswith('.00'):
                print("  ✅ Ends in .00")
            elif str(expected).endswith('.50'):
                print("  ✅ Ends in .50")

if __name__ == "__main__":
    closest_cases = analyze_exact_match_potential()
    reverse_engineer_closest_cases()
    find_mathematical_patterns() 