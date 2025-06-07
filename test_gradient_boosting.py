#!/usr/bin/env python3
"""
Direct Gradient Boosting Test
Testing Gradient Boosting algorithm directly against our evaluation system
"""

import json
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
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

def test_gradient_boosting():
    """Test Gradient Boosting with different configurations"""
    print("Loading data...")
    X, y = load_data()
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print(f"Training set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")
    
    # Test different Gradient Boosting configurations
    configs = [
        {"n_estimators": 100, "max_depth": 6, "learning_rate": 0.1, "name": "GB_100_6_0.1"},
        {"n_estimators": 200, "max_depth": 8, "learning_rate": 0.1, "name": "GB_200_8_0.1"},
        {"n_estimators": 300, "max_depth": 6, "learning_rate": 0.05, "name": "GB_300_6_0.05"},
        {"n_estimators": 150, "max_depth": 10, "learning_rate": 0.1, "name": "GB_150_10_0.1"},
        {"n_estimators": 250, "max_depth": 8, "learning_rate": 0.08, "name": "GB_250_8_0.08"},
    ]
    
    results = []
    
    for config in configs:
        print(f"\nTesting {config['name']}...")
        
        gb = GradientBoostingRegressor(
            n_estimators=config['n_estimators'],
            max_depth=config['max_depth'],
            learning_rate=config['learning_rate'],
            random_state=42
        )
        
        gb.fit(X_train, y_train)
        pred = gb.predict(X_test)
        mae = mean_absolute_error(y_test, pred)
        
        results.append((config['name'], mae, gb))
        print(f"{config['name']} MAE: ${mae:.2f}")
        
        # Feature importance
        feature_names = ['duration', 'miles', 'receipts', 'miles_per_day', 'receipts_per_day', 
                        'efficiency_ratio', 'duration_miles', 'duration_receipts', 'miles_receipts',
                        'log_duration', 'log_miles', 'log_receipts', 'duration_sq', 'miles_sqrt', 'receipts_sqrt']
        
        importances = gb.feature_importances_
        top_features = sorted(zip(feature_names, importances), key=lambda x: x[1], reverse=True)[:5]
        print(f"Top 5 features: {top_features}")
    
    # Find best model
    best_name, best_mae, best_model = min(results, key=lambda x: x[1])
    print(f"\n🏆 Best Gradient Boosting: {best_name} with MAE: ${best_mae:.2f}")
    
    return best_model, best_mae

def create_gb_calculate_reimbursement(model):
    """Create a calculate_reimbursement.py file using the trained Gradient Boosting"""
    
    # Get model parameters
    n_estimators = model.n_estimators
    max_depth = model.max_depth
    learning_rate = model.learning_rate
    
    code = f'''#!/usr/bin/env python3
import sys
import json
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
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
        
        # Train Gradient Boosting with best parameters
        model = GradientBoostingRegressor(
            n_estimators={n_estimators}, 
            max_depth={max_depth}, 
            learning_rate={learning_rate},
            random_state=42
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
    best_model, best_mae = test_gradient_boosting()
    
    print(f"\n{'='*60}")
    print("CREATING GRADIENT BOOSTING ALGORITHM FILE")
    print('='*60)
    
    # Create the algorithm file
    code = create_gb_calculate_reimbursement(best_model)
    with open('gb_calculate_reimbursement.py', 'w') as f:
        f.write(code)
    
    print("✅ Created gb_calculate_reimbursement.py")
    print(f"📊 Expected MAE: ${best_mae:.2f}")
    print("\nTo test this algorithm:")
    print("1. cp gb_calculate_reimbursement.py calculate_reimbursement.py")
    print("2. python fast_eval.py") 