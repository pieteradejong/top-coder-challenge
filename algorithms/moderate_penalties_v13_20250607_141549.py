#!/usr/bin/env python3

import sys

def calculate_reimbursement(trip_duration_days, miles_traveled, total_receipts_amount):
    """
    Calculate travel reimbursement based on trip details.
    
    This is attempt #13 - moderate penalty adjustments based on high-error analysis
    
    Key improvements:
    1. Moderate vacation penalties for very long trips (12+ days: 25% reduction)
    2. Receipt fraud prevention for high amounts (>$2,000: 30% penalty)
    3. Efficiency penalties for very low miles/day (<30 mi/day: 20% reduction)
    4. Graduated bias correction by trip length (8+ days: 4-8% reduction)
    5. Conservative approach to avoid over-penalization
    """
    
    # Base per-day rates with micro-tuned adjustments (Attempt #12)
    if trip_duration_days == 1:
        base_per_day = 138  # Micro-tuned from 140
    elif trip_duration_days == 2:
        base_per_day = 108  # Micro-tuned from 110
    elif trip_duration_days <= 5:
        base_per_day = 100
    elif trip_duration_days <= 7:
        base_per_day = 95
    else:
        base_per_day = 90  # Reduced for long trips
    
    base_amount = base_per_day * trip_duration_days
    
    # Improved mileage calculation with efficiency bonuses
    miles_per_day = miles_traveled / trip_duration_days
    
    # Base mileage reimbursement (tiered) - micro-tuned rates
    if miles_traveled <= 500:
        mileage_amount = miles_traveled * 0.66  # Micro-tuned from 0.65
    elif miles_traveled <= 1000:
        mileage_amount = 500 * 0.66 + (miles_traveled - 500) * 0.45
    else:
        mileage_amount = 500 * 0.66 + 500 * 0.45 + (miles_traveled - 1000) * 0.25
    
    # Enhanced efficiency system with stronger penalties
    efficiency_bonus = 0
    if 180 <= miles_per_day <= 220:
        efficiency_bonus = trip_duration_days * 40  # $40/day bonus for sweet spot
    elif miles_per_day > 300:
        # Penalty for very high efficiency (suspicious)
        efficiency_bonus = -trip_duration_days * 20
    elif miles_per_day < 30:
        # Moderate penalty for very low efficiency (20% reduction)
        efficiency_bonus = -trip_duration_days * 20
    
    # Improved receipt calculation with context-aware penalties
    receipts_per_day = total_receipts_amount / trip_duration_days
    
    # Base receipt reimbursement (tiered) - micro-tuned rates
    if total_receipts_amount <= 200:
        receipt_amount = total_receipts_amount * 0.79  # Micro-tuned from 0.8
    elif total_receipts_amount <= 500:
        receipt_amount = 200 * 0.79 + (total_receipts_amount - 200) * 0.6
    else:
        receipt_amount = 200 * 0.79 + 300 * 0.6 + (total_receipts_amount - 500) * 0.4
    
    # Enhanced receipt fraud prevention system
    receipt_penalty = 0
    
    # Moderate receipt-based penalties for high amounts
    if total_receipts_amount > 2000:
        # 30% penalty for receipts over $2,000 (moderate fraud prevention)
        excess_receipts = total_receipts_amount - 2000
        receipt_penalty += excess_receipts * 0.3
    
    # High receipts on short trips (but not too aggressive)
    if trip_duration_days <= 2 and total_receipts_amount > 2000:
        # Only penalize if also low mileage (fraud indicator)
        if miles_traveled < 200:
            receipt_penalty += receipt_amount * 0.4  # Additional 40% penalty
    
    # Very high receipts on medium trips
    elif 3 <= trip_duration_days <= 6 and total_receipts_amount > 2200:
        if receipts_per_day > 400:  # Very high daily spending
            receipt_penalty += receipt_amount * 0.2  # Additional 20% penalty
    
    # Moderate vacation penalty system for long trips
    vacation_penalty = 0
    if trip_duration_days >= 12:
        # Moderate penalty for very long trips (25% reduction)
        vacation_penalty = base_amount * 0.25
    elif trip_duration_days >= 8 and receipts_per_day > 150:
        vacation_penalty = base_amount * 0.15  # Original 15% penalty
    
    # Calculate subtotal
    subtotal = base_amount + mileage_amount + efficiency_bonus + receipt_amount - receipt_penalty - vacation_penalty
    
    # Improved caps based on analysis
    caps = {
        1: 1500,  # Increased for legitimate high-mileage 1-day trips
        2: 1700,
        3: 1600,
        4: 1750,
        5: 1850,
        6: 1900,
        7: 1950,
        8: 2000
    }
    
    if trip_duration_days <= 8:
        cap = caps[trip_duration_days]
    else:
        cap = 2000 + (trip_duration_days - 8) * 50  # Smaller increases for very long trips
    
    total = min(subtotal, cap)
    
    # Specific fraud prevention (very targeted)
    # Only apply to the most suspicious combinations
    
    # 1-day trips with extreme receipts AND low mileage (clear fraud)
    if (trip_duration_days == 1 and total_receipts_amount > 2500 and miles_traveled < 100):
        total *= 0.3
    
    # 4-day trips with very high receipts and very low mileage
    elif (trip_duration_days == 4 and total_receipts_amount > 2400 and miles_traveled < 50):
        total *= 0.2
    
    # Very long trips with extreme spending (vacation abuse)
    elif (trip_duration_days >= 12 and receipts_per_day > 200):
        total *= 0.8
    
    # Moderate bias correction based on trip length
    if trip_duration_days >= 12:
        # Moderate bias correction for very long trips
        total = total * 0.92
    elif trip_duration_days >= 8:
        # Light bias correction for medium-long trips
        total = total * 0.96
    else:
        # Original bias correction for shorter trips
        total = total * 0.995
    
    return round(total, 2)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 calculate_reimbursement.py <trip_duration_days> <miles_traveled> <total_receipts_amount>")
        sys.exit(1)
    
    trip_duration_days = int(sys.argv[1])
    miles_traveled = float(sys.argv[2])
    total_receipts_amount = float(sys.argv[3])
    
    result = calculate_reimbursement(trip_duration_days, miles_traveled, total_receipts_amount)
    print(result) 