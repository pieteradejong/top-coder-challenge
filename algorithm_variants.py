#!/usr/bin/env python3

import json
import datetime
import math
from typing import Dict, List, Tuple, Callable

def load_test_data():
    """Load test cases for evaluation"""
    with open('public_cases.json', 'r') as f:
        return json.load(f)

def evaluate_algorithm(algorithm_func: Callable, test_data: List[Dict]) -> Dict:
    """Evaluate an algorithm and return performance metrics"""
    total_error = 0
    exact_matches = 0
    close_matches = 0
    errors = []
    
    for case in test_data:
        duration = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        expected = case['expected_output']
        
        try:
            predicted = algorithm_func(duration, miles, receipts)
            error = abs(predicted - expected)
            
            total_error += error
            errors.append(error)
            
            if error < 0.01:
                exact_matches += 1
            if error < 1.0:
                close_matches += 1
                
        except Exception as e:
            print(f"Error in case {case}: {e}")
            errors.append(1000)  # Large penalty for errors
            total_error += 1000
    
    avg_error = total_error / len(test_data)
    max_error = max(errors) if errors else 0
    score = avg_error * 100 + (len(test_data) - exact_matches) * 0.1
    
    return {
        'avg_error': round(avg_error, 2),
        'max_error': round(max_error, 2),
        'exact_matches': exact_matches,
        'close_matches': close_matches,
        'score': round(score, 2),
        'total_cases': len(test_data)
    }

# ============================================================================
# ALGORITHM VARIANT 1: CURRENT BEST (Baseline)
# ============================================================================

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

# ============================================================================
# ALGORITHM VARIANT 2: PURE INVERSE RELATIONSHIP
# ============================================================================

def variant_02_pure_inverse(trip_duration_days, miles_traveled, total_receipts_amount):
    """Pure mathematical inverse relationship approach"""
    
    # Strong inverse relationship: per_day_rate = 814.88 / duration + 79.20
    per_day_rate = 814.88 / trip_duration_days + 79.20
    base_amount = per_day_rate * trip_duration_days
    
    # Simple mileage: flat rate
    mileage_amount = miles_traveled * 0.55
    
    # Simple receipts: flat rate
    receipt_amount = total_receipts_amount * 0.4
    
    total = base_amount + mileage_amount + receipt_amount
    
    # Simple cap
    total = min(total, 2500)
    
    return round(total, 2)

# ============================================================================
# ALGORITHM VARIANT 3: MACHINE LEARNING INSPIRED
# ============================================================================

def variant_03_ml_inspired(trip_duration_days, miles_traveled, total_receipts_amount):
    """Feature engineering approach with polynomial terms"""
    
    # Feature engineering
    miles_per_day = miles_traveled / trip_duration_days
    receipts_per_day = total_receipts_amount / trip_duration_days
    efficiency_ratio = miles_traveled / max(total_receipts_amount, 1)
    
    # Polynomial features
    duration_sq = trip_duration_days ** 2
    miles_sq = miles_traveled ** 2
    receipts_sq = total_receipts_amount ** 2
    
    # Learned coefficients (approximated from patterns)
    total = (
        100 * trip_duration_days +
        0.5 * miles_traveled +
        0.3 * total_receipts_amount +
        -2 * duration_sq +
        0.0001 * miles_sq +
        -0.00005 * receipts_sq +
        50 * efficiency_ratio +
        -10 * abs(miles_per_day - 200)
    )
    
    return round(max(total, 0), 2)

# ============================================================================
# ALGORITHM VARIANT 4: EXTREME SIMPLICITY
# ============================================================================

def variant_04_extreme_simple(trip_duration_days, miles_traveled, total_receipts_amount):
    """Extremely simple linear model"""
    
    total = (
        trip_duration_days * 120 +
        miles_traveled * 0.6 +
        total_receipts_amount * 0.5
    )
    
    return round(total, 2)

# ============================================================================
# ALGORITHM VARIANT 5: BUSINESS RULES HEAVY
# ============================================================================

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

# ============================================================================
# ALGORITHM VARIANT 6: STATISTICAL CLUSTERING
# ============================================================================

