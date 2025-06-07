#!/usr/bin/env python3

def calculate_reimbursement_improved(trip_duration_days, miles_traveled, total_receipts_amount):
    """
    Improved reimbursement calculation based on high-error case analysis
    
    Key improvements:
    1. Fix 1-day high-mileage under-prediction
    2. Add vacation penalty for long trips + high receipts
    3. Implement Kevin's efficiency sweet spot bonus
    4. More nuanced receipt penalty system
    5. Better inverse relationship modeling
    """
    
    # Base per-day rates with improved inverse relationship
    if trip_duration_days == 1:
        base_per_day = 140  # Increased from 120 for high-mileage cases
    elif trip_duration_days == 2:
        base_per_day = 110  # Slightly increased
    elif trip_duration_days <= 5:
        base_per_day = 100
    elif trip_duration_days <= 7:
        base_per_day = 95
    else:
        base_per_day = 90  # Reduced for long trips
    
    base_amount = base_per_day * trip_duration_days
    
    # Improved mileage calculation with efficiency bonuses
    miles_per_day = miles_traveled / trip_duration_days
    
    # Base mileage reimbursement (tiered)
    if miles_traveled <= 500:
        mileage_amount = miles_traveled * 0.65
    elif miles_traveled <= 1000:
        mileage_amount = 500 * 0.65 + (miles_traveled - 500) * 0.45
    else:
        mileage_amount = 500 * 0.65 + 500 * 0.45 + (miles_traveled - 1000) * 0.25
    
    # Kevin's efficiency sweet spot bonus (180-220 miles/day)
    efficiency_bonus = 0
    if 180 <= miles_per_day <= 220:
        efficiency_bonus = trip_duration_days * 40  # $40/day bonus for sweet spot
    elif miles_per_day > 300:
        # Penalty for very high efficiency (suspicious)
        efficiency_bonus = -trip_duration_days * 20
    
    # Improved receipt calculation with context-aware penalties
    receipts_per_day = total_receipts_amount / trip_duration_days
    
    # Base receipt reimbursement (tiered)
    if total_receipts_amount <= 200:
        receipt_amount = total_receipts_amount * 0.8
    elif total_receipts_amount <= 500:
        receipt_amount = 200 * 0.8 + (total_receipts_amount - 200) * 0.6
    else:
        receipt_amount = 200 * 0.8 + 300 * 0.6 + (total_receipts_amount - 500) * 0.4
    
    # Context-aware receipt penalties
    receipt_penalty = 0
    
    # High receipts on short trips (but not too aggressive)
    if trip_duration_days <= 2 and total_receipts_amount > 2000:
        # Only penalize if also low mileage (fraud indicator)
        if miles_traveled < 200:
            receipt_penalty = receipt_amount * 0.4  # 40% penalty
    
    # Very high receipts on medium trips
    elif 3 <= trip_duration_days <= 6 and total_receipts_amount > 2200:
        if receipts_per_day > 400:  # Very high daily spending
            receipt_penalty = receipt_amount * 0.2  # 20% penalty
    
    # Vacation penalty: long trips with high spending
    vacation_penalty = 0
    if trip_duration_days >= 8 and receipts_per_day > 150:
        vacation_penalty = base_amount * 0.15  # 15% penalty on base amount
    
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
    
    return round(total, 2)

def test_improved_algorithm():
    """Test the improved algorithm on high-error cases"""
    
    import json
    from calculate_reimbursement import calculate_reimbursement
    
    with open('public_cases.json', 'r') as f:
        data = json.load(f)
    
    # Test on the top error cases we identified
    high_error_cases = [
        (684, 8, 795, 1645.99, 644.69),    # Long trip + high receipts
        (175, 4, 87, 2463.92, 1413.52),   # Short trip + very high receipts
        (940, 1, 1002, 2320.13, 1475.40), # 1-day + high mileage + high receipts
        (711, 5, 516, 1878.49, 669.85),   # 5-day + medium efficiency + high receipts
        (520, 14, 481, 939.99, 877.17),   # Very long trip
    ]
    
    print("🔧 TESTING IMPROVED ALGORITHM")
    print("=" * 60)
    print("Testing on top 5 high-error cases:")
    print()
    
    total_old_error = 0
    total_new_error = 0
    
    for case_id, duration, miles, receipts, expected in high_error_cases:
        old_prediction = calculate_reimbursement(duration, miles, receipts)
        new_prediction = calculate_reimbursement_improved(duration, miles, receipts)
        
        old_error = abs(old_prediction - expected)
        new_error = abs(new_prediction - expected)
        
        total_old_error += old_error
        total_new_error += new_error
        
        improvement = old_error - new_error
        improvement_pct = (improvement / old_error) * 100 if old_error > 0 else 0
        
        status = "✅ BETTER" if new_error < old_error else "❌ WORSE" if new_error > old_error else "➡️ SAME"
        
        print(f"Case {case_id}: {duration}d, {miles}mi, ${receipts:.2f}")
        print(f"  Expected: ${expected:.2f}")
        print(f"  Old: ${old_prediction:.2f} (error: ${old_error:.2f})")
        print(f"  New: ${new_prediction:.2f} (error: ${new_error:.2f})")
        print(f"  {status} - Improvement: ${improvement:.2f} ({improvement_pct:+.1f}%)")
        print()
    
    avg_old_error = total_old_error / len(high_error_cases)
    avg_new_error = total_new_error / len(high_error_cases)
    overall_improvement = ((avg_old_error - avg_new_error) / avg_old_error) * 100
    
    print(f"📊 SUMMARY:")
    print(f"  Average old error: ${avg_old_error:.2f}")
    print(f"  Average new error: ${avg_new_error:.2f}")
    print(f"  Overall improvement: {overall_improvement:+.1f}%")
    
    return avg_new_error < avg_old_error

if __name__ == "__main__":
    test_improved_algorithm() 