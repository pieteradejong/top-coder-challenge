#!/usr/bin/env python3
"""
Direct Random Forest Test
Testing Random Forest algorithm directly against our evaluation system
"""

import json
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import warnings
warnings.filterwarnings('ignore')

def load_data():
    """Load and prepare the training data"""
    with open('public_cases.json', 'r') as f:
        cases = json.load(f)
    
    X = []
    y = []
    
    for case in cases:
        duration = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        reimbursement = case['expected_output']
        
        # Basic features
        features = [duration, miles, receipts]
        
        # Engineered features
        features.extend([
            miles / duration if duration > 0 else 0,  # miles per day
            receipts / duration if duration > 0 else 0,  # receipts per day
            miles / receipts if receipts > 0 else 0,  # efficiency ratio
            duration * miles,  # interaction
            duration * receipts,  # interaction
            miles * receipts,  # interaction
            np.log(duration + 1),  # log transforms
            np.log(miles + 1),
            np.log(receipts + 1),
            duration ** 2,  # polynomial features
            miles ** 0.5,
            receipts ** 0.5,
        ])
        
        X.append(features)
        y.append(reimbursement)
    
    return np.array(X), np.array(y)

def test_random_forest():
    """Test Random Forest with different configurations"""
    print("Loading data...")
    X, y = load_data()
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print(f"Training set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")
    
    # Test different Random Forest configurations
    configs = [
        {"n_estimators": 50, "max_depth": 8, "name": "RF_50_8"},
        {"n_estimators": 100, "max_depth": 10, "name": "RF_100_10"},
        {"n_estimators": 200, "max_depth": 12, "name": "RF_200_12"},
        {"n_estimators": 100, "max_depth": None, "name": "RF_100_None"},
        {"n_estimators": 300, "max_depth": 15, "name": "RF_300_15"},
    ]
    
    results = []
    
    for config in configs:
        print(f"\nTesting {config['name']}...")
        
        rf = RandomForestRegressor(
            n_estimators=config['n_estimators'],
            max_depth=config['max_depth'],
            random_state=42,
            n_jobs=-1
        )
        
        rf.fit(X_train, y_train)
        pred = rf.predict(X_test)
        mae = mean_absolute_error(y_test, pred)
        
        results.append((config['name'], mae, rf))
        print(f"{config['name']} MAE: ${mae:.2f}")
        
        # Feature importance
        feature_names = ['duration', 'miles', 'receipts', 'miles_per_day', 'receipts_per_day', 
                        'efficiency_ratio', 'duration_miles', 'duration_receipts', 'miles_receipts',
                        'log_duration', 'log_miles', 'log_receipts', 'duration_sq', 'miles_sqrt', 'receipts_sqrt']
        
        importances = rf.feature_importances_
        top_features = sorted(zip(feature_names, importances), key=lambda x: x[1], reverse=True)[:5]
        print(f"Top 5 features: {top_features}")
    
    # Find best model
    best_name, best_mae, best_model = min(results, key=lambda x: x[1])
    print(f"\n🏆 Best Random Forest: {best_name} with MAE: ${best_mae:.2f}")
    
    return best_model, best_mae

def create_rf_calculate_reimbursement(model):
    """Create a calculate_reimbursement.py file using the trained Random Forest"""
    
    # Get model parameters and feature importances
    n_estimators = model.n_estimators
    max_depth = model.max_depth
    
    code = f'''#!/usr/bin/env python3
import sys
import json
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import warnings
warnings.filterwarnings('ignore')

# Global model
model = None

def load_model():
    global model
    if model is None:
        # Load training data and train model
        with open('public_cases.json', 'r') as f:
            cases = json.load(f)
        
        X = []
        y = []
        
        for case in cases:
            duration = case['input']['trip_duration_days']
            miles = case['input']['miles_traveled']
            receipts = case['input']['total_receipts_amount']
            reimbursement = case['expected_output']
            
            # Basic features
            features = [duration, miles, receipts]
            
            # Engineered features
            features.extend([
                miles / duration if duration > 0 else 0,
                receipts / duration if duration > 0 else 0,
                miles / receipts if receipts > 0 else 0,
                duration * miles,
                duration * receipts,
                miles * receipts,
                np.log(duration + 1),
                np.log(miles + 1),
                np.log(receipts + 1),
                duration ** 2,
                miles ** 0.5,
                receipts ** 0.5,
            ])
            
            X.append(features)
            y.append(reimbursement)
        
        X = np.array(X)
        y = np.array(y)
        
        # Train Random Forest with best parameters
        model = RandomForestRegressor(
            n_estimators={n_estimators}, 
            max_depth={max_depth}, 
            random_state=42,
            n_jobs=1
        )
        model.fit(X, y)

def calculate_reimbursement(trip_duration_days, miles_traveled, total_receipts_amount):
    load_model()
    
    # Prepare features
    features = [trip_duration_days, miles_traveled, total_receipts_amount]
    features.extend([
        miles_traveled / trip_duration_days if trip_duration_days > 0 else 0,
        total_receipts_amount / trip_duration_days if trip_duration_days > 0 else 0,
        miles_traveled / total_receipts_amount if total_receipts_amount > 0 else 0,
        trip_duration_days * miles_traveled,
        trip_duration_days * total_receipts_amount,
        miles_traveled * total_receipts_amount,
        np.log(trip_duration_days + 1),
        np.log(miles_traveled + 1),
        np.log(total_receipts_amount + 1),
        trip_duration_days ** 2,
        miles_traveled ** 0.5,
        total_receipts_amount ** 0.5,
    ])
    
    X = np.array([features])
    prediction = model.predict(X)[0]
    
    return max(0, float(prediction))

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python calculate_reimbursement.py <trip_duration_days> <miles_traveled> <total_receipts_amount>")
        sys.exit(1)
    
    trip_duration_days = int(sys.argv[1])
    miles_traveled = float(sys.argv[2])
    total_receipts_amount = float(sys.argv[3])
    
    result = calculate_reimbursement(trip_duration_days, miles_traveled, total_receipts_amount)
    print(f"{{result:.2f}}")
'''
    
    return code

if __name__ == "__main__":
    best_model, best_mae = test_random_forest()
    
    print(f"\n{'='*60}")
    print("CREATING RANDOM FOREST ALGORITHM FILE")
    print('='*60)
    
    # Create the algorithm file
    code = create_rf_calculate_reimbursement(best_model)
    with open('rf_calculate_reimbursement.py', 'w') as f:
        f.write(code)
    
    print("✅ Created rf_calculate_reimbursement.py")
    print(f"📊 Expected MAE: ${best_mae:.2f}")
    print("\nTo test this algorithm:")
    print("1. cp rf_calculate_reimbursement.py calculate_reimbursement.py")
    print("2. python fast_eval.py") 