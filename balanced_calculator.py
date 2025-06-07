#!/usr/bin/env python3
"""
Balanced Reimbursement Calculator - Sweet spot between performance and generalization
"""

import sys
import numpy as np
import joblib
import warnings
warnings.filterwarnings('ignore')

# Global model
balanced_model = None

def load_balanced_model():
    global balanced_model
    if balanced_model is None:
        try:
            balanced_model = joblib.load('balanced_model.pkl')
        except:
            train_balanced_model()

def train_balanced_model():
    global balanced_model
    import json
    
    with open('public_cases.json', 'r') as f:
        cases = json.load(f)
    
    X = []
    y = []
    
    for case in cases:
        duration = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        reimbursement = case['expected_output']
        
        # Balanced feature set (12 features)
        features = [
            # Core features
            duration, miles, receipts,
            # Essential ratios
            miles / duration if duration > 0 else 0,
            receipts / duration if duration > 0 else 0,
            miles / (receipts + 1),
            # Key transformations
            np.log1p(receipts),
            np.log1p(miles),
            np.sqrt(receipts),
            # Important interactions
            duration * miles,
            1 if duration >= 8 else 0,
            1 if duration == 5 else 0
        ]
        
        X.append(features)
        y.append(reimbursement)
    
    X = np.array(X)
    y = np.array(y)
    
    # Balanced configuration
    from sklearn.ensemble import GradientBoostingRegressor
    model = GradientBoostingRegressor(
        n_estimators=400,
        max_depth=7,
        learning_rate=0.04,
        subsample=0.9,
        min_samples_split=5,
        min_samples_leaf=3,
        max_features=0.8,
        random_state=42
    )
    model.fit(X, y)
    
    balanced_model = {'model': model}

def create_balanced_features(duration, miles, receipts):
    """Create balanced features matching training"""
    features = [
        # Core features
        duration, miles, receipts,
        # Essential ratios
        miles / duration if duration > 0 else 0,
        receipts / duration if duration > 0 else 0,
        miles / (receipts + 1),
        # Key transformations
        np.log1p(receipts),
        np.log1p(miles),
        np.sqrt(receipts),
        # Important interactions
        duration * miles,
        1 if duration >= 8 else 0,
        1 if duration == 5 else 0
    ]
    return features

def calculate_reimbursement(trip_duration_days, miles_traveled, total_receipts_amount):
    """
    Balanced reimbursement calculation
    Sweet spot between performance and generalization
    """
    load_balanced_model()
    
    duration = float(trip_duration_days)
    miles = float(miles_traveled)
    receipts = float(total_receipts_amount)
    
    features = create_balanced_features(duration, miles, receipts)
    X = np.array([features])
    
    prediction = balanced_model['model'].predict(X)[0]
    return max(0, float(prediction))

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python balanced_calculator.py <trip_duration_days> <miles_traveled> <total_receipts_amount>")
        sys.exit(1)
    
    trip_duration_days = int(sys.argv[1])
    miles_traveled = float(sys.argv[2])
    total_receipts_amount = float(sys.argv[3])
    
    result = calculate_reimbursement(trip_duration_days, miles_traveled, total_receipts_amount)
    print(f"{result:.2f}")
