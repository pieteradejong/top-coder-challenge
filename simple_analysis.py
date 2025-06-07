#!/usr/bin/env python3

import json
from collections import defaultdict

def load_data():
    """Load the public test cases"""
    with open('public_cases.json', 'r') as f:
        data = json.load(f)
    return data

def analyze_basic_patterns(data):
    """Analyze basic patterns in the data"""
    print("=== BASIC STATISTICS ===")
    print(f"Total cases: {len(data)}")
    
    # Extract values
    durations = [case['input']['trip_duration_days'] for case in data]
    miles = [case['input']['miles_traveled'] for case in data]
    receipts = [case['input']['total_receipts_amount'] for case in data]
    outputs = [case['expected_output'] for case in data]
    
    print(f"Trip duration range: {min(durations)} - {max(durations)} days")
    print(f"Miles range: {min(miles)} - {max(miles)} miles")
    print(f"Receipts range: ${min(receipts):.2f} - ${max(receipts):.2f}")
    print(f"Reimbursement range: ${min(outputs):.2f} - ${max(outputs):.2f}")
    print()
    
    # Calculate per-day averages
    miles_per_day = [m/d for m, d in zip(miles, durations)]
    receipts_per_day = [r/d for r, d in zip(receipts, durations)]
    reimbursement_per_day = [o/d for o, d in zip(outputs, durations)]
    
    print("=== PER-DAY AVERAGES ===")
    print(f"Average miles per day: {sum(miles_per_day)/len(miles_per_day):.2f}")
    print(f"Average receipts per day: ${sum(receipts_per_day)/len(receipts_per_day):.2f}")
    print(f"Average reimbursement per day: ${sum(reimbursement_per_day)/len(reimbursement_per_day):.2f}")
    print()

def analyze_by_trip_length(data):
    """Analyze patterns by trip duration"""
    print("=== ANALYSIS BY TRIP LENGTH ===")
    
    # Group by trip duration
    by_duration = defaultdict(list)
    for case in data:
        duration = case['input']['trip_duration_days']
        reimbursement_per_day = case['expected_output'] / duration
        by_duration[duration].append(reimbursement_per_day)
    
    for duration in sorted(by_duration.keys()):
        values = by_duration[duration]
        avg = sum(values) / len(values)
        print(f"{duration} days: {len(values)} cases, avg ${avg:.2f}/day")
    print()

def analyze_simple_cases(data):
    """Analyze simple cases to understand base patterns"""
    print("=== SIMPLE CASE ANALYSIS ===")
    
    # Find cases with low receipts and low mileage to understand base per diem
    simple_cases = []
    for case in data:
        if (case['input']['total_receipts_amount'] < 50 and 
            case['input']['miles_traveled'] < 100):
            simple_cases.append(case)
    
    print(f"Simple cases (low receipts & mileage): {len(simple_cases)}")
    
    if simple_cases:
        print("Sample simple cases:")
        for case in simple_cases[:10]:
            inp = case['input']
            out = case['expected_output']
            per_day = out / inp['trip_duration_days']
            print(f"  {inp['trip_duration_days']} days, {inp['miles_traveled']} miles, ${inp['total_receipts_amount']:.2f} receipts -> ${out:.2f} (${per_day:.2f}/day)")
    print()

def analyze_mileage_patterns(data):
    """Analyze mileage patterns"""
    print("=== MILEAGE ANALYSIS ===")
    
    # Look at cases with minimal receipts to isolate mileage effects
    low_receipt_cases = []
    for case in data:
        if case['input']['total_receipts_amount'] < 25:
            low_receipt_cases.append(case)
    
    print(f"Cases with <$25 receipts: {len(low_receipt_cases)}")
    
    if low_receipt_cases:
        print("Sample mileage analysis (assuming $100/day base):")
        for case in low_receipt_cases[:15]:
            inp = case['input']
            out = case['expected_output']
            
            # Estimate mileage component
            base_estimate = inp['trip_duration_days'] * 100
            mileage_component = out - base_estimate
            
            if inp['miles_traveled'] > 0:
                implied_rate = mileage_component / inp['miles_traveled']
                print(f"  {inp['miles_traveled']} miles, {inp['trip_duration_days']} days: ${implied_rate:.3f}/mile")
    print()

def analyze_5_day_bonus(data):
    """Analyze the 5-day trip bonus"""
    print("=== 5-DAY TRIP BONUS ANALYSIS ===")
    
    five_day_cases = []
    four_six_day_cases = []
    
    for case in data:
        duration = case['input']['trip_duration_days']
        reimbursement_per_day = case['expected_output'] / duration
        
        if duration == 5:
            five_day_cases.append(reimbursement_per_day)
        elif duration in [4, 6]:
            four_six_day_cases.append(reimbursement_per_day)
    
    if five_day_cases and four_six_day_cases:
        five_day_avg = sum(five_day_cases) / len(five_day_cases)
        other_avg = sum(four_six_day_cases) / len(four_six_day_cases)
        
        print(f"5-day trips: {len(five_day_cases)} cases, avg ${five_day_avg:.2f}/day")
        print(f"4&6-day trips: {len(four_six_day_cases)} cases, avg ${other_avg:.2f}/day")
        print(f"5-day bonus: ${five_day_avg - other_avg:.2f}/day ({((five_day_avg/other_avg - 1) * 100):.1f}%)")
    print()

def analyze_efficiency_patterns(data):
    """Analyze efficiency (miles per day) patterns"""
    print("=== EFFICIENCY ANALYSIS ===")
    
    # Group by efficiency ranges
    efficiency_groups = {
        'low': [],      # < 100 miles/day
        'medium': [],   # 100-200 miles/day
        'high': [],     # 200-300 miles/day
        'very_high': [] # > 300 miles/day
    }
    
    for case in data:
        inp = case['input']
        efficiency = inp['miles_traveled'] / inp['trip_duration_days']
        reimbursement_per_day = case['expected_output'] / inp['trip_duration_days']
        
        if efficiency < 100:
            efficiency_groups['low'].append(reimbursement_per_day)
        elif efficiency < 200:
            efficiency_groups['medium'].append(reimbursement_per_day)
        elif efficiency < 300:
            efficiency_groups['high'].append(reimbursement_per_day)
        else:
            efficiency_groups['very_high'].append(reimbursement_per_day)
    
    for group_name, values in efficiency_groups.items():
        if values:
            avg = sum(values) / len(values)
            print(f"{group_name} efficiency: {len(values)} cases, avg ${avg:.2f}/day")
    print()

def main():
    """Main analysis function"""
    print("Loading data...")
    data = load_data()
    
    analyze_basic_patterns(data)
    analyze_by_trip_length(data)
    analyze_simple_cases(data)
    analyze_mileage_patterns(data)
    analyze_5_day_bonus(data)
    analyze_efficiency_patterns(data)
    
    print("Analysis complete!")

if __name__ == "__main__":
    main() 