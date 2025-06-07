#!/usr/bin/env python3
"""
Private Set Enhancer - Build on perfect score model with robustness techniques
"""

import json
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import cross_val_score, KFold
import joblib
import time
import warnings
warnings.filterwarnings('ignore')

class PrivateSetEnhancer:
    def __init__(self):
        print("🎯 Private Set Enhancer - Building on Perfect Score Model")
        print("=" * 55)
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
        
    def create_robust_features(self, df):
        """Enhanced feature engineering with robustness techniques"""
        print("🔧 Creating robust feature matrix...")
        X = []
        
        for _, row in df.iterrows():
            duration = row['trip_duration_days']
            miles = row['miles_traveled']
            receipts = row['total_receipts_amount']
            
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
            
            X.append(base_features + robust_features)
        
        return np.array(X)
    
    def test_robustness_configs(self, X, y):
        """Test multiple configurations optimized for generalization"""
        print("\n⚙️ Testing Robustness Configurations...")
        
        # Configurations optimized for generalization (less overfitting)
        configs = [
            # Current perfect score config
            {'n_estimators': 750, 'max_depth': 15, 'learning_rate': 0.02, 'subsample': 0.98},
            
            # More conservative (less overfitting)
            {'n_estimators': 500, 'max_depth': 10, 'learning_rate': 0.05, 'subsample': 0.9},
            {'n_estimators': 600, 'max_depth': 12, 'learning_rate': 0.03, 'subsample': 0.95},
            
            # Higher regularization
            {'n_estimators': 800, 'max_depth': 8, 'learning_rate': 0.02, 'subsample': 0.85},
            {'n_estimators': 1000, 'max_depth': 6, 'learning_rate': 0.01, 'subsample': 0.9},
            
            # Balanced approach
            {'n_estimators': 700, 'max_depth': 14, 'learning_rate': 0.025, 'subsample': 0.92}
        ]
        
        results = []
        kfold = KFold(n_splits=10, shuffle=True, random_state=42)  # More folds for better CV
        
        for i, config in enumerate(configs):
            print(f"⏳ Config {i+1}/{len(configs)}: {config}")
            
            model = GradientBoostingRegressor(random_state=42, **config)
            
            # Cross-validation for generalization estimate
            cv_scores = cross_val_score(model, X, y, cv=kfold, scoring='neg_mean_absolute_error')
            cv_mae = -cv_scores.mean()
            cv_std = cv_scores.std()
            
            # Train on full data for exact match evaluation
            model.fit(X, y)
            train_pred = model.predict(X)
            train_mae = np.mean(np.abs(train_pred - y))
            exact_matches = np.sum(np.abs(train_pred - y) < 0.01)
            
            result = {
                'config': config,
                'cv_mae': cv_mae,
                'cv_std': cv_std,
                'train_mae': train_mae,
                'exact_matches': exact_matches,
                'model': model,
                'generalization_gap': train_mae - cv_mae  # Lower is better
            }
            results.append(result)
            
            print(f"   → CV MAE: ${cv_mae:.4f} ± ${cv_std:.4f}")
            print(f"   → Train MAE: ${train_mae:.6f}")
            print(f"   → Exact: {exact_matches}/1000")
            print(f"   → Gap: ${result['generalization_gap']:.4f}")
            
        return results
    
    def select_best_model(self, results):
        """Select model with best generalization potential"""
        print("\n🏆 Selecting Best Model for Private Set...")
        
        # Sort by multiple criteria
        # 1. Exact matches (must be high)
        # 2. Small generalization gap (good for private set)
        # 3. Low CV standard deviation (stable)
        
        high_exact = [r for r in results if r['exact_matches'] >= 900]  # Must have high accuracy
        
        if high_exact:
            # Among high-accuracy models, pick the one with best generalization
            best = min(high_exact, key=lambda x: (x['generalization_gap'], x['cv_std']))
            print(f"✅ Selected model with {best['exact_matches']} exact matches")
            print(f"   Generalization gap: ${best['generalization_gap']:.4f}")
            print(f"   CV stability: ±${best['cv_std']:.4f}")
        else:
            # Fallback to best exact matches
            best = max(results, key=lambda x: x['exact_matches'])
            print(f"⚠️  Fallback: Best exact matches = {best['exact_matches']}")
        
        return best
    
    def create_enhanced_calculator(self, best_model, feature_count):
        """Create enhanced calculator for private set"""
        print("\n💾 Creating Enhanced Calculator...")
        
        # Save the enhanced model
        enhanced_data = {
            'model': best_model['model'],
            'config': best_model['config'],
            'feature_count': feature_count,
            'performance': {
                'exact_matches': best_model['exact_matches'],
                'cv_mae': best_model['cv_mae'],
                'generalization_gap': best_model['generalization_gap']
            }
        }
        
        joblib.dump(enhanced_data, 'enhanced_private_model.pkl')
        print("✅ Saved enhanced_private_model.pkl")
        
        # Create enhanced calculator script
        calculator_code = '''#!/usr/bin/env python3
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
'''
        
        with open('enhanced_calculator.py', 'w') as f:
            f.write(calculator_code)
        
        print("✅ Created enhanced_calculator.py")
        
        return enhanced_data
    
    def run_enhancement(self):
        """Run complete enhancement pipeline"""
        start_time = time.time()
        
        # Step 1: Create robust features
        X = self.create_robust_features(self.df)
        y = self.df['expected_output'].values
        print(f"✅ Created {X.shape[1]} robust features")
        
        # Step 2: Test configurations
        results = self.test_robustness_configs(X, y)
        
        # Step 3: Select best model
        best_model = self.select_best_model(results)
        
        # Step 4: Create enhanced calculator
        enhanced_data = self.create_enhanced_calculator(best_model, X.shape[1])
        
        elapsed = time.time() - start_time
        print(f"\n🏁 Enhancement Complete in {elapsed:.1f} seconds")
        print(f"🚀 Enhanced model ready for private set!")
        
        return enhanced_data

if __name__ == "__main__":
    enhancer = PrivateSetEnhancer()
    results = enhancer.run_enhancement() 