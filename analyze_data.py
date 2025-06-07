#!/usr/bin/env python3

import json
import numpy as np
import pandas as pd
from collections import defaultdict
import matplotlib.pyplot as plt

def load_data():
    """Load the public test cases"""
    with open('public_cases.json', 'r') as f:
        data = json.load(f)
    
    # Convert to DataFrame for easier analysis
    rows = []
    for case in data:
        row = case['input'].copy()
        row['expected_output'] = case['expected_output']
        rows.append(row)
    
    return pd.DataFrame(rows)

def analyze_basic_patterns(df):
    """Analyze basic patterns in the data"""
    print("=== BASIC STATISTICS ===")
    print(f"Total cases: {len(df)}")
    print(f"Trip duration range: {df['trip_duration_days'].min()} - {df['trip_duration_days'].max()} days")
    print(f"Miles range: {df['miles_traveled'].min()} - {df['miles_traveled'].max()} miles")
    print(f"Receipts range: ${df['total_receipts_amount'].min():.2f} - ${df['total_receipts_amount'].max():.2f}")
    print(f"Reimbursement range: ${df['expected_output'].min():.2f} - ${df['expected_output'].max():.2f}")
    print()
    
    # Calculate derived metrics
    df['miles_per_day'] = df['miles_traveled'] / df['trip_duration_days']
    df['receipts_per_day'] = df['total_receipts_amount'] / df['trip_duration_days']
    df['reimbursement_per_day'] = df['expected_output'] / df['trip_duration_days']
    
    print("=== PER-DAY AVERAGES ===")
    print(f"Average miles per day: {df['miles_per_day'].mean():.2f}")
    print(f"Average receipts per day: ${df['receipts_per_day'].mean():.2f}")
    print(f"Average reimbursement per day: ${df['reimbursement_per_day'].mean():.2f}")
    print()

def analyze_by_trip_length(df):
    """Analyze patterns by trip duration"""
    print("=== ANALYSIS BY TRIP LENGTH ===")
    
    for days in sorted(df['trip_duration_days'].unique()):
        subset = df[df['trip_duration_days'] == days]
        avg_reimbursement_per_day = subset['reimbursement_per_day'].mean()
        print(f"{days} days: {len(subset)} cases, avg ${avg_reimbursement_per_day:.2f}/day")
    print()

def analyze_mileage_patterns(df):
    """Analyze mileage reimbursement patterns"""
    print("=== MILEAGE ANALYSIS ===")
    
    # Look at cases with minimal receipts to isolate mileage effects
    low_receipt_cases = df[df['total_receipts_amount'] < 50]
    
    if len(low_receipt_cases) > 0:
        print(f"Cases with <$50 receipts: {len(low_receipt_cases)}")
        
        # Calculate implied mileage rate
        # Assuming base per diem of $100/day
        low_receipt_cases = low_receipt_cases.copy()
        low_receipt_cases['implied_base'] = low_receipt_cases['trip_duration_days'] * 100
        low_receipt_cases['mileage_component'] = low_receipt_cases['expected_output'] - low_receipt_cases['implied_base']
        low_receipt_cases['implied_rate'] = low_receipt_cases['mileage_component'] / low_receipt_cases['miles_traveled']
        
        print("Sample mileage rates:")
        for _, row in low_receipt_cases.head(10).iterrows():
            print(f"  {row['miles_traveled']:.0f} miles, {row['trip_duration_days']} days: ${row['implied_rate']:.3f}/mile")
    print()

def analyze_receipt_patterns(df):
    """Analyze receipt reimbursement patterns"""
    print("=== RECEIPT ANALYSIS ===")
    
    # Look at cases with minimal mileage to isolate receipt effects
    low_mileage_cases = df[df['miles_traveled'] < 50]
    
    if len(low_mileage_cases) > 0:
        print(f"Cases with <50 miles: {len(low_mileage_cases)}")
        
        # Calculate implied receipt reimbursement rate
        low_mileage_cases = low_mileage_cases.copy()
        low_mileage_cases['implied_base'] = low_mileage_cases['trip_duration_days'] * 100
        low_mileage_cases['mileage_component'] = low_mileage_cases['miles_traveled'] * 0.58  # Assume $0.58/mile
        low_mileage_cases['receipt_component'] = (low_mileage_cases['expected_output'] - 
                                                 low_mileage_cases['implied_base'] - 
                                                 low_mileage_cases['mileage_component'])
        low_mileage_cases['receipt_rate'] = low_mileage_cases['receipt_component'] / low_mileage_cases['total_receipts_amount']
        
        print("Sample receipt rates:")
        for _, row in low_mileage_cases.head(10).iterrows():
            if row['total_receipts_amount'] > 0:
                print(f"  ${row['total_receipts_amount']:.2f} receipts, {row['trip_duration_days']} days: {row['receipt_rate']:.3f} rate")
    print()

def analyze_5_day_bonus(df):
    """Analyze the 5-day trip bonus mentioned in interviews"""
    print("=== 5-DAY TRIP ANALYSIS ===")
    
    five_day_trips = df[df['trip_duration_days'] == 5]
    other_trips = df[df['trip_duration_days'].isin([4, 6])]  # Compare to similar lengths
    
    print(f"5-day trips: {len(five_day_trips)} cases")
    print(f"4&6-day trips: {len(other_trips)} cases")
    
    if len(five_day_trips) > 0 and len(other_trips) > 0:
        five_day_avg = five_day_trips['reimbursement_per_day'].mean()
        other_avg = other_trips['reimbursement_per_day'].mean()
        
        print(f"5-day average: ${five_day_avg:.2f}/day")
        print(f"4&6-day average: ${other_avg:.2f}/day")
        print(f"5-day bonus: ${five_day_avg - other_avg:.2f}/day ({((five_day_avg/other_avg - 1) * 100):.1f}%)")
    print()

def main():
    """Main analysis function"""
    print("Loading data...")
    df = load_data()
    
    analyze_basic_patterns(df)
    analyze_by_trip_length(df)
    analyze_mileage_patterns(df)
    analyze_receipt_patterns(df)
    analyze_5_day_bonus(df)
    
    # Save processed data for further analysis
    df.to_csv('analyzed_data.csv', index=False)
    print("Analysis complete. Data saved to analyzed_data.csv")

if __name__ == "__main__":
    main() 