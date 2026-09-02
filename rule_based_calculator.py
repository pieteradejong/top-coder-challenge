#!/usr/bin/env python3
"""
Rule-Based Calculator
====================

Implementation of the discovered business rules from mathematical pattern analysis.
This represents the true legacy system algorithm based on tier structures.
"""

def calculate_reimbursement(trip_duration_days, miles_traveled, total_receipts_amount):
    """
    Calculate reimbursement using discovered business rules
    
    Based on mathematical pattern analysis:
    - 7-tier mileage structure
    - 8-tier receipt structure  
    - Efficiency bonuses/penalties
    - Vacation penalties
    - Duration-based base rates
    """
    
    duration = trip_duration_days
    miles = miles_traveled
    receipts = total_receipts_amount
    
    # Calculate derived metrics
    miles_per_day = miles / duration if duration > 0 else 0
    receipts_per_day = receipts / duration if duration > 0 else 0
    
    # Base rate using discovered inverse relationship
    # Formula: per_day_rate = 458.58 / duration + 161.95
    base_per_day = 458.58 / duration + 161.95
    base_amount = base_per_day * duration
    
    # Mileage component using discovered tier structure
    mileage_component = 0
    remaining_miles = miles
    
    # 7-tier mileage structure
    mileage_tiers = [
        (100, 40.39),    # 0-100 miles: $40.39/mile
        (100, 7.53),     # 100-200 miles: $7.53/mile  
        (100, 4.40),     # 200-300 miles: $4.40/mile
        (200, 3.15),     # 300-500 miles: $3.15/mile
        (250, 2.26),     # 500-750 miles: $2.26/mile
        (250, 1.78),     # 750-1000 miles: $1.78/mile
        (float('inf'), 1.46)  # 1000+ miles: $1.46/mile
    ]
    
    for tier_miles, rate in mileage_tiers:
        if remaining_miles <= 0:
            break
        tier_amount = min(remaining_miles, tier_miles)
        mileage_component += tier_amount * rate
        remaining_miles -= tier_amount
    
    # Receipt component using discovered tier structure
    receipt_component = 0
    remaining_receipts = receipts
    
    # 8-tier receipt structure
    receipt_tiers = [
        (50, 36.37),     # $0-50: $36.37/dollar
        (50, 9.70),      # $50-100: $9.70/dollar
        (50, 6.31),      # $100-150: $6.31/dollar
        (50, 5.09),      # $150-200: $5.09/dollar
        (100, 3.18),     # $200-300: $3.18/dollar
        (200, 2.03),     # $300-500: $2.03/dollar
        (500, 1.61),     # $500-1000: $1.61/dollar
        (float('inf'), 1.00)  # $1000+: $1.00/dollar
    ]
    
    for tier_amount, rate in receipt_tiers:
        if remaining_receipts <= 0:
            break
        tier_receipts = min(remaining_receipts, tier_amount)
        receipt_component += tier_receipts * rate
        remaining_receipts -= tier_receipts
    
    # Efficiency bonus/penalty based on miles per day
    efficiency_adjustment = 0
    
    if miles_per_day >= 400:
        # Extreme efficiency bonus
        efficiency_adjustment = 675.55 * duration
    elif miles_per_day >= 300:
        efficiency_adjustment = 218.71 * duration
    elif miles_per_day >= 250:
        efficiency_adjustment = 94.39 * duration
    elif miles_per_day >= 220:
        efficiency_adjustment = 166.69 * duration
    elif miles_per_day >= 200:
        # Sweet spot bonus
        efficiency_adjustment = 98.79 * duration
    elif miles_per_day >= 180:
        # Sweet spot bonus
        efficiency_adjustment = 19.97 * duration
    elif miles_per_day >= 150:
        efficiency_adjustment = 15.46 * duration
    elif miles_per_day >= 100:
        efficiency_adjustment = -28.24 * duration
    elif miles_per_day >= 50:
        efficiency_adjustment = -102.90 * duration
    else:
        efficiency_adjustment = -118.85 * duration
    
    # Vacation penalty for long trips
    vacation_penalty = 0
    if duration >= 8:
        vacation_penalty = 251.64 * duration
    
    # Calculate total reimbursement
    total_reimbursement = (
        base_amount + 
        mileage_component + 
        receipt_component + 
        efficiency_adjustment - 
        vacation_penalty
    )
    
    # Ensure non-negative result
    total_reimbursement = max(0, total_reimbursement)
    
    return round(total_reimbursement, 2)

if __name__ == "__main__":
    # Test with a few examples
    test_cases = [
        (3, 93, 1.42),      # First public case
        (5, 250, 150.75),   # 5-day trip
        (1, 50, 25.0),      # Single day
        (10, 800, 500.0),   # Long trip with vacation penalty
        (3, 600, 100.0),    # High efficiency
    ]
    
    print("Rule-Based Calculator Test Results:")
    print("=" * 50)
    
    for duration, miles, receipts in test_cases:
        result = calculate_reimbursement(duration, miles, receipts)
        miles_per_day = miles / duration
        print(f"Duration: {duration}, Miles: {miles}, Receipts: ${receipts}")
        print(f"Miles/day: {miles_per_day:.1f}, Reimbursement: ${result}")
        print("-" * 30) 