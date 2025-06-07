#!/usr/bin/env python3

import json
from calculate_reimbursement import calculate_reimbursement

def test_micro_adjustments():
    """Test micro-adjustments to base rates and components based on closest case analysis"""
    
    with open('public_cases.json', 'r') as f:
        data = json.load(f)
    
    # Get the 5 closest cases for focused testing
    closest_cases = []
    for i, case in enumerate(data):
        duration = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        expected = case['expected_output']
        
        predicted = calculate_reimbursement(duration, miles, receipts)
        error = abs(predicted - expected)
        
        closest_cases.append({
            'case_id': i + 1,
            'duration': duration,
            'miles': miles,
            'receipts': receipts,
            'expected': expected,
            'predicted': predicted,
            'error': error
        })
    
    closest_cases.sort(key=lambda x: x['error'])
    top_5 = closest_cases[:5]
    
    print("🔧 MICRO-TUNING ALGORITHM")
    print("=" * 60)
    print("Testing systematic adjustments on 5 closest cases:")
    print()
    
    # Test different base rate adjustments
    base_rate_adjustments = [
        # (1-day, 2-day, 3-day, 4-day, 5-day, 6-day, 7-day, 8+day)
        (140, 110, 100, 100, 100, 95, 95, 90),  # Current
        (138, 108, 100, 100, 100, 95, 95, 90),  # Reduce 1-2 day rates
        (142, 112, 100, 100, 100, 95, 95, 90),  # Increase 1-2 day rates
        (140, 110, 100.5, 100, 100, 95, 95, 90),  # Micro-adjust 3-day
        (140, 110, 99.5, 100, 100, 95, 95, 90),   # Micro-adjust 3-day down
    ]
    
    # Test different mileage rate adjustments
    mileage_rate_adjustments = [
        (0.65, 0.45, 0.25),  # Current
        (0.64, 0.45, 0.25),  # Reduce first tier
        (0.66, 0.45, 0.25),  # Increase first tier
        (0.65, 0.44, 0.25),  # Reduce second tier
        (0.65, 0.46, 0.25),  # Increase second tier
    ]
    
    # Test different receipt rate adjustments
    receipt_rate_adjustments = [
        (0.8, 0.6, 0.4),   # Current
        (0.79, 0.6, 0.4),  # Reduce first tier
        (0.81, 0.6, 0.4),  # Increase first tier
        (0.8, 0.59, 0.4),  # Reduce second tier
        (0.8, 0.61, 0.4),  # Increase second tier
    ]
    
    best_improvement = 0
    best_config = None
    
    for base_rates in base_rate_adjustments:
        for mileage_rates in mileage_rate_adjustments:
            for receipt_rates in receipt_rate_adjustments:
                total_error = 0
                
                for case in top_5:
                    predicted = calculate_reimbursement_with_params(
                        case['duration'], case['miles'], case['receipts'],
                        base_rates, mileage_rates, receipt_rates
                    )
                    error = abs(predicted - case['expected'])
                    total_error += error
                
                avg_error = total_error / len(top_5)
                current_avg = sum(c['error'] for c in top_5) / len(top_5)
                improvement = current_avg - avg_error
                
                if improvement > best_improvement:
                    best_improvement = improvement
                    best_config = {
                        'base_rates': base_rates,
                        'mileage_rates': mileage_rates,
                        'receipt_rates': receipt_rates,
                        'avg_error': avg_error,
                        'improvement': improvement
                    }
    
    print(f"Current average error on top 5 cases: ${sum(c['error'] for c in top_5) / len(top_5):.2f}")
    
    if best_config:
        print(f"\n🎯 BEST MICRO-ADJUSTMENT FOUND:")
        print(f"  Base rates: {best_config['base_rates']}")
        print(f"  Mileage rates: {best_config['mileage_rates']}")
        print(f"  Receipt rates: {best_config['receipt_rates']}")
        print(f"  New average error: ${best_config['avg_error']:.2f}")
        print(f"  Improvement: ${best_config['improvement']:.2f}")
        
        return best_config
    else:
        print("No improvement found with micro-adjustments")
        return None

