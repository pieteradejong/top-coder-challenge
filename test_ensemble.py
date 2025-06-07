#!/usr/bin/env python3

import json
import datetime
from ensemble_algorithm import (
    ensemble_algorithm_v1, 
    ensemble_algorithm_v2, 
    ensemble_algorithm_v3,
    variant_01_current_best,
    variant_05_business_rules,
    variant_11_weighted_avg
)

def evaluate_algorithm(algorithm_func, test_data):
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
            errors.append(1000)
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

def test_all_ensemble_variants():
    """Test all ensemble variants and compare with base algorithms"""
    
    print("🎭 ENSEMBLE ALGORITHM TESTING")
    print("=" * 80)
    
    # Load test data
    with open('public_cases.json', 'r') as f:
        test_data = json.load(f)
    
    # Define algorithms to test
    algorithms = [
        ("Base: Current Best", variant_01_current_best),
        ("Base: Business Rules", variant_05_business_rules),
        ("Base: Weighted Average", variant_11_weighted_avg),
        ("Ensemble V1: Weighted", ensemble_algorithm_v1),
        ("Ensemble V2: Adaptive", ensemble_algorithm_v2),
        ("Ensemble V3: Median", ensemble_algorithm_v3),
    ]
    
    results = []
    
    for name, algorithm_func in algorithms:
        print(f"\n🔬 Testing {name}")
        
        try:
            performance = evaluate_algorithm(algorithm_func, test_data)
            
            result = {
                'name': name,
                'timestamp': datetime.datetime.now().isoformat(),
                'performance': performance,
                'algorithm_type': 'ensemble' if 'Ensemble' in name else 'base'
            }
            
            results.append(result)
            
            print(f"   Score: {performance['score']:,.2f}")
            print(f"   Avg Error: ${performance['avg_error']}")
            print(f"   Exact Matches: {performance['exact_matches']}")
            print(f"   Close Matches: {performance['close_matches']}")
            
        except Exception as e:
            print(f"   ❌ FAILED: {e}")
    
    # Generate comparison report
    generate_ensemble_report(results)
    
    # Save results
    with open('ensemble_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    return results

def generate_ensemble_report(results):
    """Generate comprehensive ensemble comparison report"""
    
    print(f"\n📊 ENSEMBLE PERFORMANCE COMPARISON")
    print("=" * 80)
    
    # Sort by score (lower is better)
    results.sort(key=lambda x: x['performance']['score'])
    
    print(f"{'Rank':<4} {'Algorithm':<25} {'Score':<10} {'Avg Error':<10} {'Exact':<6} {'Close':<6}")
    print("-" * 80)
    
    for i, result in enumerate(results):
        perf = result['performance']
        rank = i + 1
        name = result['name'][:24]
        score = f"{perf['score']:,.0f}"
        avg_error = f"${perf['avg_error']}"
        exact = perf['exact_matches']
        close = perf['close_matches']
        
        # Highlight ensemble methods
        marker = "🎭" if result['algorithm_type'] == 'ensemble' else "  "
        
        print(f"{rank:<4} {marker} {name:<23} {score:<10} {avg_error:<10} {exact:<6} {close:<6}")
    
    # Analysis
    best_overall = results[0]
    best_exact = max(results, key=lambda x: x['performance']['exact_matches'])
    
    ensemble_results = [r for r in results if r['algorithm_type'] == 'ensemble']
    base_results = [r for r in results if r['algorithm_type'] == 'base']
    
    print(f"\n🏆 PERFORMANCE ANALYSIS:")
    print(f"  Best Overall: {best_overall['name']} (Score: {best_overall['performance']['score']:,.0f})")
    print(f"  Most Exact: {best_exact['name']} ({best_exact['performance']['exact_matches']} exact)")
    
    if ensemble_results and base_results:
        best_ensemble = min(ensemble_results, key=lambda x: x['performance']['score'])
        best_base = min(base_results, key=lambda x: x['performance']['score'])
        
        improvement = best_base['performance']['score'] - best_ensemble['performance']['score']
        improvement_pct = (improvement / best_base['performance']['score']) * 100
        
        print(f"\n🎯 ENSEMBLE EFFECTIVENESS:")
        print(f"  Best Base Algorithm: {best_base['name']} (Score: {best_base['performance']['score']:,.0f})")
        print(f"  Best Ensemble: {best_ensemble['name']} (Score: {best_ensemble['performance']['score']:,.0f})")
        print(f"  Improvement: {improvement:+.0f} points ({improvement_pct:+.1f}%)")
        
        if improvement > 0:
            print("  ✅ Ensemble methods show improvement!")
        else:
            print("  ⚠️  Ensemble methods need refinement")

def analyze_ensemble_predictions():
    """Analyze how ensemble predictions differ from base algorithms"""
    
    print(f"\n🔍 ENSEMBLE PREDICTION ANALYSIS")
    print("=" * 60)
    
    # Load test data
    with open('public_cases.json', 'r') as f:
        test_data = json.load(f)
    
    # Sample a few cases for detailed analysis
    sample_cases = test_data[:10]
    
    print(f"{'Case':<4} {'Expected':<10} {'Current':<10} {'Business':<10} {'Weighted':<10} {'Ensemble':<10}")
    print("-" * 70)
    
    for i, case in enumerate(sample_cases):
        duration = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        expected = case['expected_output']
        
        pred_current = variant_01_current_best(duration, miles, receipts)
        pred_business = variant_05_business_rules(duration, miles, receipts)
        pred_weighted = variant_11_weighted_avg(duration, miles, receipts)
        pred_ensemble = ensemble_algorithm_v2(duration, miles, receipts)
        
        print(f"{i+1:<4} ${expected:<9.2f} ${pred_current:<9.2f} ${pred_business:<9.2f} ${pred_weighted:<9.2f} ${pred_ensemble:<9.2f}")

def find_best_ensemble_weights():
    """Systematically test different ensemble weights"""
    
    print(f"\n🎯 ENSEMBLE WEIGHT OPTIMIZATION")
    print("=" * 50)
    
    # Load test data
    with open('public_cases.json', 'r') as f:
        test_data = json.load(f)
    
    best_score = float('inf')
    best_weights = None
    
    # Test different weight combinations
    weight_combinations = [
        (0.7, 0.2, 0.1),  # Current best heavy
        (0.6, 0.3, 0.1),  # Balanced
        (0.5, 0.4, 0.1),  # Business rules heavy
        (0.4, 0.4, 0.2),  # Equal current/business
        (0.3, 0.3, 0.4),  # Weighted average heavy
        (0.8, 0.1, 0.1),  # Very current best heavy
        (0.2, 0.6, 0.2),  # Very business rules heavy
    ]
    
    print(f"{'Weights (C/B/W)':<15} {'Score':<10} {'Avg Error':<10} {'Exact':<6} {'Close':<6}")
    print("-" * 55)
    
    for w1, w2, w3 in weight_combinations:
        total_error = 0
        exact_matches = 0
        close_matches = 0
        
        for case in test_data:
            duration = case['input']['trip_duration_days']
            miles = case['input']['miles_traveled']
            receipts = case['input']['total_receipts_amount']
            expected = case['expected_output']
            
            pred_current = variant_01_current_best(duration, miles, receipts)
            pred_business = variant_05_business_rules(duration, miles, receipts)
            pred_weighted = variant_11_weighted_avg(duration, miles, receipts)
            
            ensemble_pred = pred_current * w1 + pred_business * w2 + pred_weighted * w3
            ensemble_pred = round(ensemble_pred, 2)
            
            error = abs(ensemble_pred - expected)
            total_error += error
            
            if error < 0.01:
                exact_matches += 1
            if error < 1.0:
                close_matches += 1
        
        avg_error = total_error / len(test_data)
        score = avg_error * 100 + (len(test_data) - exact_matches) * 0.1
        
        weights_str = f"({w1:.1f}/{w2:.1f}/{w3:.1f})"
        print(f"{weights_str:<15} {score:<10.0f} ${avg_error:<9.2f} {exact_matches:<6} {close_matches:<6}")
        
        if score < best_score:
            best_score = score
            best_weights = (w1, w2, w3)
    
    print(f"\n🏆 Best weights: {best_weights} (Score: {best_score:.0f})")
    return best_weights

if __name__ == "__main__":
    # Run comprehensive ensemble testing
    results = test_all_ensemble_variants()
    
    # Analyze predictions
    analyze_ensemble_predictions()
    
    # Optimize weights
    best_weights = find_best_ensemble_weights()
    
    print(f"\n✅ Ensemble testing complete!")
    print(f"📁 Results saved to ensemble_results.json")
    print(f"🎯 Recommended weights: {best_weights}") 