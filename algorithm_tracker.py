#!/usr/bin/env python3

import json
import datetime
from calculate_reimbursement import calculate_reimbursement

def track_algorithm_performance():
    """Track the current algorithm's performance and save to history"""
    
    # Load test data
    with open('public_cases.json', 'r') as f:
        data = json.load(f)
    
    # Calculate current metrics
    total_error = 0
    exact_matches = 0
    close_matches = 0
    errors = []
    
    for case in data:
        duration = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        expected = case['expected_output']
        
        predicted = calculate_reimbursement(duration, miles, receipts)
        error = abs(predicted - expected)
        
        total_error += error
        errors.append(error)
        
        if error < 0.01:
            exact_matches += 1
        if error < 1.0:
            close_matches += 1
    
    avg_error = total_error / len(data)
    max_error = max(errors)
    score = avg_error * 100 + (len(data) - exact_matches) * 0.1
    
    # Create algorithm entry
    algorithm_entry = {
        'timestamp': datetime.datetime.now().isoformat(),
        'attempt': 13,  # Current attempt number
        'description': 'Moderate penalty adjustments - major score improvement',
        'configuration': {
            'base_rates': {
                '1_day': 138,
                '2_day': 108,
                '3_5_day': 100,
                '6_7_day': 95,
                '8_plus_day': 90
            },
            'mileage_rates': {
                'first_500': 0.66,
                'next_500': 0.45,
                'beyond_1000': 0.25
            },
            'receipt_rates': {
                'first_200': 0.79,
                'next_300': 0.6,
                'beyond_500': 0.4
            },
            'efficiency_bonus': {
                'sweet_spot_range': '180-220 mi/day',
                'bonus_per_day': 40,
                'penalty_threshold': 300,
                'penalty_per_day': -20
            },
            'caps': {
                '1_day': 1500,
                '2_day': 1700,
                '3_day': 1600,
                '4_day': 1750,
                '5_day': 1850,
                '6_day': 1900,
                '7_day': 1950,
                '8_day': 2000
            },
            'bias_correction': 0.995,
            'fraud_prevention': {
                '1_day_extreme': 0.3,
                '4_day_extreme': 0.2,
                'long_trip_vacation': 0.8
            }
        },
        'performance': {
            'avg_error': round(avg_error, 2),
            'max_error': round(max_error, 2),
            'exact_matches': exact_matches,
            'close_matches': close_matches,
            'score': round(score, 2),
            'total_cases': len(data)
        },
        'key_changes': [
            'Added moderate vacation penalties: 12+ days get 25% reduction',
            'Receipt fraud prevention: >$2,000 gets 30% penalty on excess',
            'Efficiency penalties: <30 mi/day gets $20/day penalty',
            'Graduated bias correction: 8+ days (4%), 12+ days (8%)',
            'Conservative approach to avoid over-penalization'
        ]
    }
    
    # Load existing algorithm history or create new
    try:
        with open('algorithm_history.json', 'r') as f:
            algorithm_history = json.load(f)
    except FileNotFoundError:
        algorithm_history = []
    
    # Add new entry
    algorithm_history.append(algorithm_entry)
    
    # Save updated history
    with open('algorithm_history.json', 'w') as f:
        json.dump(algorithm_history, f, indent=2)
    
    print(f"🎯 ALGORITHM PERFORMANCE TRACKED")
    print(f"=" * 60)
    print(f"Attempt: {algorithm_entry['attempt']}")
    print(f"Description: {algorithm_entry['description']}")
    print(f"Average Error: ${algorithm_entry['performance']['avg_error']}")
    print(f"Exact Matches: {algorithm_entry['performance']['exact_matches']} 🎉")
    print(f"Close Matches: {algorithm_entry['performance']['close_matches']}")
    print(f"Score: {algorithm_entry['performance']['score']}")
    print(f"Max Error: ${algorithm_entry['performance']['max_error']}")
    
    return algorithm_entry

