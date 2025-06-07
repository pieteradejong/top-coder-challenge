#!/usr/bin/env python3
"""
Enhanced Private Set Calculator - Optimized for generalization
"""

import sys
import numpy as np
import joblib
import warnings
warnings.filterwarnings('ignore')

# Global model
enhanced_model = None

def load_enhanced_model():
    global enhanced_model
    if enhanced_model is None:
        enhanced_model = joblib.load('enhanced_private_model.pkl')

def create_robust_features(duration, miles, receipts):
    """Create robust features matching training"""
    # Original perfect score features (15)
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
    
    # Additional robustness features (10 more)
    robust_features = [
        # Capped versions to handle outliers
        min(duration, 20),  # Cap extreme durations
        min(miles, 2000),   # Cap extreme miles
        min(receipts, 1000), # Cap extreme receipts
        
        # Smoothed ratios with regularization
        miles / (duration + 0.1),  # Avoid division by zero
        receipts / (duration + 0.1),
        
        # Interaction with caps
        min(duration * miles, 10000),
        min(duration * receipts, 5000),
        
        # Normalized features (0-1 scale approximation)
        duration / 30.0,  # Normalize by max reasonable duration
        miles / 3000.0,   # Normalize by max reasonable miles
        receipts / 2000.0 # Normalize by max reasonable receipts
    ]
    
    return base_features + robust_features

def calculate_reimbursement(trip_duration_days, miles_traveled, total_receipts_amount):
    """Enhanced reimbursement calculation optimized for private set"""
    load_enhanced_model()
    
    duration = float(trip_duration_days)
    miles = float(miles_traveled)
    receipts = float(total_receipts_amount)
    
    features = create_robust_features(duration, miles, receipts)
    X = np.array([features])
    
    prediction = enhanced_model['model'].predict(X)[0]
    return max(0, float(prediction))

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python enhanced_calculator.py <trip_duration_days> <miles_traveled> <total_receipts_amount>")
        sys.exit(1)
    
    trip_duration_days = int(sys.argv[1])
    miles_traveled = float(sys.argv[2])
    total_receipts_amount = float(sys.argv[3])
    
    result = calculate_reimbursement(trip_duration_days, miles_traveled, total_receipts_amount)
    print(f"{result:.2f}")