def variant_06_clustering(trip_duration_days, miles_traveled, total_receipts_amount):
    """Approach based on clustering similar trips"""
    
    miles_per_day = miles_traveled / trip_duration_days
    receipts_per_day = total_receipts_amount / trip_duration_days
    
    # Cluster 1: Short efficient trips
    if trip_duration_days <= 3 and miles_per_day > 150:
        base_rate = 400
        mileage_rate = 0.7
        receipt_rate = 0.5
    
    # Cluster 2: Medium balanced trips
    elif 4 <= trip_duration_days <= 7 and 100 <= miles_per_day <= 250:
        base_rate = 250
        mileage_rate = 0.6
        receipt_rate = 0.6
    
    # Cluster 3: Long trips
    elif trip_duration_days >= 8:
        base_rate = 150
        mileage_rate = 0.5
        receipt_rate = 0.4
    
    # Cluster 4: High spending trips
    elif receipts_per_day > 200:
        base_rate = 200
        mileage_rate = 0.4
        receipt_rate = 0.3
    
    # Default cluster
    else:
        base_rate = 300
        mileage_rate = 0.6
        receipt_rate = 0.5
    
    total = (
        base_rate * trip_duration_days +
        miles_traveled * mileage_rate +
        total_receipts_amount * receipt_rate
    )
    
    return round(total, 2)

# ============================================================================
# ALGORITHM VARIANT 7: EXPONENTIAL DECAY
# ============================================================================

def variant_07_exponential(trip_duration_days, miles_traveled, total_receipts_amount):
    """Exponential decay model for diminishing returns"""
    
    # Exponential decay for duration
    duration_factor = 1000 * math.exp(-0.2 * trip_duration_days)
    base_amount = duration_factor * trip_duration_days
    
    # Logarithmic mileage
    mileage_amount = 100 * math.log(miles_traveled + 1)
    
    # Square root receipts (diminishing returns)
    receipt_amount = 50 * math.sqrt(total_receipts_amount)
    
    total = base_amount + mileage_amount + receipt_amount
    
    return round(total, 2)

# ============================================================================
# ALGORITHM VARIANT 8: RATIO-BASED
# ============================================================================

def variant_08_ratio_based(trip_duration_days, miles_traveled, total_receipts_amount):
    """Focus on ratios and efficiency metrics"""
    
    miles_per_day = miles_traveled / trip_duration_days
    receipts_per_day = total_receipts_amount / trip_duration_days
    efficiency_ratio = miles_traveled / max(total_receipts_amount, 1)
    
    # Base amount from efficiency ratio
    if efficiency_ratio > 2:
        base_multiplier = 1.5  # High efficiency
    elif efficiency_ratio > 1:
        base_multiplier = 1.2
    elif efficiency_ratio > 0.5:
        base_multiplier = 1.0
    else:
        base_multiplier = 0.7  # Low efficiency
    
    base_amount = 150 * trip_duration_days * base_multiplier
    
    # Mileage based on per-day efficiency
    if miles_per_day > 200:
        mileage_amount = miles_traveled * 0.7
    elif miles_per_day > 100:
        mileage_amount = miles_traveled * 0.6
    else:
        mileage_amount = miles_traveled * 0.4
    
    # Receipts inversely related to efficiency
    receipt_multiplier = max(0.2, 1 - efficiency_ratio * 0.3)
    receipt_amount = total_receipts_amount * receipt_multiplier
    
    total = base_amount + mileage_amount + receipt_amount
    
    return round(total, 2)

# ============================================================================
# ALGORITHM VARIANT 9: PIECEWISE LINEAR
# ============================================================================

def variant_09_piecewise(trip_duration_days, miles_traveled, total_receipts_amount):
    """Piecewise linear functions for each component"""
    
    # Piecewise duration
    if trip_duration_days <= 2:
        duration_rate = 400
    elif trip_duration_days <= 5:
        duration_rate = 300 - (trip_duration_days - 2) * 50
    elif trip_duration_days <= 10:
        duration_rate = 150 - (trip_duration_days - 5) * 10
    else:
        duration_rate = 100
    
    base_amount = duration_rate * trip_duration_days
    
    # Piecewise mileage
    if miles_traveled <= 100:
        mileage_amount = miles_traveled * 0.8
    elif miles_traveled <= 500:
        mileage_amount = 100 * 0.8 + (miles_traveled - 100) * 0.6
    elif miles_traveled <= 1000:
        mileage_amount = 100 * 0.8 + 400 * 0.6 + (miles_traveled - 500) * 0.4
    else:
        mileage_amount = 100 * 0.8 + 400 * 0.6 + 500 * 0.4 + (miles_traveled - 1000) * 0.2
    
    # Piecewise receipts
    if total_receipts_amount <= 100:
        receipt_amount = total_receipts_amount * 0.9
    elif total_receipts_amount <= 500:
        receipt_amount = 100 * 0.9 + (total_receipts_amount - 100) * 0.7
    elif total_receipts_amount <= 1500:
        receipt_amount = 100 * 0.9 + 400 * 0.7 + (total_receipts_amount - 500) * 0.5
    else:
        receipt_amount = 100 * 0.9 + 400 * 0.7 + 1000 * 0.5 + (total_receipts_amount - 1500) * 0.2
    
    total = base_amount + mileage_amount + receipt_amount
    
    return round(total, 2)

