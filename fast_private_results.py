#!/usr/bin/env python3
"""
Fast Private Results Generator
Uses our perfect score algorithm to quickly generate private_results.txt
"""

import json
import time
from calculate_reimbursement import calculate_reimbursement

def generate_private_results():
    print("🧾 Fast Private Results Generator")
    print("=" * 50)
    
    start_time = time.time()
    
    # Load private cases
    print("📊 Loading private test cases...")
    with open('private_cases.json', 'r') as f:
        private_cases = json.load(f)
    
    print(f"✅ Loaded {len(private_cases)} private test cases")
    
    # Generate results
    results = []
    print("⏳ Generating results...")
    
    for i, case in enumerate(private_cases):
        if i % 500 == 0:
            print(f"Progress: {i}/{len(private_cases)} cases processed...")
        
        trip_duration = case['trip_duration_days']
        miles = case['miles_traveled']
        receipts = case['total_receipts_amount']
        
        # Use our perfect score algorithm
        reimbursement = calculate_reimbursement(trip_duration, miles, receipts)
        results.append(f"{reimbursement:.2f}")
    
    # Save results
    print("💾 Saving results to private_results.txt...")
    with open('private_results.txt', 'w') as f:
        for result in results:
            f.write(f"{result}\n")
    
    elapsed = time.time() - start_time
    print(f"✅ Generated {len(results)} results in {elapsed:.1f} seconds")
    print(f"📁 Results saved to private_results.txt")
    print(f"🚀 Ready for submission!")

if __name__ == "__main__":
    generate_private_results() 