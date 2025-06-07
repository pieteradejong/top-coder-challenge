#!/usr/bin/env python3
"""
Generalizable Reimbursement Calculator - Optimized for unseen data
Focus on generalization over perfect training performance
"""

import sys
import numpy as np
import joblib
import warnings
warnings.filterwarnings('ignore')

# Global model
generalizable_model = None

def load_generalizable_model():
    global generalizable_model
    if generalizable_model is None:
        try:
            generalizable_model = joblib.load('generalizable_model.pkl')
        except:
            # Fallback to training if model file not found
            train_generalizable_model()

def train_generalizable_model():
    global generalizable_model
    import json
    
    # Load training data
    with open('public_cases.json', 'r') as f:
        cases = json.load(f)
    
    X = []
    y = []
    
    for case in cases:
        duration = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        reimbursement = case['expected_output']
        
        # Simple, interpretable features (8 features)
        features = [
            duration,                                    # Trip length
            miles,                                       # Distance
            receipts,                                    # Spending
            miles / duration if duration > 0 else 0,    # Miles per day
            receipts / duration if duration > 0 else 0, # Spending per day
            np.log1p(receipts),                         # Log receipts
            duration * miles,                           # Trip complexity
            1 if duration >= 8 else 0                  # Long trip penalty
        ]
        
        X.append(features)
        y.append(reimbursement)
    
    X = np.array(X)
    y = np.array(y)
    
    # Generalizable configuration (conservative)
    from sklearn.ensemble import GradientBoostingRegressor
    model = GradientBoostingRegressor(
        n_estimators=150,
        max_depth=5,
        learning_rate=0.08,
        subsample=0.85,
        min_samples_split=10,
        min_samples_leaf=5,
        max_features='sqrt',
        random_state=42
    )
    model.fit(X, y)
    
    generalizable_model = {'model': model}

def create_simple_features(duration, miles, receipts):
    """Create simple features matching training"""
    features = [
        duration,                                    # Trip length
        miles,                                       # Distance
        receipts,                                    # Spending
        miles / duration if duration > 0 else 0,    # Miles per day
        receipts / duration if duration > 0 else 0, # Spending per day
        np.log1p(receipts),                         # Log receipts
        duration * miles,                           # Trip complexity
        1 if duration >= 8 else 0                  # Long trip penalty
    ]
    return features

def calculate_reimbursement(trip_duration_days, miles_traveled, total_receipts_amount):
    """
    Generalizable reimbursement calculation
    Optimized for unseen data performance over training accuracy
    """
    load_generalizable_model()
    
    duration = float(trip_duration_days)
    miles = float(miles_traveled)
    receipts = float(total_receipts_amount)
    
    features = create_simple_features(duration, miles, receipts)
    X = np.array([features])
    
    prediction = generalizable_model['model'].predict(X)[0]
    return max(0, float(prediction))

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python generalizable_calculator.py <trip_duration_days> <miles_traveled> <total_receipts_amount>")
        sys.exit(1)
    
    trip_duration_days = int(sys.argv[1])
    miles_traveled = float(sys.argv[2])
    total_receipts_amount = float(sys.argv[3])
    
    result = calculate_reimbursement(trip_duration_days, miles_traveled, total_receipts_amount)
    print(f"{result:.2f}")
