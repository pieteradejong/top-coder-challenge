#!/usr/bin/env python3

import json
import time
from calculate_reimbursement import calculate_reimbursement

def fast_evaluation():
    """Fast evaluation that loads everything into memory and avoids subprocess calls"""
    
    print("🧾 Black Box Challenge - Fast Evaluation")
    print("=" * 50)
    print()
    
    # Load test cases once
    print("📊 Loading test cases...")
    with open('public_cases.json', 'r') as f:
        test_cases = json.load(f)
    
    print(f"Running evaluation against {len(test_cases)} test cases...")
    print()
    
    start_time = time.time()
    
    # Initialize counters
    successful_runs = 0
    exact_matches = 0
    close_matches = 0
    total_error = 0.0
    max_error = 0.0
    max_error_case = ""
    results = []
    errors = []
    
    # Process all cases in memory
    for i, case in enumerate(test_cases):
        if i % 100 == 0:
            print(f"Progress: {i}/{len(test_cases)} cases processed...")
        
        try:
            # Extract inputs
            trip_duration = case['input']['trip_duration_days']
            miles_traveled = case['input']['miles_traveled']
            receipts_amount = case['input']['total_receipts_amount']
            expected = case['expected_output']
            
            # Calculate reimbursement directly (no subprocess)
            actual = calculate_reimbursement(trip_duration, miles_traveled, receipts_amount)
            
            # Calculate error
            error = abs(actual - expected)
            
            # Store result
            results.append({
                'case_num': i + 1,
                'expected': expected,
                'actual': actual,
                'error': error,
                'trip_duration': trip_duration,
                'miles_traveled': miles_traveled,
                'receipts_amount': receipts_amount
            })
            
            successful_runs += 1
            
            # Check for exact match (within $0.01)
            if error < 0.01:
                exact_matches += 1
            
            # Check for close match (within $1.00)
            if error < 1.0:
                close_matches += 1
            
            # Update totals
            total_error += error
            
            # Track maximum error
            if error > max_error:
                max_error = error
                max_error_case = f"Case {i+1}: {trip_duration} days, {miles_traveled} miles, ${receipts_amount} receipts"
            
        except Exception as e:
            errors.append(f"Case {i+1}: Error - {str(e)}")
    
    end_time = time.time()
    elapsed = end_time - start_time
    
    print("✅ Evaluation Complete!")
    print()
    
    if successful_runs == 0:
        print("❌ No successful test cases!")
        return
    
    # Calculate metrics
    avg_error = total_error / successful_runs
    exact_pct = (exact_matches * 100) / successful_runs
    close_pct = (close_matches * 100) / successful_runs
    score = avg_error * 100 + (len(test_cases) - exact_matches) * 0.1
    
    print("📈 Results Summary:")
    print(f"  Total test cases: {len(test_cases)}")
    print(f"  Successful runs: {successful_runs}")
    print(f"  Exact matches (±$0.01): {exact_matches} ({exact_pct:.1f}%)")
    print(f"  Close matches (±$1.00): {close_matches} ({close_pct:.1f}%)")
    print(f"  Average error: ${avg_error:.2f}")
    print(f"  Maximum error: ${max_error:.2f}")
    print(f"  Evaluation time: {elapsed:.2f} seconds")
    print()
    print(f"🎯 Your Score: {score:.2f} (lower is better)")
    print()
    
    # Show high-error cases
    if exact_matches < len(test_cases):
        print("💡 Tips for improvement:")
        print("  Check these high-error cases:")
        
        # Sort by error and show top 5
        high_error_cases = sorted(results, key=lambda x: x['error'], reverse=True)[:5]
        for result in high_error_cases:
            print(f"    Case {result['case_num']}: {result['trip_duration']} days, "
                  f"{result['miles_traveled']} miles, ${result['receipts_amount']} receipts")
            print(f"      Expected: ${result['expected']:.2f}, Got: ${result['actual']:.2f}, "
                  f"Error: ${result['error']:.2f}")
    
    # Show errors if any
    if errors:
        print()
        print("⚠️  Errors encountered:")
        for error in errors[:10]:
            print(f"  {error}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more errors")
    
    return results

if __name__ == "__main__":
    fast_evaluation() 