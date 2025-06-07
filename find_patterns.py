#!/usr/bin/env python3

import json

def load_data():
    """Load the public test cases"""
    with open('public_cases.json', 'r') as f:
        data = json.load(f)
    return data

def find_high_mileage_one_day_trips(data):
    """Find 1-day trips with high mileage to understand caps"""
    print("=== HIGH MILEAGE 1-DAY TRIPS ===")
    
    one_day_trips = []
    for case in data:
        inp = case['input']
        out = case['expected_output']
        
        if inp['trip_duration_days'] == 1:
            one_day_trips.append({
                'miles': inp['miles_traveled'],
                'receipts': inp['total_receipts_amount'],
                'output': out
            })
    
    # Sort by mileage
    one_day_trips.sort(key=lambda x: x['miles'])
    
    print("1-day trips sorted by mileage:")
    for trip in one_day_trips:
        if trip['miles'] > 500:  # Focus on high mileage
            print(f"  {trip['miles']:4.0f} miles, ${trip['receipts']:7.2f} receipts -> ${trip['output']:7.2f}")

def find_receipt_caps(data):
    """Find evidence of receipt caps"""
    print("\n=== HIGH RECEIPT CASES ===")
    
    high_receipt_cases = []
    for case in data:
        inp = case['input']
        out = case['expected_output']
        
        if inp['total_receipts_amount'] > 1500:
            high_receipt_cases.append({
                'days': inp['trip_duration_days'],
                'miles': inp['miles_traveled'],
                'receipts': inp['total_receipts_amount'],
                'output': out,
                'per_day': out / inp['trip_duration_days']
            })
    
    # Sort by receipts
    high_receipt_cases.sort(key=lambda x: x['receipts'])
    
    print("High receipt cases:")
    for case in high_receipt_cases[-20:]:  # Show highest 20
        print(f"  {case['days']}d, {case['miles']:3.0f}mi, ${case['receipts']:7.2f}r -> ${case['output']:7.2f} (${case['per_day']:6.2f}/d)")

def analyze_outliers(data):
    """Find cases with unusually low reimbursements"""
    print("\n=== LOW REIMBURSEMENT OUTLIERS ===")
    
    cases_with_ratios = []
    for case in data:
        inp = case['input']
        out = case['expected_output']
        
        # Calculate a simple expected value: days*100 + miles*0.5 + receipts*0.5
        simple_expected = inp['trip_duration_days'] * 100 + inp['miles_traveled'] * 0.5 + inp['total_receipts_amount'] * 0.5
        ratio = out / simple_expected if simple_expected > 0 else 0
        
        cases_with_ratios.append({
            'days': inp['trip_duration_days'],
            'miles': inp['miles_traveled'],
            'receipts': inp['total_receipts_amount'],
            'output': out,
            'simple_expected': simple_expected,
            'ratio': ratio
        })
    
    # Sort by ratio (lowest first)
    cases_with_ratios.sort(key=lambda x: x['ratio'])
    
    print("Cases with lowest actual/expected ratios (potential caps):")
    for case in cases_with_ratios[:20]:
        print(f"  {case['days']}d, {case['miles']:3.0f}mi, ${case['receipts']:7.2f}r -> ${case['output']:7.2f} (ratio: {case['ratio']:.3f})")

def main():
    """Main analysis function"""
    print("Loading data...")
    data = load_data()
    
    find_high_mileage_one_day_trips(data)
    find_receipt_caps(data)
    analyze_outliers(data)
    
    print("\nPattern analysis complete!")

if __name__ == "__main__":
    main() 