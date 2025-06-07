#!/usr/bin/env python3

import sys
import json

def variant_01_current_best(trip_duration_days, miles_traveled, total_receipts_amount):
    """Current best algorithm - moderate penalties approach"""
    
    # Base rates
    if trip_duration_days == 1:
        base_per_day = 138
    elif trip_duration_days == 2:
        base_per_day = 108
    elif trip_duration_days <= 5:
        base_per_day = 100
    elif trip_duration_days <= 7:
        base_per_day = 95
    else:
        base_per_day = 90
    
    base_amount = base_per_day * trip_duration_days
    miles_per_day = miles_traveled / trip_duration_days
    
    # Mileage
    if miles_traveled <= 500:
        mileage_amount = miles_traveled * 0.66
    elif miles_traveled <= 1000:
        mileage_amount = 500 * 0.66 + (miles_traveled - 500) * 0.45
    else:
        mileage_amount = 500 * 0.66 + 500 * 0.45 + (miles_traveled - 1000) * 0.25
    
    # Efficiency
    efficiency_bonus = 0
    if 180 <= miles_per_day <= 220:
        efficiency_bonus = trip_duration_days * 40
    elif miles_per_day > 300:
        efficiency_bonus = -trip_duration_days * 20
    elif miles_per_day < 30:
        efficiency_bonus = -trip_duration_days * 20
    
    # Receipts
    if total_receipts_amount <= 200:
        receipt_amount = total_receipts_amount * 0.79
    elif total_receipts_amount <= 500:
        receipt_amount = 200 * 0.79 + (total_receipts_amount - 200) * 0.6
    else:
        receipt_amount = 200 * 0.79 + 300 * 0.6 + (total_receipts_amount - 500) * 0.4
    
    # Penalties
    receipt_penalty = 0
    if total_receipts_amount > 2000:
        excess_receipts = total_receipts_amount - 2000
        receipt_penalty += excess_receipts * 0.3
    
    vacation_penalty = 0
    if trip_duration_days >= 12:
        vacation_penalty = base_amount * 0.25
    elif trip_duration_days >= 8:
        vacation_penalty = base_amount * 0.15
    
    # Calculate
    subtotal = base_amount + mileage_amount + efficiency_bonus + receipt_amount - receipt_penalty - vacation_penalty
    
    # Caps
    caps = {1: 1500, 2: 1700, 3: 1600, 4: 1750, 5: 1850, 6: 1900, 7: 1950, 8: 2000}
    cap = caps.get(trip_duration_days, 2000 + (trip_duration_days - 8) * 50)
    total = min(subtotal, cap)
    
    # Bias correction
    if trip_duration_days >= 12:
        total = total * 0.92
    elif trip_duration_days >= 8:
        total = total * 0.96
    else:
        total = total * 0.995
    
    return round(total, 2)

def variant_05_business_rules(trip_duration_days, miles_traveled, total_receipts_amount):
    """Heavy business logic based on interview insights"""
    
    miles_per_day = miles_traveled / trip_duration_days
    receipts_per_day = total_receipts_amount / trip_duration_days
    
    # Base per diem with strong inverse
    if trip_duration_days == 1:
        base_per_day = 800
    elif trip_duration_days == 2:
        base_per_day = 500
    elif trip_duration_days == 3:
        base_per_day = 330
    elif trip_duration_days == 4:
        base_per_day = 270
    elif trip_duration_days == 5:
        base_per_day = 230
    else:
        base_per_day = max(100, 1000 / trip_duration_days)
    
    base_amount = base_per_day * trip_duration_days
    
    # Mileage with strong efficiency focus
    if miles_per_day < 50:
        mileage_rate = 0.3  # Penalty for inefficiency
    elif 180 <= miles_per_day <= 220:
        mileage_rate = 0.8  # Kevin's sweet spot
    elif miles_per_day > 300:
        mileage_rate = 0.4  # Suspicious high efficiency
    else:
        mileage_rate = 0.6
    
    mileage_amount = miles_traveled * mileage_rate
    
    # Receipts with fraud prevention
    if receipts_per_day > 300:
        receipt_rate = 0.2  # High spending penalty
    elif receipts_per_day < 50:
        receipt_rate = 0.9  # Low spending bonus
    else:
        receipt_rate = 0.6
    
    receipt_amount = total_receipts_amount * receipt_rate
    
    # 5-day bonus
    five_day_bonus = 0
    if trip_duration_days == 5 and 180 <= miles_per_day <= 220 and receipts_per_day < 100:
        five_day_bonus = 200  # Kevin's sweet spot combo
    
    total = base_amount + mileage_amount + receipt_amount + five_day_bonus
    
    # Vacation penalty
    if trip_duration_days >= 8:
        total *= 0.8
    
    return round(total, 2)

