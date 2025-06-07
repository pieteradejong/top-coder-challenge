#!/usr/bin/env python3
"""
Balanced Generalization Optimizer - Find sweet spot between performance and generalization
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

class BalancedGeneralizationOptimizer:
    def __init__(self):
        print("⚖️ BALANCED GENERALIZATION OPTIMIZER")
        print("=" * 50)
        print("Finding sweet spot between performance and generalization")
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
        
    def create_balanced_features(self, df):
        """Create balanced features - more than simple, fewer than complex"""
        print("🔧 Creating balanced feature set...")
        X = []
        
        for _, row in df.iterrows():
            duration = row['trip_duration_days']
            miles = row['miles_traveled']
            receipts = row['total_receipts_amount']
            
            # Balanced feature set (12 features)
            features = [
                # Core features (3)
                duration, miles, receipts,
                
                # Essential ratios (3)
                miles / duration if duration > 0 else 0,    # Efficiency
                receipts / duration if duration > 0 else 0, # Daily spending
                miles / (receipts + 1),                     # Miles per dollar
                
                # Key transformations (3)
                np.log1p(receipts),                         # Diminishing returns
                np.log1p(miles),                            # Distance scaling
                np.sqrt(receipts),                          # Receipt scaling
                
                # Important interactions (3)
                duration * miles,                           # Trip complexity
                1 if duration >= 8 else 0,                 # Long trip penalty
                1 if duration == 5 else 0                  # 5-day bonus
            ]
            
            X.append(features)
        
        return np.array(X)
    
    def test_balanced_configs(self, X, y):
        """Test configurations that balance performance and generalization"""
        print("\n⚙️ Testing Balanced Configurations...")
        
        # Split data for honest evaluation
        X_train, X_holdout, y_train, y_holdout = train_test_split(
            X, y, test_size=0.2, random_state=42, shuffle=True
        )
        
        print(f"📊 Training: {len(X_train)} cases, Holdout: {len(X_holdout)} cases")
        
        # Balanced configurations - moderate complexity with regularization
        configs = [
            # Moderate complexity
            {'n_estimators': 200, 'max_depth': 8, 'learning_rate': 0.05, 'subsample': 0.9, 'name': 'Moderate_1'},
            {'n_estimators': 300, 'max_depth': 6, 'learning_rate': 0.08, 'subsample': 0.85, 'name': 'Moderate_2'},
            {'n_estimators': 400, 'max_depth': 7, 'learning_rate': 0.04, 'subsample': 0.9, 'name': 'Moderate_3'},
            
            # Higher performance with some regularization
            {'n_estimators': 500, 'max_depth': 10, 'learning_rate': 0.03, 'subsample': 0.95, 'name': 'Higher_Perf_1'},
            {'n_estimators': 600, 'max_depth': 8, 'learning_rate': 0.025, 'subsample': 0.9, 'name': 'Higher_Perf_2'},
            
            # Conservative but capable
            {'n_estimators': 250, 'max_depth': 5, 'learning_rate': 0.06, 'subsample': 0.85, 'name': 'Conservative'},
        ]
        
        results = []
        kfold = KFold(n_splits=5, shuffle=True, random_state=42)
        
        for config in configs:
            name = config.pop('name')
            print(f"⏳ Testing {name}: {config}")
            
            # Add moderate regularization
            model = GradientBoostingRegressor(
                random_state=42,
                min_samples_split=5,     # Moderate regularization
                min_samples_leaf=3,      # Moderate regularization
                max_features=0.8,        # Use most features but not all
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
            train_exact = np.sum(np.abs(train_pred - y_train) < 0.01)
            
            # Holdout performance (honest evaluation)
            holdout_pred = model.predict(X_holdout)
            holdout_mae = mean_absolute_error(y_holdout, holdout_pred)
            holdout_exact = np.sum(np.abs(holdout_pred - y_holdout) < 0.01)
            
            # Generalization metrics
            gen_gap = holdout_mae - train_mae
            exact_retention = holdout_exact / max(train_exact, 1) if train_exact > 0 else 0
            
            result = {
                'name': name,
                'config': config,
                'cv_mae': cv_mae,
                'cv_std': cv_std,
                'train_mae': train_mae,
                'holdout_mae': holdout_mae,
                'train_exact': train_exact,
                'holdout_exact': holdout_exact,
                'generalization_gap': gen_gap,
                'exact_retention': exact_retention,
                'model': model
            }
            results.append(result)
            
            print(f"   → CV MAE: ${cv_mae:.2f} ± ${cv_std:.2f}")
            print(f"   → Train: ${train_mae:.2f} ({train_exact} exact)")
            print(f"   → Holdout: ${holdout_mae:.2f} ({holdout_exact} exact)")
            print(f"   → Gen Gap: ${gen_gap:.2f} {'✅' if gen_gap < 20 else '⚠️'}")
            print(f"   → Exact Retention: {exact_retention:.1%}")
            
        return results, X_holdout, y_holdout
    
    def select_balanced_model(self, results):
        """Select model with best balance of performance and generalization"""
        print("\n⚖️ Selecting Best Balanced Model...")
        
        # Score models based on multiple criteria
        for result in results:
            # Composite score: balance performance and generalization
            performance_score = 100 - result['holdout_mae']  # Higher is better
            generalization_score = max(0, 50 - result['generalization_gap'])  # Lower gap is better
            stability_score = max(0, 20 - result['cv_std'])  # Lower std is better
            exact_score = result['holdout_exact'] * 2  # Exact matches bonus
            
            result['composite_score'] = (
                performance_score * 0.4 +      # 40% performance
                generalization_score * 0.3 +   # 30% generalization
                stability_score * 0.2 +        # 20% stability
                exact_score * 0.1              # 10% exact matches
            )
        
        # Select best composite score
        best = max(results, key=lambda x: x['composite_score'])
        
        print(f"✅ Selected: {best['name']}")
        print(f"   Composite Score: {best['composite_score']:.1f}")
        print(f"   Holdout MAE: ${best['holdout_mae']:.2f}")
        print(f"   Generalization Gap: ${best['generalization_gap']:.2f}")
        print(f"   Holdout Exact: {best['holdout_exact']}")
        print(f"   CV Stability: ±${best['cv_std']:.2f}")
        
        return best
    
    def evaluate_balanced_model(self, best_model, X, y):
        """Evaluate the balanced model on full public set"""
        print("\n📊 Evaluating Balanced Model on Full Public Set...")
        
        # Retrain on full dataset
        model = best_model['model']
        model.fit(X, y)
        
        predictions = model.predict(X)
        mae = mean_absolute_error(y, predictions)
        errors = np.abs(predictions - y)
        exact_matches = np.sum(errors < 0.01)
        close_matches = np.sum(errors < 1.0)
        
        print(f"📈 Balanced Model Performance:")
        print(f"   MAE: ${mae:.2f}")
        print(f"   Exact matches: {exact_matches}/1000 ({exact_matches/10:.1f}%)")
        print(f"   Close matches: {close_matches}/1000 ({close_matches/10:.1f}%)")
        print(f"   Max error: ${np.max(errors):.2f}")
        
        # Compare to perfect and anti-overfitting models
        print(f"\n🔍 Model Comparison:")
        print(f"   Perfect Model:      1000 exact (100%) - High overfitting risk")
        print(f"   Anti-Overfitting:   0 exact (0%) - Low overfitting risk")
        print(f"   Balanced Model:     {exact_matches} exact ({exact_matches/10:.1f}%) - Moderate risk")
        
        return {
            'mae': mae,
            'exact_matches': exact_matches,
            'close_matches': close_matches,
            'max_error': np.max(errors),
            'model': model
        }
    
    def create_balanced_calculator(self, model_data, feature_count, best_config):
        """Create calculator with balanced approach"""
        print("\n💾 Creating Balanced Calculator...")
        
        # Save balanced model
        balanced_data = {
            'model': model_data['model'],
            'config': best_config,
            'performance': {
                'mae': model_data['mae'],
                'exact_matches': model_data['exact_matches'],
                'close_matches': model_data['close_matches']
            },
            'feature_count': feature_count,
            'version': 'BALANCED_GENERALIZATION'
        }
        
        joblib.dump(balanced_data, 'balanced_model.pkl')
        print("✅ Saved balanced_model.pkl")
        
        # Create balanced calculator
        calculator_code = '''#!/usr/bin/env python3
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
'''
        
        with open('balanced_calculator.py', 'w') as f:
            f.write(calculator_code)
        
        print("✅ Created balanced_calculator.py")
        
        return balanced_data
    
    def run_balanced_optimization(self):
        """Run complete balanced optimization"""
        start_time = time.time()
        
        print("\n⚖️ BALANCED OPTIMIZATION PIPELINE")
        print("=" * 45)
        
        # Step 1: Create balanced features
        X = self.create_balanced_features(self.df)
        y = self.df['expected_output'].values
        print(f"✅ Created {X.shape[1]} balanced features")
        
        # Step 2: Test balanced configurations
        results, X_holdout, y_holdout = self.test_balanced_configs(X, y)
        
        # Step 3: Select best balanced model
        best_model = self.select_balanced_model(results)
        
        # Step 4: Evaluate on full public set
        performance = self.evaluate_balanced_model(best_model, X, y)
        
        # Step 5: Create balanced calculator
        balanced_data = self.create_balanced_calculator(performance, X.shape[1], best_model['config'])
        
        elapsed = time.time() - start_time
        print(f"\n🏁 BALANCED OPTIMIZATION COMPLETE in {elapsed:.1f} seconds")
        print(f"⚖️ Model balances performance and generalization!")
        
        return balanced_data

if __name__ == "__main__":
    optimizer = BalancedGeneralizationOptimizer()
    results = optimizer.run_balanced_optimization() 