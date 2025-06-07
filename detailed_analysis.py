#!/usr/bin/env python3

import json
import math

def load_data():
    """Load the public test cases"""
    with open('public_cases.json', 'r') as f:
        data = json.load(f)
    return data

def analyze_per_day_rates(data):
    """Analyze per-day reimbursement rates by trip length"""
    print("=== DETAILED PER-DAY RATE ANALYSIS ===")
    
    # The data shows a clear inverse relationship with trip length
    # 1 day: $873.55/day
    # 2 days: $523.12/day  
    # 3 days: $336.85/day
    # etc.
    
    # This suggests a base amount that gets divided by days, plus per-day components
    
    # Let's look for patterns in the base amount
    total_reimbursements = []
    for case in data:
        inp = case['input']
        out = case['expected_output']
        total_reimbursements.append((inp['trip_duration_days'], out))
    
    # Group by duration and look at total amounts
    by_duration = {}
    for duration, total in total_reimbursements:
        if duration not in by_duration:
            by_duration[duration] = []
        by_duration[duration].append(total)
    
    print("Average total reimbursement by trip length:")
    for duration in sorted(by_duration.keys()):
        totals = by_duration[duration]
        avg_total = sum(totals) / len(totals)
        avg_per_day = avg_total / duration
        print(f"{duration} days: ${avg_total:.2f} total, ${avg_per_day:.2f}/day")
    print()

def analyze_mileage_tiers(data):
    """Analyze mileage reimbursement tiers"""
    print("=== MILEAGE TIER ANALYSIS ===")
    
    # Look at cases with minimal receipts to isolate mileage effects
    low_receipt_cases = []
    for case in data:
        if case['input']['total_receipts_amount'] < 50:
            inp = case['input']
            out = case['expected_output']
            
            # Calculate implied mileage rate
            # Try different base per diem assumptions
            for base_per_day in [100, 120, 80]:
                base_estimate = inp['trip_duration_days'] * base_per_day
                mileage_component = out - base_estimate
                
                if inp['miles_traveled'] > 0:
                    implied_rate = mileage_component / inp['miles_traveled']
                    low_receipt_cases.append({
                        'miles': inp['miles_traveled'],
                        'days': inp['trip_duration_days'],
                        'receipts': inp['total_receipts_amount'],
                        'output': out,
                        'base_assumption': base_per_day,
                        'implied_rate': implied_rate
                    })
    
    # Sort by miles to see tier patterns
    low_receipt_cases.sort(key=lambda x: x['miles'])
    
    print("Mileage rate analysis (assuming $100/day base):")
    for case in low_receipt_cases[:20]:
        if case['base_assumption'] == 100:
            print(f"  {case['miles']:3.0f} miles: ${case['implied_rate']:.3f}/mile")
    print()

def analyze_efficiency_bonus(data):
    """Analyze efficiency bonus patterns"""
    print("=== EFFICIENCY BONUS ANALYSIS ===")
    
    # The data shows clear efficiency bonuses:
    # low efficiency (<100 mi/day): $173.75/day
    # medium efficiency (100-200 mi/day): $269.63/day  
    # high efficiency (200-300 mi/day): $395.51/day
    # very high efficiency (>300 mi/day): $787.51/day
    
    efficiency_cases = []
    for case in data:
        inp = case['input']
        out = case['expected_output']
        efficiency = inp['miles_traveled'] / inp['trip_duration_days']
        per_day = out / inp['trip_duration_days']
        
        efficiency_cases.append({
            'efficiency': efficiency,
            'per_day': per_day,
            'miles': inp['miles_traveled'],
            'days': inp['trip_duration_days'],
            'receipts': inp['total_receipts_amount']
        })
    
    # Sort by efficiency
    efficiency_cases.sort(key=lambda x: x['efficiency'])
    
    print("Efficiency patterns:")
    for i in range(0, len(efficiency_cases), 50):  # Sample every 50th case
        case = efficiency_cases[i]
        print(f"  {case['efficiency']:6.1f} mi/day: ${case['per_day']:6.2f}/day")
    print()

def find_base_formula(data):
    """Try to find the base formula"""
    print("=== BASE FORMULA ANALYSIS ===")
    
    # Based on the patterns, it looks like there might be:
    # 1. A base per-diem component
    # 2. A mileage component with tiers
    # 3. An efficiency bonus
    # 4. A receipt component
    
    # Let's try to reverse engineer some simple cases
    simple_cases = []
    for case in data:
        inp = case['input']
        out = case['expected_output']
        
        # Focus on cases with low receipts to minimize that variable
        if inp['total_receipts_amount'] < 100:
            simple_cases.append({
                'days': inp['trip_duration_days'],
                'miles': inp['miles_traveled'],
                'receipts': inp['total_receipts_amount'],
                'output': out,
                'efficiency': inp['miles_traveled'] / inp['trip_duration_days'],
                'per_day': out / inp['trip_duration_days']
            })
    
    # Sort by efficiency to see patterns
    simple_cases.sort(key=lambda x: x['efficiency'])
    
    print("Simple cases sorted by efficiency:")
    for case in simple_cases[:30]:
        print(f"  {case['days']}d, {case['miles']:3.0f}mi, ${case['receipts']:5.2f}r, {case['efficiency']:6.1f}mi/d -> ${case['output']:6.2f} (${case['per_day']:6.2f}/d)")
    print()

def main():
    """Main analysis function"""
    print("Loading data...")
    data = load_data()
    
    analyze_per_day_rates(data)
    analyze_mileage_tiers(data)
    analyze_efficiency_bonus(data)
    find_base_formula(data)
    
    print("Detailed analysis complete!")

if __name__ == "__main__":
    main() 