# ============================================================================
# ALGORITHM VARIANT 10: THRESHOLD-BASED
# ============================================================================

def variant_10_thresholds(trip_duration_days, miles_traveled, total_receipts_amount):
    """Hard thresholds and step functions"""
    
    miles_per_day = miles_traveled / trip_duration_days
    receipts_per_day = total_receipts_amount / trip_duration_days
    
    # Base amount with hard thresholds
    if trip_duration_days == 1:
        base_amount = 600
    elif trip_duration_days <= 3:
        base_amount = 400 * trip_duration_days
    elif trip_duration_days <= 7:
        base_amount = 300 * trip_duration_days
    else:
        base_amount = 200 * trip_duration_days
    
    # Mileage with efficiency thresholds
    if miles_per_day >= 200:
        mileage_amount = miles_traveled * 0.8
    elif miles_per_day >= 100:
        mileage_amount = miles_traveled * 0.6
    elif miles_per_day >= 50:
        mileage_amount = miles_traveled * 0.4
    else:
        mileage_amount = miles_traveled * 0.2
    
    # Receipt thresholds
    if receipts_per_day >= 300:
        receipt_amount = total_receipts_amount * 0.2
    elif receipts_per_day >= 150:
        receipt_amount = total_receipts_amount * 0.5
    elif receipts_per_day >= 75:
        receipt_amount = total_receipts_amount * 0.7
    else:
        receipt_amount = total_receipts_amount * 0.9
    
    total = base_amount + mileage_amount + receipt_amount
    
    # Hard caps
    if trip_duration_days <= 3:
        total = min(total, 2000)
    elif trip_duration_days <= 7:
        total = min(total, 2500)
    else:
        total = min(total, 3000)
    
    return round(total, 2)

# ============================================================================
# ALGORITHM VARIANT 11: WEIGHTED AVERAGE
# ============================================================================

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

# ============================================================================
# ALGORITHM VARIANT 12: OUTLIER ROBUST
# ============================================================================

def variant_12_outlier_robust(trip_duration_days, miles_traveled, total_receipts_amount):
    """Robust to outliers with median-based approach"""
    
    # Use median-like logic instead of means
    miles_per_day = miles_traveled / trip_duration_days
    receipts_per_day = total_receipts_amount / trip_duration_days
    
    # Robust base calculation
    if trip_duration_days <= 2:
        base_per_day = 350
    elif trip_duration_days <= 5:
        base_per_day = 250
    elif trip_duration_days <= 10:
        base_per_day = 180
    else:
        base_per_day = 120
    
    base_amount = base_per_day * trip_duration_days
    
    # Robust mileage (capped to prevent outliers)
    mileage_per_day_capped = min(miles_per_day, 400)  # Cap extreme values
    mileage_amount = mileage_per_day_capped * trip_duration_days * 0.6
    
    # Robust receipts (capped)
    receipts_per_day_capped = min(receipts_per_day, 300)  # Cap extreme values
    receipt_amount = receipts_per_day_capped * trip_duration_days * 0.5
    
    total = base_amount + mileage_amount + receipt_amount
    
    # Robust final cap
    reasonable_max = trip_duration_days * 500  # Reasonable maximum per day
    total = min(total, reasonable_max)
    
    return round(total, 2)

# ============================================================================
# TESTING AND DOCUMENTATION SYSTEM
# ============================================================================

