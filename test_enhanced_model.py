#!/usr/bin/env python3
"""
Test Enhanced Model Performance
"""

import joblib
import numpy as np
import json

def test_enhanced_model():
    # Test enhanced model
    enhanced = joblib.load('enhanced_private_model.pkl')
    print('🔍 Enhanced Model Analysis:')
    print(f'   Config: {enhanced["config"]}')
    print(f'   Performance: {enhanced["performance"]}')
    print(f'   Features: {enhanced["feature_count"]}')

    # Quick test on a few cases
    with open('public_cases.json', 'r') as f:
        cases = json.load(f)

    print('\n🧪 Quick Test on 5 cases:')
    for i in range(5):
        case = cases[i]
        duration = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled'] 
        receipts = case['input']['total_receipts_amount']
        expected = case['expected_output']
        
        # Create features like enhanced calculator
        base_features = [
            duration, miles, receipts,
            np.log1p(receipts),
            duration * miles,
            np.sqrt(receipts),
            miles / duration if duration > 0 else 0,
            receipts / duration if duration > 0 else 0,
            miles / (receipts + 1),
            duration ** 2,
            miles ** 0.5,
            receipts ** 2,
            (miles / duration) * (receipts / duration) if duration > 0 else 0,
            np.log1p(miles),
            duration * receipts
        ]
        
        robust_features = [
            min(duration, 20), min(miles, 2000), min(receipts, 1000),
            miles / (duration + 0.1), receipts / (duration + 0.1),
            min(duration * miles, 10000), min(duration * receipts, 5000),
            duration / 30.0, miles / 3000.0, receipts / 2000.0
        ]
        
        features = base_features + robust_features
        X = np.array([features])
        prediction = enhanced['model'].predict(X)[0]
        error = abs(prediction - expected)
        
        print(f'   Case {i+1}: Expected ${expected:.2f}, Got ${prediction:.2f}, Error ${error:.6f}')

if __name__ == "__main__":
    test_enhanced_model() 