def compare_algorithms():
    """Compare performance across all tracked algorithms"""
    
    try:
        with open('algorithm_history.json', 'r') as f:
            algorithm_history = json.load(f)
    except FileNotFoundError:
        print("No algorithm history found. Run track_algorithm_performance() first.")
        return
    
    print(f"\n📊 ALGORITHM PERFORMANCE COMPARISON")
    print(f"=" * 80)
    
    # Sort by score (lower is better)
    sorted_algorithms = sorted(algorithm_history, key=lambda x: x['performance']['score'])
    
    print(f"{'Rank':<4} {'Attempt':<8} {'Avg Error':<10} {'Exact':<6} {'Close':<6} {'Score':<10} {'Description'}")
    print(f"-" * 80)
    
    for i, algo in enumerate(sorted_algorithms):
        perf = algo['performance']
        rank = i + 1
        attempt = algo['attempt']
        avg_error = f"${perf['avg_error']}"
        exact = perf['exact_matches']
        close = perf['close_matches']
        score = f"{perf['score']:.0f}"
        desc = algo['description'][:30] + "..." if len(algo['description']) > 30 else algo['description']
        
        print(f"{rank:<4} {attempt:<8} {avg_error:<10} {exact:<6} {close:<6} {score:<10} {desc}")
    
    # Highlight best performers
    best_overall = sorted_algorithms[0]
    best_exact = max(algorithm_history, key=lambda x: x['performance']['exact_matches'])
    best_avg_error = min(algorithm_history, key=lambda x: x['performance']['avg_error'])
    
    print(f"\n🏆 BEST PERFORMERS:")
    print(f"  Best Overall Score: Attempt #{best_overall['attempt']} (Score: {best_overall['performance']['score']:.0f})")
    print(f"  Most Exact Matches: Attempt #{best_exact['attempt']} ({best_exact['performance']['exact_matches']} exact)")
    print(f"  Lowest Avg Error: Attempt #{best_avg_error['attempt']} (${best_avg_error['performance']['avg_error']})")

def analyze_algorithm_evolution():
    """Analyze how our algorithms have evolved over time"""
    
    try:
        with open('algorithm_history.json', 'r') as f:
            algorithm_history = json.load(f)
    except FileNotFoundError:
        print("No algorithm history found.")
        return
    
    print(f"\n📈 ALGORITHM EVOLUTION ANALYSIS")
    print(f"=" * 60)
    
    # Sort by attempt number
    sorted_by_attempt = sorted(algorithm_history, key=lambda x: x['attempt'])
    
    print(f"Progress over time:")
    for algo in sorted_by_attempt:
        perf = algo['performance']
        print(f"  Attempt #{algo['attempt']:2d}: ${perf['avg_error']:6.2f} avg, {perf['exact_matches']} exact, {perf['close_matches']} close")
    
    # Calculate trends
    if len(sorted_by_attempt) >= 2:
        first = sorted_by_attempt[0]['performance']
        latest = sorted_by_attempt[-1]['performance']
        
        error_improvement = first['avg_error'] - latest['avg_error']
        exact_improvement = latest['exact_matches'] - first['exact_matches']
        close_improvement = latest['close_matches'] - first['close_matches']
        
        print(f"\n📊 Overall Progress:")
        print(f"  Average Error: ${first['avg_error']:.2f} → ${latest['avg_error']:.2f} ({error_improvement:+.2f})")
        print(f"  Exact Matches: {first['exact_matches']} → {latest['exact_matches']} ({exact_improvement:+d})")
        print(f"  Close Matches: {first['close_matches']} → {latest['close_matches']} ({close_improvement:+d})")

def get_best_algorithm_config():
    """Get the configuration of the best performing algorithm"""
    
    try:
        with open('algorithm_history.json', 'r') as f:
            algorithm_history = json.load(f)
    except FileNotFoundError:
        print("No algorithm history found.")
        return None
    
    # Find best by score
    best_algorithm = min(algorithm_history, key=lambda x: x['performance']['score'])
    
    print(f"\n🏆 BEST ALGORITHM CONFIGURATION")
    print(f"=" * 60)
    print(f"Attempt: #{best_algorithm['attempt']}")
    print(f"Description: {best_algorithm['description']}")
    print(f"Score: {best_algorithm['performance']['score']:.2f}")
    print(f"Exact Matches: {best_algorithm['performance']['exact_matches']}")
    
    print(f"\nConfiguration:")
    config = best_algorithm['configuration']
    
    print(f"  Base Rates:")
    for key, value in config['base_rates'].items():
        print(f"    {key}: ${value}/day")
    
    print(f"  Mileage Rates:")
    for key, value in config['mileage_rates'].items():
        print(f"    {key}: ${value:.2f}/mile")
    
    print(f"  Receipt Rates:")
    for key, value in config['receipt_rates'].items():
        print(f"    {key}: {value:.0%}")
    
    print(f"  Bias Correction: {config['bias_correction']}")
    
    return best_algorithm

if __name__ == "__main__":
    # Track current algorithm
    current_algo = track_algorithm_performance()
    
    # Compare with previous algorithms
    compare_algorithms()
    
    # Show evolution
    analyze_algorithm_evolution()
    
    # Show best config
    get_best_algorithm_config() 