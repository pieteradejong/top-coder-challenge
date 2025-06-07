#!/usr/bin/env python3
"""
ML Integration Script
Integrates best ML algorithms with our evaluation system
"""

import json
import numpy as np
from advanced_ml_algorithms import *
import subprocess
import os

def create_ml_calculate_reimbursement(algorithm_name, model):
    """Create a calculate_reimbursement.py file for ML algorithm"""
    
    if algorithm_name == "Neural Network (TensorFlow)":
        code = f'''#!/usr/bin/env python3
import sys
import json
import numpy as np
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

try:
    import tensorflow as tf
    from tensorflow import keras
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False

# Load trained model and scaler (saved during training)
model = None
scaler = None

def load_model():
    global model, scaler
    if model is None and TENSORFLOW_AVAILABLE:
        # Load the saved model and scaler
        with open('public_cases.json', 'r') as f:
            cases = json.load(f)
        
        X = []
        y = []
        
        for case in cases:
            duration = case['trip_duration_days']
            miles = case['miles_traveled']
            receipts = case['total_receipts_amount']
            reimbursement = case['expected_reimbursement']
            
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
        
        # Train model
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        model = keras.Sequential([
            keras.layers.Dense(128, activation='relu', input_shape=(X.shape[1],)),
            keras.layers.Dropout(0.3),
            keras.layers.Dense(64, activation='relu'),
            keras.layers.Dropout(0.2),
            keras.layers.Dense(32, activation='relu'),
            keras.layers.Dense(16, activation='relu'),
            keras.layers.Dense(1)
        ])
        
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )
        
        model.fit(X_scaled, y, epochs=100, batch_size=32, verbose=0)

def calculate_reimbursement(trip_duration_days, miles_traveled, total_receipts_amount):
    load_model()
    
    if not TENSORFLOW_AVAILABLE or model is None:
        # Fallback to simple calculation
        return trip_duration_days * 100 + miles_traveled * 0.5 + total_receipts_amount * 0.7
    
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
    X_scaled = scaler.transform(X)
    prediction = model.predict(X_scaled, verbose=0)[0][0]
    
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
    
    elif algorithm_name == "Random Forest":
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
            duration = case['trip_duration_days']
            miles = case['miles_traveled']
            receipts = case['total_receipts_amount']
            reimbursement = case['expected_reimbursement']
            
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
        
        # Train Random Forest
        model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
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
    
    elif algorithm_name == "Gradient Boosting":
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
            duration = case['trip_duration_days']
            miles = case['miles_traveled']
            receipts = case['total_receipts_amount']
            reimbursement = case['expected_reimbursement']
            
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
        
        # Train Gradient Boosting
        model = GradientBoostingRegressor(n_estimators=100, max_depth=6, random_state=42)
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
    
    else:  # Genetic Algorithm
        code = f'''#!/usr/bin/env python3
import sys
import json
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Best parameters found by genetic algorithm
BEST_PARAMS = [95.2, 0.58, 0.72, 28.5, 0.15]  # Will be updated after training

def calculate_reimbursement(trip_duration_days, miles_traveled, total_receipts_amount):
    base_rate, mileage_rate, receipt_rate, efficiency_bonus, vacation_penalty = BEST_PARAMS
    
    # Basic calculation
    base_amount = base_rate * trip_duration_days
    mileage_amount = mileage_rate * miles_traveled
    receipt_amount = receipt_rate * total_receipts_amount
    
    total = base_amount + mileage_amount + receipt_amount
    
    # Apply bonuses/penalties
    efficiency = miles_traveled / trip_duration_days if trip_duration_days > 0 else 0
    if 180 <= efficiency <= 220:
        total += efficiency_bonus * trip_duration_days
    
    if trip_duration_days >= 8:
        total *= (1 - vacation_penalty)
    
    return max(0, float(total))

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

def test_ml_algorithms():
    """Test ML algorithms using our evaluation system"""
    
    # Backup current algorithm
    if os.path.exists('calculate_reimbursement.py'):
        os.rename('calculate_reimbursement.py', 'calculate_reimbursement_backup.py')
    
    results = {}
    
    # Test algorithms that don't require heavy dependencies first
    algorithms_to_test = [
        "Random Forest",
        "Gradient Boosting", 
        "Genetic Algorithm"
    ]
    
    # Add neural network if TensorFlow is available
    try:
        import tensorflow as tf
        algorithms_to_test.insert(0, "Neural Network (TensorFlow)")
    except ImportError:
        print("TensorFlow not available, skipping Neural Network")
    
    for algorithm in algorithms_to_test:
        print(f"\n{'='*60}")
        print(f"Testing {algorithm}")
        print('='*60)
        
        # Create algorithm file
        code = create_ml_calculate_reimbursement(algorithm, None)
        with open('calculate_reimbursement.py', 'w') as f:
            f.write(code)
        
        # Make executable
        os.chmod('calculate_reimbursement.py', 0o755)
        
        # Run evaluation
        try:
            result = subprocess.run(['python', 'fast_eval.py'], 
                                  capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                output = result.stdout.strip()
                print(f"Output: {output}")
                
                # Parse results
                lines = output.split('\\n')
                for line in lines:
                    if 'Average Error:' in line:
                        avg_error = float(line.split('$')[1])
                        results[algorithm] = avg_error
                        print(f"{algorithm} Average Error: ${avg_error:.2f}")
                        break
            else:
                print(f"Error running {algorithm}: {result.stderr}")
                results[algorithm] = float('inf')
                
        except subprocess.TimeoutExpired:
            print(f"{algorithm} timed out")
            results[algorithm] = float('inf')
        except Exception as e:
            print(f"Error testing {algorithm}: {e}")
            results[algorithm] = float('inf')
    
    # Restore backup
    if os.path.exists('calculate_reimbursement_backup.py'):
        os.rename('calculate_reimbursement_backup.py', 'calculate_reimbursement.py')
    
    # Print summary
    print(f"\n{'='*60}")
    print("ML ALGORITHMS EVALUATION SUMMARY")
    print('='*60)
    
    sorted_results = sorted(results.items(), key=lambda x: x[1])
    for i, (name, error) in enumerate(sorted_results, 1):
        if error != float('inf'):
            print(f"{i:2d}. {name:<25} Average Error: ${error:8.2f}")
        else:
            print(f"{i:2d}. {name:<25} FAILED")
    
    return results

if __name__ == "__main__":
    test_ml_algorithms() 