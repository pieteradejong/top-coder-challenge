#!/usr/bin/env python3

import json
import statistics

def load_data():
    """Load the public test cases"""
    with open('public_cases.json', 'r') as f:
        data = json.load(f)
    return data

def analyze_simple_linear_model(data):
    """Try to find a simple linear relationship"""
    print("=== SIMPLE LINEAR MODEL ANALYSIS ===")
    
    # Let's try to find coefficients for: reimbursement = a*days + b*miles + c*receipts + d
    
    # Look at some specific patterns
    cases_by_pattern = {
        'low_receipts_low_miles': [],
        'low_receipts_high_miles': [],
        'high_receipts_low_miles': [],
        'high_receipts_high_miles': []
    }
    
    for case in data:
        inp = case['input']
        out = case['expected_output']
        
        days = inp['trip_duration_days']
        miles = inp['miles_traveled']
        receipts = inp['total_receipts_amount']
        
        if receipts < 100 and miles < 200:
            cases_by_pattern['low_receipts_low_miles'].append((days, miles, receipts, out))
        elif receipts < 100 and miles >= 200:
            cases_by_pattern['low_receipts_high_miles'].append((days, miles, receipts, out))
        elif receipts >= 100 and miles < 200:
            cases_by_pattern['high_receipts_low_miles'].append((days, miles, receipts, out))
        else:
            cases_by_pattern['high_receipts_high_miles'].append((days, miles, receipts, out))
    
    for pattern_name, cases in cases_by_pattern.items():
        if cases:
            print(f"\n{pattern_name}: {len(cases)} cases")
            for i, (days, miles, receipts, out) in enumerate(cases[:10]):
                per_day = out / days
                print(f"  {days}d, {miles:3.0f}mi, ${receipts:6.2f}r -> ${out:7.2f} (${per_day:6.2f}/d)")

def analyze_per_mile_rates(data):
    """Analyze what the actual per-mile rates might be"""
    print("\n=== PER-MILE RATE ANALYSIS ===")
    
    # Look at cases with minimal receipts to isolate mileage effects
    low_receipt_cases = []
    for case in data:
        inp = case['input']
        out = case['expected_output']
        
        if inp['total_receipts_amount'] < 50:
            low_receipt_cases.append({
                'days': inp['trip_duration_days'],
                'miles': inp['miles_traveled'],
                'receipts': inp['total_receipts_amount'],
                'output': out,
                'per_day': out / inp['trip_duration_days']
            })
    
    # Sort by miles to see patterns
    low_receipt_cases.sort(key=lambda x: x['miles'])
    
    print("Low receipt cases (to isolate mileage patterns):")
    for case in low_receipt_cases:
        # Try to estimate base per diem and mileage component
        estimated_base = case['days'] * 100  # Assume $100/day base
        mileage_component = case['output'] - estimated_base
        if case['miles'] > 0:
            implied_rate = mileage_component / case['miles']
            print(f"  {case['days']}d, {case['miles']:3.0f}mi, ${case['receipts']:5.2f}r -> ${case['output']:6.2f} | Est rate: ${implied_rate:.3f}/mi")

def analyze_receipt_patterns(data):
    """Analyze receipt reimbursement patterns"""
    print("\n=== RECEIPT PATTERN ANALYSIS ===")
    
    # Look at cases with minimal mileage to isolate receipt effects
    low_mileage_cases = []
    for case in data:
        inp = case['input']
        out = case['expected_output']
        
        if inp['miles_traveled'] < 50:
            low_mileage_cases.append({
                'days': inp['trip_duration_days'],
                'miles': inp['miles_traveled'],
                'receipts': inp['total_receipts_amount'],
                'output': out,
                'per_day': out / inp['trip_duration_days']
            })
    
    # Sort by receipts to see patterns
    low_mileage_cases.sort(key=lambda x: x['receipts'])
    
    print("Low mileage cases (to isolate receipt patterns):")
    for case in low_mileage_cases:
        # Try to estimate base per diem and receipt component
        estimated_base = case['days'] * 100  # Assume $100/day base
        estimated_mileage = case['miles'] * 0.5  # Assume $0.50/mile
        receipt_component = case['output'] - estimated_base - estimated_mileage
        if case['receipts'] > 0:
            implied_rate = receipt_component / case['receipts']
            print(f"  {case['days']}d, {case['miles']:2.0f}mi, ${case['receipts']:7.2f}r -> ${case['output']:7.2f} | Est rate: {implied_rate:.3f}")

def find_actual_base_rate(data):
    """Try to find the actual base per-day rate"""
    print("\n=== BASE RATE ANALYSIS ===")
    
    # Look for cases with minimal miles and receipts
    minimal_cases = []
    for case in data:
        inp = case['input']
        out = case['expected_output']
        
        if inp['miles_traveled'] < 25 and inp['total_receipts_amount'] < 25:
            minimal_cases.append({
                'days': inp['trip_duration_days'],
                'miles': inp['miles_traveled'],
                'receipts': inp['total_receipts_amount'],
                'output': out,
                'per_day': out / inp['trip_duration_days']
            })
    
    print("Minimal cases (low miles and receipts):")
    for case in minimal_cases:
        print(f"  {case['days']}d, {case['miles']:2.0f}mi, ${case['receipts']:5.2f}r -> ${case['output']:6.2f} (${case['per_day']:6.2f}/d)")
    
    if minimal_cases:
        avg_per_day = statistics.mean([case['per_day'] for case in minimal_cases])
        print(f"\nAverage per-day rate for minimal cases: ${avg_per_day:.2f}")

def analyze_specific_examples(data):
    """Analyze specific examples to understand the formula"""
    print("\n=== SPECIFIC EXAMPLE ANALYSIS ===")
    
    # Let's look at the first few cases in detail
    print("First 10 cases with detailed breakdown:")
    for i, case in enumerate(data[:10]):
        inp = case['input']
        out = case['expected_output']
        
        days = inp['trip_duration_days']
        miles = inp['miles_traveled']
        receipts = inp['total_receipts_amount']
        
        print(f"\nCase {i+1}: {days}d, {miles}mi, ${receipts:.2f}r -> ${out:.2f}")
        print(f"  Per day: ${out/days:.2f}")
        print(f"  Miles per day: {miles/days:.1f}")
        
        # Try different decompositions
        if miles > 0:
            # If we assume $100/day base + $0.50/mile + some receipt component
            base_100 = days * 100
            mileage_50c = miles * 0.50
            receipt_component = out - base_100 - mileage_50c
            print(f"  Decomposition 1: ${base_100} base + ${mileage_50c:.2f} mileage + ${receipt_component:.2f} receipts")
            
            # If we assume different base rates
            base_80 = days * 80
            mileage_component = out - base_80
            if receipts > 0:
                remaining_after_receipts = mileage_component - receipts * 0.5
                implied_mile_rate = remaining_after_receipts / miles if miles > 0 else 0
                print(f"  Decomposition 2: ${base_80} base + ${receipts * 0.5:.2f} receipts + ${remaining_after_receipts:.2f} mileage (${implied_mile_rate:.3f}/mi)")

def main():
    """Main analysis function"""
    print("Loading data...")
    data = load_data()
    
    analyze_simple_linear_model(data)
    analyze_per_mile_rates(data)
    analyze_receipt_patterns(data)
    find_actual_base_rate(data)
    analyze_specific_examples(data)
    
    print("\nBetter analysis complete!")

if __name__ == "__main__":
    main() 