#!/usr/bin/env python3
"""
Anti-Overfitting Optimizer - Focus on generalization over perfect training performance
"""

import json
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import cross_val_score, KFold, train_test_split
from sklearn.metrics import mean_absolute_error
import joblib
import time
import warnings
warnings.filterwarnings('ignore')

class AntiOverfittingOptimizer:
    def __init__(self):
        print("🛡️ ANTI-OVERFITTING OPTIMIZER")
        print("=" * 50)
        print("Focus: Generalization over perfect training performance")
        self.load_data()
        
    def load_data(self):
        with open('public_cases.json', 'r') as f:
            cases = json.load(f)
        
        data = []
        for case in cases:
            data.append({
                'trip_duration_days': case['input']['trip_duration_days'],
                'miles_traveled': case['input']['miles_traveled'],
                'total_receipts_amount': case['input']['total_receipts_amount'],
                'expected_output': case['expected_output']
            })
        
        self.df = pd.DataFrame(data)
        print(f"✅ Loaded {len(self.df)} training cases")
        
    def create_simple_features(self, df):
        """Create minimal, interpretable features to avoid overfitting"""
        print("🔧 Creating simple, interpretable features...")
        X = []
        
        for _, row in df.iterrows():
            duration = row['trip_duration_days']
            miles = row['miles_traveled']
            receipts = row['total_receipts_amount']
            
            # Core business logic features only (8 features total)
            features = [
                duration,                                    # Trip length
                miles,                                       # Distance
                receipts,                                    # Spending
                miles / duration if duration > 0 else 0,    # Miles per day (efficiency)
                receipts / duration if duration > 0 else 0, # Spending per day
                np.log1p(receipts),                         # Log receipts (diminishing returns)
                duration * miles,                           # Trip complexity
                1 if duration >= 8 else 0                  # Long trip penalty
            ]
            
            X.append(features)
        
        return np.array(X)
    
    def test_generalization_configs(self, X, y):
        """Test configurations optimized for generalization, not training performance"""
        print("\n⚙️ Testing Generalization-Focused Configurations...")
        
        # Split data for honest evaluation
        X_train, X_holdout, y_train, y_holdout = train_test_split(
            X, y, test_size=0.2, random_state=42, shuffle=True
        )
        
        print(f"📊 Training: {len(X_train)} cases, Holdout: {len(X_holdout)} cases")
        
        # Conservative configurations focused on generalization
        configs = [
            # Conservative (low overfitting risk)
            {'n_estimators': 100, 'max_depth': 4, 'learning_rate': 0.1, 'subsample': 0.8, 'name': 'Conservative'},
            {'n_estimators': 150, 'max_depth': 5, 'learning_rate': 0.08, 'subsample': 0.85, 'name': 'Moderate'},
            {'n_estimators': 200, 'max_depth': 6, 'learning_rate': 0.05, 'subsample': 0.9, 'name': 'Balanced'},
            
            # Regularized (high regularization)
            {'n_estimators': 100, 'max_depth': 3, 'learning_rate': 0.1, 'subsample': 0.7, 'name': 'High_Reg'},
            {'n_estimators': 250, 'max_depth': 4, 'learning_rate': 0.03, 'subsample': 0.8, 'name': 'Ultra_Reg'},
            
            # Business-focused (interpretable)
            {'n_estimators': 50, 'max_depth': 6, 'learning_rate': 0.15, 'subsample': 0.9, 'name': 'Business_Logic'}
        ]
        
        results = []
        kfold = KFold(n_splits=5, shuffle=True, random_state=42)
        
        for config in configs:
            name = config.pop('name')
            print(f"⏳ Testing {name}: {config}")
            
            # Add regularization parameters
            model = GradientBoostingRegressor(
                random_state=42,
                min_samples_split=10,    # Prevent overfitting to small groups
                min_samples_leaf=5,      # Ensure meaningful leaf nodes
                max_features='sqrt',     # Feature subsampling
                **config
            )
            
            # Cross-validation on training set
            cv_scores = cross_val_score(model, X_train, y_train, cv=kfold, 
                                      scoring='neg_mean_absolute_error')
            cv_mae = -cv_scores.mean()
            cv_std = cv_scores.std()
            
            # Train on full training set and test on holdout
            model.fit(X_train, y_train)
            
            # Training performance
            train_pred = model.predict(X_train)
            train_mae = mean_absolute_error(y_train, train_pred)
            
            # Holdout performance (honest evaluation)
            holdout_pred = model.predict(X_holdout)
            holdout_mae = mean_absolute_error(y_holdout, holdout_pred)
            
            # Generalization gap (key metric)
            gen_gap = holdout_mae - train_mae
            
            result = {
                'name': name,
                'config': config,
                'cv_mae': cv_mae,
                'cv_std': cv_std,
                'train_mae': train_mae,
                'holdout_mae': holdout_mae,
                'generalization_gap': gen_gap,
                'model': model
            }
            results.append(result)
            
            print(f"   → CV MAE: ${cv_mae:.2f} ± ${cv_std:.2f}")
            print(f"   → Train MAE: ${train_mae:.2f}")
            print(f"   → Holdout MAE: ${holdout_mae:.2f}")
            print(f"   → Gen Gap: ${gen_gap:.2f} {'✅' if gen_gap < 5 else '⚠️'}")
            
        return results, X_holdout, y_holdout
    
    def select_generalizable_model(self, results):
        """Select model with best generalization, not best training performance"""
        print("\n🏆 Selecting Most Generalizable Model...")
        
        # Sort by generalization criteria
        # 1. Small generalization gap (most important)
        # 2. Low CV standard deviation (stable)
        # 3. Reasonable holdout performance
        
        # Filter out models with large generalization gaps
        good_generalizers = [r for r in results if r['generalization_gap'] < 10]
        
        if good_generalizers:
            # Among good generalizers, pick the most stable
            best = min(good_generalizers, key=lambda x: (x['generalization_gap'], x['cv_std']))
            print(f"✅ Selected: {best['name']}")
            print(f"   Generalization gap: ${best['generalization_gap']:.2f}")
            print(f"   CV stability: ±${best['cv_std']:.2f}")
            print(f"   Holdout MAE: ${best['holdout_mae']:.2f}")
        else:
            # Fallback to best holdout performance
            best = min(results, key=lambda x: x['holdout_mae'])
            print(f"⚠️  Fallback: {best['name']} (best holdout performance)")
            print(f"   Holdout MAE: ${best['holdout_mae']:.2f}")
        
        return best
    
    def evaluate_on_full_public_set(self, best_model, X, y):
        """Evaluate the generalizable model on full public set"""
        print("\n📊 Evaluating Generalizable Model on Full Public Set...")
        
        # Retrain on full dataset
        model = best_model['model']
        model.fit(X, y)
        
        predictions = model.predict(X)
        mae = mean_absolute_error(y, predictions)
        errors = np.abs(predictions - y)
        exact_matches = np.sum(errors < 0.01)
        close_matches = np.sum(errors < 1.0)
        
        print(f"📈 Generalizable Model Performance:")
        print(f"   MAE: ${mae:.2f}")
        print(f"   Exact matches: {exact_matches}/1000 ({exact_matches/10:.1f}%)")
        print(f"   Close matches: {close_matches}/1000 ({close_matches/10:.1f}%)")
        print(f"   Max error: ${np.max(errors):.2f}")
        
        # Compare to our "perfect" model
        print(f"\n🔍 Comparison to Perfect Model:")
        print(f"   Perfect model: 1000 exact matches (100%)")
        print(f"   Generalizable: {exact_matches} exact matches ({exact_matches/10:.1f}%)")
        print(f"   Trade-off: -{1000-exact_matches} exact matches for better generalization")
        
        return {
            'mae': mae,
            'exact_matches': exact_matches,
            'close_matches': close_matches,
            'max_error': np.max(errors),
            'model': model
        }
    
    def create_generalizable_calculator(self, model_data, feature_count):
        """Create calculator optimized for generalization"""
        print("\n💾 Creating Generalizable Calculator...")
        
        # Save generalizable model
        generalizable_data = {
            'model': model_data['model'],
            'performance': {
                'mae': model_data['mae'],
                'exact_matches': model_data['exact_matches'],
                'close_matches': model_data['close_matches']
            },
            'feature_count': feature_count,
            'version': 'GENERALIZABLE_ANTI_OVERFITTING'
        }
        
        joblib.dump(generalizable_data, 'generalizable_model.pkl')
        print("✅ Saved generalizable_model.pkl")
        
        # Create generalizable calculator
        calculator_code = '''#!/usr/bin/env python3
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
'''
        
        with open('generalizable_calculator.py', 'w') as f:
            f.write(calculator_code)
        
        print("✅ Created generalizable_calculator.py")
        
        return generalizable_data
    
    def run_anti_overfitting_optimization(self):
        """Run complete anti-overfitting optimization"""
        start_time = time.time()
        
        print("\n🛡️ ANTI-OVERFITTING OPTIMIZATION PIPELINE")
        print("=" * 50)
        
        # Step 1: Create simple features
        X = self.create_simple_features(self.df)
        y = self.df['expected_output'].values
        print(f"✅ Created {X.shape[1]} simple features (vs 15+ complex features)")
        
        # Step 2: Test generalization-focused configurations
        results, X_holdout, y_holdout = self.test_generalization_configs(X, y)
        
        # Step 3: Select most generalizable model
        best_model = self.select_generalizable_model(results)
        
        # Step 4: Evaluate on full public set
        performance = self.evaluate_on_full_public_set(best_model, X, y)
        
        # Step 5: Create generalizable calculator
        generalizable_data = self.create_generalizable_calculator(performance, X.shape[1])
        
        elapsed = time.time() - start_time
        print(f"\n🏁 ANTI-OVERFITTING OPTIMIZATION COMPLETE in {elapsed:.1f} seconds")
        print(f"🎯 Model optimized for GENERALIZATION over training performance!")
        
        return generalizable_data

if __name__ == "__main__":
    optimizer = AntiOverfittingOptimizer()
    results = optimizer.run_anti_overfitting_optimization() 