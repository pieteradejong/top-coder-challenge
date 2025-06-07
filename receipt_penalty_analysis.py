#!/usr/bin/env python3

import json
import numpy as np
from collections import defaultdict

def analyze_receipt_penalties():
    """Analyze cases with high receipt amounts to understand penalty patterns"""
    
    with open('public_cases.json', 'r') as f:
        data = json.load(f)
    
    # Focus on cases with high receipt amounts
    high_receipt_cases = []
    
    for i, case in enumerate(data):
        duration = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        reimbursement = case['expected_output']
        
        receipts_per_day = receipts / duration
        
        # Look for cases with high receipts per day
        if receipts_per_day > 200:
            high_receipt_cases.append({
                'case_id': i,
                'duration': duration,
                'miles': miles,
                'receipts': receipts,
                'reimbursement': reimbursement,
                'receipts_per_day': receipts_per_day,
                'reimbursement_per_day': reimbursement / duration,
                'receipt_ratio': reimbursement / receipts if receipts > 0 else 0
            })
    
    print("=== HIGH RECEIPT PENALTY ANALYSIS ===")
    print(f"Found {len(high_receipt_cases)} cases with >$200/day in receipts")
    print()
    
    # Sort by receipt ratio (reimbursement / receipts) to find the most penalized
    high_receipt_cases.sort(key=lambda x: x['receipt_ratio'])
    
    print("Most penalized cases (lowest reimbursement/receipt ratio):")
    for case in high_receipt_cases[:10]:
        print(f"  Case {case['case_id']}: {case['duration']} days, {case['miles']} miles, ${case['receipts']:.2f} receipts")
        print(f"    -> ${case['reimbursement']:.2f} reimbursement (ratio: {case['receipt_ratio']:.3f})")
        print(f"    -> ${case['receipts_per_day']:.2f}/day receipts, ${case['reimbursement_per_day']:.2f}/day reimbursement")
        print()
    
    # Analyze by trip duration
    print("=== RECEIPT PENALTIES BY TRIP DURATION ===")
    print()
    
    by_duration = defaultdict(list)
    for case in high_receipt_cases:
        by_duration[case['duration']].append(case)
    
    for duration in sorted(by_duration.keys()):
        cases = by_duration[duration]
        ratios = [c['receipt_ratio'] for c in cases]
        
        print(f"Duration {duration} days ({len(cases)} high-receipt cases):")
        print(f"  Receipt ratio range: {min(ratios):.3f} - {max(ratios):.3f}")
        print(f"  Mean receipt ratio: {np.mean(ratios):.3f}")
        print(f"  Median receipt ratio: {np.median(ratios):.3f}")
        
        # Show a few examples
        sorted_cases = sorted(cases, key=lambda x: x['receipt_ratio'])
        print(f"  Lowest ratio example: ${sorted_cases[0]['receipts']:.2f} -> ${sorted_cases[0]['reimbursement']:.2f} (ratio: {sorted_cases[0]['receipt_ratio']:.3f})")
        if len(sorted_cases) > 1:
            print(f"  Highest ratio example: ${sorted_cases[-1]['receipts']:.2f} -> ${sorted_cases[-1]['reimbursement']:.2f} (ratio: {sorted_cases[-1]['receipt_ratio']:.3f})")
        print()
    
    # Look for thresholds
    print("=== RECEIPT THRESHOLD ANALYSIS ===")
    print()
    
    # Group by receipt amount ranges
    ranges = [
        (0, 500),
        (500, 1000),
        (1000, 1500),
        (1500, 2000),
        (2000, 2500),
        (2500, float('inf'))
    ]
    
    for min_receipts, max_receipts in ranges:
        range_cases = []
        for case in data:
            receipts = case['input']['total_receipts_amount']
            if min_receipts <= receipts < max_receipts:
                duration = case['input']['trip_duration_days']
                reimbursement = case['expected_output']
                ratio = reimbursement / receipts if receipts > 0 else 0
                range_cases.append(ratio)
        
        if range_cases:
            range_name = f"${min_receipts}-${max_receipts}" if max_receipts != float('inf') else f"${min_receipts}+"
            print(f"Receipt range {range_name} ({len(range_cases)} cases):")
            print(f"  Mean ratio: {np.mean(range_cases):.3f}")
            print(f"  Median ratio: {np.median(range_cases):.3f}")
            print(f"  Min ratio: {min(range_cases):.3f}")
            print(f"  Max ratio: {max(range_cases):.3f}")
            print()
    
    # Specific analysis of the high-error cases mentioned in the evaluation
    print("=== ANALYSIS OF SPECIFIC HIGH-ERROR CASES ===")
    print()
    
    high_error_cases = [
        (4, 69, 2321.49, 322.00),  # Case 152
        (8, 795, 1645.99, 644.69),  # Case 684
        (14, 481, 939.99, 877.17),  # Case 520
        (5, 516, 1878.49, 669.85),  # Case 711
        (11, 740, 1171.99, 902.09)  # Case 367
    ]
    
    for duration, miles, receipts, expected in high_error_cases:
        ratio = expected / receipts
        receipts_per_day = receipts / duration
        reimbursement_per_day = expected / duration
        
        print(f"Case: {duration} days, {miles} miles, ${receipts:.2f} receipts -> ${expected:.2f}")
        print(f"  Receipt ratio: {ratio:.3f}")
        print(f"  Receipts per day: ${receipts_per_day:.2f}")
        print(f"  Reimbursement per day: ${reimbursement_per_day:.2f}")
        print()

if __name__ == "__main__":
    analyze_receipt_penalties() 