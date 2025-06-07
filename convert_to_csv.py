#!/usr/bin/env python3

import json
import csv
import os

def convert_json_to_csv():
    """Convert JSON test cases to CSV for faster loading"""
    
    print("Converting JSON to CSV for faster analysis...")
    
    # Load JSON data
    with open('public_cases.json', 'r') as f:
        data = json.load(f)
    
    # Write CSV file
    with open('test_cases.csv', 'w', newline='') as csvfile:
        fieldnames = ['case_id', 'trip_duration_days', 'miles_traveled', 'total_receipts_amount', 'expected_output']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for i, case in enumerate(data):
            row = {
                'case_id': i + 1,
                'trip_duration_days': case['input']['trip_duration_days'],
                'miles_traveled': case['input']['miles_traveled'],
                'total_receipts_amount': case['input']['total_receipts_amount'],
                'expected_output': case['expected_output']
            }
            writer.writerow(row)
    
    # Get file size
    file_size = os.path.getsize('test_cases.csv') / 1024
    
    print(f"✅ Converted {len(data)} test cases to test_cases.csv")
    print(f"CSV file size: {file_size:.1f} KB")
    
    # Show sample
    print("\nSample data (first 5 rows):")
    with open('test_cases.csv', 'r') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= 5:
                break
            print(f"  Case {row['case_id']}: {row['trip_duration_days']} days, {row['miles_traveled']} miles, ${row['total_receipts_amount']} -> ${row['expected_output']}")
    
    return len(data)

if __name__ == "__main__":
    convert_json_to_csv() 