def run_all_variants():
    """Run all algorithm variants and document results"""
    
    print("🧪 COMPREHENSIVE ALGORITHM VARIANT TESTING")
    print("=" * 80)
    
    # Load test data
    test_data = load_test_data()
    
    # Define all variants
    variants = [
        ("01_current_best", "Current Best (Moderate Penalties)", variant_01_current_best),
        ("02_pure_inverse", "Pure Inverse Relationship", variant_02_pure_inverse),
        ("03_ml_inspired", "ML Feature Engineering", variant_03_ml_inspired),
        ("04_extreme_simple", "Extreme Simplicity", variant_04_extreme_simple),
        ("05_business_rules", "Heavy Business Rules", variant_05_business_rules),
        ("06_clustering", "Statistical Clustering", variant_06_clustering),
        ("07_exponential", "Exponential Decay", variant_07_exponential),
        ("08_ratio_based", "Ratio & Efficiency Focus", variant_08_ratio_based),
        ("09_piecewise", "Piecewise Linear", variant_09_piecewise),
        ("10_thresholds", "Hard Thresholds", variant_10_thresholds),
        ("11_weighted_avg", "Weighted Average Models", variant_11_weighted_avg),
        ("12_outlier_robust", "Outlier Robust", variant_12_outlier_robust),
    ]
    
    # Test all variants
    results = []
    
    for variant_id, description, algorithm_func in variants:
        print(f"\n🔬 Testing {variant_id}: {description}")
        
        try:
            performance = evaluate_algorithm(algorithm_func, test_data)
            
            result = {
                'variant_id': variant_id,
                'description': description,
                'timestamp': datetime.datetime.now().isoformat(),
                'performance': performance,
                'algorithm_source': algorithm_func.__name__
            }
            
            results.append(result)
            
            print(f"   Score: {performance['score']:,.2f}")
            print(f"   Avg Error: ${performance['avg_error']}")
            print(f"   Exact Matches: {performance['exact_matches']}")
            print(f"   Close Matches: {performance['close_matches']}")
            
        except Exception as e:
            print(f"   ❌ FAILED: {e}")
            results.append({
                'variant_id': variant_id,
                'description': description,
                'timestamp': datetime.datetime.now().isoformat(),
                'performance': {'error': str(e)},
                'algorithm_source': algorithm_func.__name__
            })
    
    # Save results
    with open('variant_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # Generate summary report
    generate_variant_report(results)
    
    return results

def generate_variant_report(results):
    """Generate a comprehensive report of all variants"""
    
    print(f"\n📊 VARIANT PERFORMANCE SUMMARY")
    print("=" * 80)
    
    # Filter successful results
    successful_results = [r for r in results if 'error' not in r['performance']]
    
    if not successful_results:
        print("❌ No successful variants to analyze")
        return
    
    # Sort by score (lower is better)
    successful_results.sort(key=lambda x: x['performance']['score'])
    
    print(f"{'Rank':<4} {'Variant':<15} {'Score':<10} {'Avg Error':<10} {'Exact':<6} {'Close':<6} {'Description'}")
    print("-" * 80)
    
    for i, result in enumerate(successful_results):
        perf = result['performance']
        rank = i + 1
        variant = result['variant_id']
        score = f"{perf['score']:,.0f}"
        avg_error = f"${perf['avg_error']}"
        exact = perf['exact_matches']
        close = perf['close_matches']
        desc = result['description'][:25] + "..." if len(result['description']) > 25 else result['description']
        
        print(f"{rank:<4} {variant:<15} {score:<10} {avg_error:<10} {exact:<6} {close:<6} {desc}")
    
    # Best performers analysis
    best_score = successful_results[0]
    best_exact = max(successful_results, key=lambda x: x['performance']['exact_matches'])
    best_avg_error = min(successful_results, key=lambda x: x['performance']['avg_error'])
    
    print(f"\n🏆 BEST PERFORMERS:")
    print(f"  Best Score: {best_score['variant_id']} ({best_score['performance']['score']:,.0f})")
    print(f"  Most Exact: {best_exact['variant_id']} ({best_exact['performance']['exact_matches']} exact)")
    print(f"  Lowest Error: {best_avg_error['variant_id']} (${best_avg_error['performance']['avg_error']})")
    
    # Save detailed report
    with open('variant_report.md', 'w') as f:
        f.write("# Algorithm Variant Testing Report\n\n")
        f.write(f"Generated: {datetime.datetime.now().isoformat()}\n\n")
        f.write("## Performance Summary\n\n")
        f.write("| Rank | Variant | Score | Avg Error | Exact | Close | Description |\n")
        f.write("|------|---------|-------|-----------|-------|-------|-------------|\n")
        
        for i, result in enumerate(successful_results):
            perf = result['performance']
            f.write(f"| {i+1} | {result['variant_id']} | {perf['score']:,.0f} | ${perf['avg_error']} | {perf['exact_matches']} | {perf['close_matches']} | {result['description']} |\n")
        
        f.write(f"\n## Best Performers\n\n")
        f.write(f"- **Best Score**: {best_score['variant_id']} ({best_score['performance']['score']:,.0f})\n")
        f.write(f"- **Most Exact Matches**: {best_exact['variant_id']} ({best_exact['performance']['exact_matches']} exact)\n")
        f.write(f"- **Lowest Average Error**: {best_avg_error['variant_id']} (${best_avg_error['performance']['avg_error']})\n")

if __name__ == "__main__":
    results = run_all_variants()
    print(f"\n✅ Testing complete! Results saved to variant_results.json and variant_report.md") 