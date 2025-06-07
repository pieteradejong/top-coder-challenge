#!/usr/bin/env python3

import json
from collections import defaultdict

def analyze_public_cases():
    """Analyze patterns in the public cases data"""
    
    with open('public_cases.json', 'r') as f:
        data = json.load(f)

    print('=== PUBLIC CASES DATA ANALYSIS ===')
    print(f'Total cases: {len(data)}')

    # Duration analysis
    durations = [case['input']['trip_duration_days'] for case in data]
    duration_counts = defaultdict(int)
    for d in durations:
        duration_counts[d] += 1

    print('\nTrip Duration Distribution:')
    for d in sorted(duration_counts.keys()):
        print(f'  {d} days: {duration_counts[d]} cases ({duration_counts[d]/len(data)*100:.1f}%)')

    # Miles analysis
    miles = [case['input']['miles_traveled'] for case in data]
    print(f'\nMiles Statistics:')
    print(f'  Range: {min(miles)} - {max(miles)} miles')
    print(f'  Average: {sum(miles)/len(miles):.1f} miles')
    print(f'  High mileage (>500): {sum(1 for m in miles if m > 500)} cases')
    print(f'  Very high mileage (>1000): {sum(1 for m in miles if m > 1000)} cases')

    # Receipts analysis
    receipts = [case['input']['total_receipts_amount'] for case in data]
    print(f'\nReceipts Statistics:')
    print(f'  Range: ${min(receipts):.2f} - ${max(receipts):.2f}')
    print(f'  Average: ${sum(receipts)/len(receipts):.2f}')
    print(f'  Low receipts (<$50): {sum(1 for r in receipts if r < 50)} cases')
    print(f'  High receipts (>$1000): {sum(1 for r in receipts if r > 1000)} cases')
    print(f'  Very high receipts (>$2000): {sum(1 for r in receipts if r > 2000)} cases')

    # Output analysis
    outputs = [case['expected_output'] for case in data]
    print(f'\nReimbursement Statistics:')
    print(f'  Range: ${min(outputs):.2f} - ${max(outputs):.2f}')
    print(f'  Average: ${sum(outputs)/len(outputs):.2f}')

    # Extreme cases
    print('\n=== EXTREME CASES ===')
    print('Top 5 highest reimbursements:')
    sorted_by_output = sorted(data, key=lambda x: x['expected_output'], reverse=True)
    for i, case in enumerate(sorted_by_output[:5]):
        inp = case['input']
        out = case['expected_output']
        ratio = out / inp['total_receipts_amount'] if inp['total_receipts_amount'] > 0 else 0
        print(f'  {i+1}. {inp["trip_duration_days"]}d, {inp["miles_traveled"]}mi, ${inp["total_receipts_amount"]:.2f} -> ${out:.2f} (ratio: {ratio:.2f})')

    print('\nTop 5 lowest reimbursements:')
    for i, case in enumerate(sorted_by_output[-5:]):
        inp = case['input']
        out = case['expected_output']
        ratio = out / inp['total_receipts_amount'] if inp['total_receipts_amount'] > 0 else 0
        print(f'  {i+1}. {inp["trip_duration_days"]}d, {inp["miles_traveled"]}mi, ${inp["total_receipts_amount"]:.2f} -> ${out:.2f} (ratio: {ratio:.2f})')

    # Efficiency patterns
    print('\n=== EFFICIENCY PATTERNS ===')
    efficiency_cases = []
    for case in data:
        inp = case['input']
        out = case['expected_output']
        miles_per_day = inp['miles_traveled'] / inp['trip_duration_days']
        receipts_per_day = inp['total_receipts_amount'] / inp['trip_duration_days']
        per_day_rate = out / inp['trip_duration_days']
        
        efficiency_cases.append({
            'duration': inp['trip_duration_days'],
            'miles_per_day': miles_per_day,
            'receipts_per_day': receipts_per_day,
            'per_day_rate': per_day_rate,
            'total_output': out
        })

    # Kevin's sweet spot analysis (180-220 miles/day)
    sweet_spot_cases = [c for c in efficiency_cases if 180 <= c['miles_per_day'] <= 220]
    other_cases = [c for c in efficiency_cases if not (180 <= c['miles_per_day'] <= 220)]
    
    if sweet_spot_cases:
        sweet_spot_avg = sum(c['per_day_rate'] for c in sweet_spot_cases) / len(sweet_spot_cases)
        other_avg = sum(c['per_day_rate'] for c in other_cases) / len(other_cases)
        
        print(f'Kevin\'s "Sweet Spot" (180-220 mi/day):')
        print(f'  Cases in sweet spot: {len(sweet_spot_cases)}')
        print(f'  Average per-day rate: ${sweet_spot_avg:.2f}')
        print(f'  Other cases average: ${other_avg:.2f}')
        print(f'  Sweet spot bonus: ${sweet_spot_avg - other_avg:.2f} ({((sweet_spot_avg/other_avg-1)*100):.1f}%)')

    # 5-day trip analysis
    five_day_cases = [c for c in efficiency_cases if c['duration'] == 5]
    if five_day_cases:
        five_day_avg = sum(c['per_day_rate'] for c in five_day_cases) / len(five_day_cases)
        print(f'\n5-Day Trip Analysis:')
        print(f'  Total 5-day cases: {len(five_day_cases)}')
        print(f'  Average per-day rate: ${five_day_avg:.2f}')
        
        # Compare to other durations
        for duration in [4, 6]:
            duration_cases = [c for c in efficiency_cases if c['duration'] == duration]
            if duration_cases:
                duration_avg = sum(c['per_day_rate'] for c in duration_cases) / len(duration_cases)
                print(f'  {duration}-day average: ${duration_avg:.2f} (diff: ${five_day_avg - duration_avg:.2f})')

    # Receipt penalty analysis
    print('\n=== RECEIPT PENALTY PATTERNS ===')
    receipt_ratios = []
    for case in data:
        inp = case['input']
        out = case['expected_output']
        if inp['total_receipts_amount'] > 0:
            ratio = out / inp['total_receipts_amount']
            receipt_ratios.append({
                'receipts': inp['total_receipts_amount'],
                'ratio': ratio,
                'duration': inp['trip_duration_days'],
                'miles': inp['miles_traveled']
            })

    # Group by receipt ranges
    ranges = [(0, 500), (500, 1000), (1000, 1500), (1500, 2000), (2000, 2500), (2500, float('inf'))]
    for min_r, max_r in ranges:
        range_cases = [r for r in receipt_ratios if min_r <= r['receipts'] < max_r]
        if range_cases:
            avg_ratio = sum(r['ratio'] for r in range_cases) / len(range_cases)
            range_name = f'${min_r}-{max_r}' if max_r != float('inf') else f'${min_r}+'
            print(f'  {range_name}: {len(range_cases)} cases, avg ratio: {avg_ratio:.3f}')

if __name__ == "__main__":
    analyze_public_cases() 