def variant_11_weighted_avg(trip_duration_days, miles_traveled, total_receipts_amount):
    """Weighted average of multiple simple models"""
    
    # Model 1: Duration focused
    model1 = trip_duration_days * 200 + miles_traveled * 0.3 + total_receipts_amount * 0.2
    
    # Model 2: Mileage focused  
    model2 = trip_duration_days * 100 + miles_traveled * 0.8 + total_receipts_amount * 0.1
    
    # Model 3: Receipt focused
    model3 = trip_duration_days * 150 + miles_traveled * 0.2 + total_receipts_amount * 0.6
    
    # Model 4: Inverse relationship
    model4 = (800 / trip_duration_days + 80) * trip_duration_days + miles_traveled * 0.4
    
    # Weighted combination
    total = (
        model1 * 0.3 +
        model2 * 0.2 +
        model3 * 0.2 +
        model4 * 0.3
    )
    
    return round(total, 2)

def ensemble_algorithm_v1(trip_duration_days, miles_traveled, total_receipts_amount):
    """
    Ensemble Algorithm V1 - Weighted combination of top 3 performers
    
    This is attempt #14 - ensemble approach combining best variants
    
    Components:
    - 60% Current Best (moderate penalties) - Score 16,922
    - 25% Business Rules (interview insights) - Score 41,398  
    - 15% Weighted Average (multi-model) - Score 42,147, 1 exact match
    
    Strategy: Leverage the stability of current best while incorporating
    the exact match capability of weighted average and business insights
    """
    
    # Get predictions from each component
    pred_current = variant_01_current_best(trip_duration_days, miles_traveled, total_receipts_amount)
    pred_business = variant_05_business_rules(trip_duration_days, miles_traveled, total_receipts_amount)
    pred_weighted = variant_11_weighted_avg(trip_duration_days, miles_traveled, total_receipts_amount)
    
    # Weighted ensemble
    ensemble_result = (
        pred_current * 0.60 +
        pred_business * 0.25 +
        pred_weighted * 0.15
    )
    
    return round(ensemble_result, 2)

def ensemble_algorithm_v2(trip_duration_days, miles_traveled, total_receipts_amount):
    """
    Ensemble Algorithm V2 - Adaptive weighting based on trip characteristics
    
    This is attempt #15 - adaptive ensemble with context-aware weighting
    
    Strategy: Use different algorithm weights based on trip characteristics
    to leverage each algorithm's strengths in different scenarios
    """
    
    miles_per_day = miles_traveled / trip_duration_days
    receipts_per_day = total_receipts_amount / trip_duration_days
    
    # Get predictions from each component
    pred_current = variant_01_current_best(trip_duration_days, miles_traveled, total_receipts_amount)
    pred_business = variant_05_business_rules(trip_duration_days, miles_traveled, total_receipts_amount)
    pred_weighted = variant_11_weighted_avg(trip_duration_days, miles_traveled, total_receipts_amount)
    
    # Adaptive weighting based on trip characteristics
    if trip_duration_days <= 3:
        # Short trips: favor current best (handles caps well)
        weights = [0.70, 0.20, 0.10]
    elif trip_duration_days >= 10:
        # Long trips: favor business rules (strong vacation penalties)
        weights = [0.40, 0.50, 0.10]
    elif 180 <= miles_per_day <= 220:
        # Efficiency sweet spot: favor business rules (Kevin's insights)
        weights = [0.50, 0.40, 0.10]
    elif receipts_per_day > 200:
        # High spending: favor current best (good fraud prevention)
        weights = [0.60, 0.25, 0.15]
    else:
        # Default case: balanced weighting
        weights = [0.55, 0.30, 0.15]
    
    # Apply adaptive weights
    ensemble_result = (
        pred_current * weights[0] +
        pred_business * weights[1] +
        pred_weighted * weights[2]
    )
    
    return round(ensemble_result, 2)

def ensemble_algorithm_v3(trip_duration_days, miles_traveled, total_receipts_amount):
    """
    Ensemble Algorithm V3 - Median-based robust ensemble
    
    This is attempt #16 - robust ensemble using median instead of weighted average
    
    Strategy: Use median of top 3 algorithms to be robust against outlier predictions
    """
    
    # Get predictions from each component
    pred_current = variant_01_current_best(trip_duration_days, miles_traveled, total_receipts_amount)
    pred_business = variant_05_business_rules(trip_duration_days, miles_traveled, total_receipts_amount)
    pred_weighted = variant_11_weighted_avg(trip_duration_days, miles_traveled, total_receipts_amount)
    
    # Use median for robustness
    predictions = [pred_current, pred_business, pred_weighted]
    predictions.sort()
    median_result = predictions[1]  # Middle value
    
    return round(median_result, 2)

def calculate_reimbursement(trip_duration_days, miles_traveled, total_receipts_amount):
    """Main function - currently using ensemble v2 (adaptive weighting)"""
    return ensemble_algorithm_v2(trip_duration_days, miles_traveled, total_receipts_amount)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 ensemble_algorithm.py <trip_duration_days> <miles_traveled> <total_receipts_amount>")
        sys.exit(1)
    
    trip_duration_days = int(sys.argv[1])
    miles_traveled = float(sys.argv[2])
    total_receipts_amount = float(sys.argv[3])
    
    result = calculate_reimbursement(trip_duration_days, miles_traveled, total_receipts_amount)
    print(result) 