def calculate_reimbursement_with_params(trip_duration_days, miles_traveled, total_receipts_amount, 
                                      base_rates, mileage_rates, receipt_rates):
    """Calculate reimbursement with custom parameters for testing"""
    
    # Base per-day rates
    if trip_duration_days == 1:
        base_per_day = base_rates[0]
    elif trip_duration_days == 2:
        base_per_day = base_rates[1]
    elif trip_duration_days == 3:
        base_per_day = base_rates[2]
    elif trip_duration_days == 4:
        base_per_day = base_rates[3]
    elif trip_duration_days == 5:
        base_per_day = base_rates[4]
    elif trip_duration_days == 6:
        base_per_day = base_rates[5]
    elif trip_duration_days == 7:
        base_per_day = base_rates[6]
    else:
        base_per_day = base_rates[7]
    
    base_amount = base_per_day * trip_duration_days
    
    # Mileage calculation
    miles_per_day = miles_traveled / trip_duration_days
    
    if miles_traveled <= 500:
        mileage_amount = miles_traveled * mileage_rates[0]
    elif miles_traveled <= 1000:
        mileage_amount = 500 * mileage_rates[0] + (miles_traveled - 500) * mileage_rates[1]
    else:
        mileage_amount = 500 * mileage_rates[0] + 500 * mileage_rates[1] + (miles_traveled - 1000) * mileage_rates[2]
    
    # Efficiency bonus
    efficiency_bonus = 0
    if 180 <= miles_per_day <= 220:
        efficiency_bonus = trip_duration_days * 40
    elif miles_per_day > 300:
        efficiency_bonus = -trip_duration_days * 20
    
    # Receipt calculation
    receipts_per_day = total_receipts_amount / trip_duration_days
    
    if total_receipts_amount <= 200:
        receipt_amount = total_receipts_amount * receipt_rates[0]
    elif total_receipts_amount <= 500:
        receipt_amount = 200 * receipt_rates[0] + (total_receipts_amount - 200) * receipt_rates[1]
    else:
        receipt_amount = 200 * receipt_rates[0] + 300 * receipt_rates[1] + (total_receipts_amount - 500) * receipt_rates[2]
    
    # Context-aware penalties (simplified for testing)
    receipt_penalty = 0
    vacation_penalty = 0
    
    if trip_duration_days <= 2 and total_receipts_amount > 2000 and miles_traveled < 200:
        receipt_penalty = receipt_amount * 0.4
    elif 3 <= trip_duration_days <= 6 and total_receipts_amount > 2200 and receipts_per_day > 400:
        receipt_penalty = receipt_amount * 0.2
    
    if trip_duration_days >= 8 and receipts_per_day > 150:
        vacation_penalty = base_amount * 0.15
    
    # Calculate subtotal
    subtotal = base_amount + mileage_amount + efficiency_bonus + receipt_amount - receipt_penalty - vacation_penalty
    
    # Apply caps
    caps = {1: 1500, 2: 1700, 3: 1600, 4: 1750, 5: 1850, 6: 1900, 7: 1950, 8: 2000}
    
    if trip_duration_days <= 8:
        cap = caps[trip_duration_days]
    else:
        cap = 2000 + (trip_duration_days - 8) * 50
    
    total = min(subtotal, cap)
    
    # Fraud prevention
    if (trip_duration_days == 1 and total_receipts_amount > 2500 and miles_traveled < 100):
        total *= 0.3
    elif (trip_duration_days == 4 and total_receipts_amount > 2400 and miles_traveled < 50):
        total *= 0.2
    elif (trip_duration_days >= 12 and receipts_per_day > 200):
        total *= 0.8
    
    return round(total, 2)

def test_rounding_strategies():
    """Test different rounding strategies on closest cases"""
    
    with open('public_cases.json', 'r') as f:
        data = json.load(f)
    
    # Get closest cases
    closest_cases = []
    for i, case in enumerate(data):
        duration = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        expected = case['expected_output']
        
        predicted = calculate_reimbursement(duration, miles, receipts)
        error = abs(predicted - expected)
        
        if error < 5.0:  # Focus on cases within $5
            closest_cases.append({
                'case_id': i + 1,
                'duration': duration,
                'miles': miles,
                'receipts': receipts,
                'expected': expected,
                'predicted': predicted,
                'error': error
            })
    
    print(f"\n🔄 TESTING ROUNDING STRATEGIES")
    print("=" * 60)
    print(f"Testing on {len(closest_cases)} cases within $5 error:")
    
    # Test different rounding strategies
    import math
    
    rounding_strategies = [
        ('Standard round(x, 2)', lambda x: round(x, 2)),
        ('Floor to cent', lambda x: math.floor(x * 100) / 100),
        ('Ceil to cent', lambda x: math.ceil(x * 100) / 100),
        ('Banker\'s rounding', lambda x: round(x + 0.0001, 2)),  # Slight bias
        ('Round to nearest 5¢', lambda x: round(x * 20) / 20),
        ('Round to nearest 10¢', lambda x: round(x * 10) / 10),
    ]
    
    for strategy_name, rounding_func in rounding_strategies:
        total_error = 0
        exact_matches = 0
        
        for case in closest_cases:
            # Get the raw calculation (before rounding)
            raw_prediction = calculate_reimbursement_raw(case['duration'], case['miles'], case['receipts'])
            rounded_prediction = rounding_func(raw_prediction)
            
            error = abs(rounded_prediction - case['expected'])
            total_error += error
            
            if error < 0.01:
                exact_matches += 1
        
        avg_error = total_error / len(closest_cases)
        print(f"  {strategy_name:20s}: Avg error ${avg_error:.3f}, Exact matches: {exact_matches}")

