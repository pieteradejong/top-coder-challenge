#!/usr/bin/env python3

import json
import numpy as np
from collections import defaultdict

def analyze_five_day_bonus():
    """Analyze 5-day trips to understand the bonus pattern mentioned by Lisa"""
    
    with open('public_cases.json', 'r') as f:
        data = json.load(f)
    
    # Group by trip duration, focusing on 4, 5, 6 days
    by_duration = defaultdict(list)
    
    for case in data:
        duration = case['input']['trip_duration_days']
        if duration in [4, 5, 6]:
            miles = case['input']['miles_traveled']
            receipts = case['input']['total_receipts_amount']
            reimbursement = case['expected_output']
            
            by_duration[duration].append({
                'miles': miles,
                'receipts': receipts,
                'reimbursement': reimbursement,
                'per_day': reimbursement / duration,
                'miles_per_day': miles / duration,
                'receipts_per_day': receipts / duration
            })
    
    print("=== 5-DAY BONUS ANALYSIS ===")
    print()
    
    # Compare 5-day trips to 4-day and 6-day
    for duration in [4, 5, 6]:
        cases = by_duration[duration]
        per_day_rates = [c['per_day'] for c in cases]
        
        print(f"{duration}-day trips ({len(cases)} cases):")
        print(f"  Mean per-day: ${np.mean(per_day_rates):.2f}")
        print(f"  Median per-day: ${np.median(per_day_rates):.2f}")
        print(f"  Range: ${min(per_day_rates):.2f} - ${max(per_day_rates):.2f}")
        print()
    
    # Look for efficiency patterns in 5-day trips
    print("=== 5-DAY EFFICIENCY PATTERNS ===")
    print()
    
    five_day_cases = by_duration[5]
    
    # Sort by efficiency (miles per day)
    five_day_cases.sort(key=lambda x: x['miles_per_day'])
    
    print("5-day trips by efficiency (miles/day):")
    print("Low efficiency (bottom 10):")
    for case in five_day_cases[:10]:
        print(f"  {case['miles_per_day']:.1f} mi/day: ${case['per_day']:.2f}/day reimbursement")
    
    print("\nHigh efficiency (top 10):")
    for case in five_day_cases[-10:]:
        print(f"  {case['miles_per_day']:.1f} mi/day: ${case['per_day']:.2f}/day reimbursement")
    
    print()
    
    # Look for the "sweet spot" mentioned by Kevin: 180-220 miles/day
    print("=== SWEET SPOT ANALYSIS (180-220 miles/day) ===")
    print()
    
    sweet_spot_cases = [c for c in five_day_cases if 180 <= c['miles_per_day'] <= 220]
    other_cases = [c for c in five_day_cases if not (180 <= c['miles_per_day'] <= 220)]
    
    if sweet_spot_cases:
        sweet_spot_rates = [c['per_day'] for c in sweet_spot_cases]
        other_rates = [c['per_day'] for c in other_cases]
        
        print(f"Sweet spot cases (180-220 mi/day): {len(sweet_spot_cases)} cases")
        print(f"  Mean per-day: ${np.mean(sweet_spot_rates):.2f}")
        print(f"  Median per-day: ${np.median(sweet_spot_rates):.2f}")
        
        print(f"\nOther 5-day cases: {len(other_cases)} cases")
        print(f"  Mean per-day: ${np.mean(other_rates):.2f}")
        print(f"  Median per-day: ${np.median(other_rates):.2f}")
        
        bonus = np.mean(sweet_spot_rates) - np.mean(other_rates)
        print(f"\nSweet spot bonus: ${bonus:.2f}/day")
    
    print()
    
    # Look for spending patterns
    print("=== 5-DAY SPENDING PATTERNS ===")
    print()
    
    # Kevin mentioned <$100/day spending as part of sweet spot
    low_spending = [c for c in five_day_cases if c['receipts_per_day'] < 100]
    high_spending = [c for c in five_day_cases if c['receipts_per_day'] >= 100]
    
    if low_spending and high_spending:
        low_rates = [c['per_day'] for c in low_spending]
        high_rates = [c['per_day'] for c in high_spending]
        
        print(f"Low spending (<$100/day): {len(low_spending)} cases")
        print(f"  Mean per-day: ${np.mean(low_rates):.2f}")
        
        print(f"High spending (≥$100/day): {len(high_spending)} cases")
        print(f"  Mean per-day: ${np.mean(high_rates):.2f}")
        
        spending_bonus = np.mean(low_rates) - np.mean(high_rates)
        print(f"\nLow spending bonus: ${spending_bonus:.2f}/day")
    
    print()
    
    # Look for the "sweet spot combo" mentioned by Kevin
    print("=== SWEET SPOT COMBO ANALYSIS ===")
    print("Kevin mentioned: 5-day + 180+ miles/day + <$100/day spending")
    print()
    
    combo_cases = [c for c in five_day_cases 
                   if c['miles_per_day'] >= 180 and c['receipts_per_day'] < 100]
    non_combo_cases = [c for c in five_day_cases 
                       if not (c['miles_per_day'] >= 180 and c['receipts_per_day'] < 100)]
    
    if combo_cases:
        combo_rates = [c['per_day'] for c in combo_cases]
        non_combo_rates = [c['per_day'] for c in non_combo_cases]
        
        print(f"Sweet spot combo cases: {len(combo_cases)} cases")
        print(f"  Mean per-day: ${np.mean(combo_rates):.2f}")
        print(f"  Examples:")
        for case in combo_cases[:5]:
            print(f"    {case['miles_per_day']:.1f} mi/day, ${case['receipts_per_day']:.2f}/day -> ${case['per_day']:.2f}/day")
        
        print(f"\nOther 5-day cases: {len(non_combo_cases)} cases")
        print(f"  Mean per-day: ${np.mean(non_combo_rates):.2f}")
        
        combo_bonus = np.mean(combo_rates) - np.mean(non_combo_rates)
        print(f"\nSweet spot combo bonus: ${combo_bonus:.2f}/day")

if __name__ == "__main__":
    analyze_five_day_bonus() 