def calculate_reimbursement_raw(trip_duration_days, miles_traveled, total_receipts_amount):
    """Calculate reimbursement without final rounding for testing"""
    
    # Use current algorithm but return raw value
    if trip_duration_days == 1:
        base_per_day = 140
    elif trip_duration_days == 2:
        base_per_day = 110
    elif trip_duration_days <= 5:
        base_per_day = 100
    elif trip_duration_days <= 7:
        base_per_day = 95
    else:
        base_per_day = 90
    
    base_amount = base_per_day * trip_duration_days
    
    miles_per_day = miles_traveled / trip_duration_days
    
    if miles_traveled <= 500:
        mileage_amount = miles_traveled * 0.65
    elif miles_traveled <= 1000:
        mileage_amount = 500 * 0.65 + (miles_traveled - 500) * 0.45
    else:
        mileage_amount = 500 * 0.65 + 500 * 0.45 + (miles_traveled - 1000) * 0.25
    
    efficiency_bonus = 0
    if 180 <= miles_per_day <= 220:
        efficiency_bonus = trip_duration_days * 40
    elif miles_per_day > 300:
        efficiency_bonus = -trip_duration_days * 20
    
    receipts_per_day = total_receipts_amount / trip_duration_days
    
    if total_receipts_amount <= 200:
        receipt_amount = total_receipts_amount * 0.8
    elif total_receipts_amount <= 500:
        receipt_amount = 200 * 0.8 + (total_receipts_amount - 200) * 0.6
    else:
        receipt_amount = 200 * 0.8 + 300 * 0.6 + (total_receipts_amount - 500) * 0.4
    
    receipt_penalty = 0
    vacation_penalty = 0
    
    if trip_duration_days <= 2 and total_receipts_amount > 2000 and miles_traveled < 200:
        receipt_penalty = receipt_amount * 0.4
    elif 3 <= trip_duration_days <= 6 and total_receipts_amount > 2200 and receipts_per_day > 400:
        receipt_penalty = receipt_amount * 0.2
    
    if trip_duration_days >= 8 and receipts_per_day > 150:
        vacation_penalty = base_amount * 0.15
    
    subtotal = base_amount + mileage_amount + efficiency_bonus + receipt_amount - receipt_penalty - vacation_penalty
    
    caps = {1: 1500, 2: 1700, 3: 1600, 4: 1750, 5: 1850, 6: 1900, 7: 1950, 8: 2000}
    
    if trip_duration_days <= 8:
        cap = caps[trip_duration_days]
    else:
        cap = 2000 + (trip_duration_days - 8) * 50
    
    total = min(subtotal, cap)
    
    if (trip_duration_days == 1 and total_receipts_amount > 2500 and miles_traveled < 100):
        total *= 0.3
    elif (trip_duration_days == 4 and total_receipts_amount > 2400 and miles_traveled < 50):
        total *= 0.2
    elif (trip_duration_days >= 12 and receipts_per_day > 200):
        total *= 0.8
    
    return total  # Return without rounding

def test_systematic_bias_correction():
    """Test systematic bias correction based on prediction ratio analysis"""
    
    with open('public_cases.json', 'r') as f:
        data = json.load(f)
    
    print(f"\n📊 SYSTEMATIC BIAS CORRECTION")
    print("=" * 60)
    
    # Calculate current prediction ratios
    ratios = []
    for case in data:
        duration = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        expected = case['expected_output']
        
        predicted = calculate_reimbursement(duration, miles, receipts)
        if expected > 0:
            ratio = predicted / expected
            ratios.append(ratio)
    
    avg_ratio = sum(ratios) / len(ratios)
    print(f"Current average prediction ratio: {avg_ratio:.6f}")
    
    # Test bias correction multipliers
    correction_factors = [0.995, 0.996, 0.997, 0.998, 0.999, 1.001, 1.002, 1.003, 1.004, 1.005]
    
    best_improvement = 0
    best_factor = 1.0
    
    for factor in correction_factors:
        total_error = 0
        exact_matches = 0
        
        for case in data:
            duration = case['input']['trip_duration_days']
            miles = case['input']['miles_traveled']
            receipts = case['input']['total_receipts_amount']
            expected = case['expected_output']
            
            raw_predicted = calculate_reimbursement(duration, miles, receipts)
            corrected_predicted = round(raw_predicted * factor, 2)
            
            error = abs(corrected_predicted - expected)
            total_error += error
            
            if error < 0.01:
                exact_matches += 1
        
        avg_error = total_error / len(data)
        
        # Calculate improvement
        current_total_error = sum(abs(calculate_reimbursement(case['input']['trip_duration_days'], 
                                                            case['input']['miles_traveled'], 
                                                            case['input']['total_receipts_amount']) - 
                                     case['expected_output']) for case in data)
        current_avg_error = current_total_error / len(data)
        improvement = current_avg_error - avg_error
        
        print(f"  Factor {factor:.3f}: Avg error ${avg_error:.2f}, Exact matches: {exact_matches}, Improvement: ${improvement:.2f}")
        
        if improvement > best_improvement:
            best_improvement = improvement
            best_factor = factor
    
    print(f"\n🎯 Best correction factor: {best_factor:.3f} (improvement: ${best_improvement:.2f})")
    return best_factor

if __name__ == "__main__":
    best_config = test_micro_adjustments()
    test_rounding_strategies()
    best_factor = test_systematic_bias_correction() 