#!/usr/bin/env python3
"""
Ultra Private Set Optimizer - Advanced ensemble and hyperparameter optimization
for maximizing performance on unseen private test cases
"""

import json
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor, ExtraTreesRegressor
from sklearn.model_selection import cross_val_score, KFold
from sklearn.metrics import mean_absolute_error
import joblib
import time
from itertools import product
import warnings
warnings.filterwarnings('ignore')

class UltraPrivateOptimizer:
    def __init__(self):
        print("🚀 Ultra Private Set Optimizer - Advanced Ensemble Approach")
        print("=" * 60)
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
        
    def create_advanced_features(self, df):
        """Create 25+ advanced engineered features for maximum generalization"""
        print("🔧 Creating advanced feature matrix (25+ features)...")
        X = []
        
        for _, row in df.iterrows():
            duration = row['trip_duration_days']
            miles = row['miles_traveled']
            receipts = row['total_receipts_amount']
            
            # Original 15 features
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
            
            # Advanced features for better generalization
            advanced_features = [
                # Efficiency ratios
                miles / (duration * receipts + 1),
                receipts / (miles + 1),
                duration / (miles + 1),
                
                # Polynomial combinations
                duration ** 3,
                miles ** (1/3),
                receipts ** 0.5,
                
                # Logarithmic combinations
                np.log1p(duration),
                np.log1p(miles * receipts),
                np.log1p(duration * receipts),
                
                # Trigonometric features (for cyclical patterns)
                np.sin(duration / 7.0),  # Weekly patterns
                np.cos(duration / 7.0),
                
                # Interaction terms
                duration * miles * receipts,
                (duration + miles) / (receipts + 1),
                (miles + receipts) / (duration + 1),
                
                # Binning indicators
                1 if duration <= 3 else 0,  # Short trips
                1 if duration >= 8 else 0,  # Long trips
                1 if (miles / duration > 200 if duration > 0 else False) else 0,  # High efficiency
                1 if (receipts / duration > 100 if duration > 0 else False) else 0,  # High spending
                
                # Outlier indicators
                1 if miles > 1000 else 0,
                1 if receipts > 500 else 0,
                1 if duration > 10 else 0
            ]
            
            X.append(base_features + advanced_features)
        
        return np.array(X)
    
    def optimize_hyperparameters(self, X, y):
        """Advanced hyperparameter optimization with cross-validation"""
        print("\n⚙️ Advanced Hyperparameter Optimization...")
        
        # Expanded parameter grid for thorough search
        param_combinations = [
            # Ultra-precise configurations
            {'n_estimators': 1000, 'max_depth': 20, 'learning_rate': 0.01, 'subsample': 0.99},
            {'n_estimators': 1500, 'max_depth': 15, 'learning_rate': 0.008, 'subsample': 0.98},
            {'n_estimators': 2000, 'max_depth': 12, 'learning_rate': 0.005, 'subsample': 0.97},
            
            # Balanced configurations
            {'n_estimators': 800, 'max_depth': 25, 'learning_rate': 0.015, 'subsample': 0.95},
            {'n_estimators': 1200, 'max_depth': 18, 'learning_rate': 0.012, 'subsample': 0.96},
            
            # High-capacity configurations
            {'n_estimators': 3000, 'max_depth': 10, 'learning_rate': 0.003, 'subsample': 0.99},
        ]
        
        best_score = float('inf')
        best_params = None
        best_model = None
        
        kfold = KFold(n_splits=5, shuffle=True, random_state=42)
        
        for i, params in enumerate(param_combinations):
            print(f"⏳ Testing config {i+1}/{len(param_combinations)}: {params}")
            
            model = GradientBoostingRegressor(random_state=42, **params)
            
            # Cross-validation score
            cv_scores = cross_val_score(model, X, y, cv=kfold, scoring='neg_mean_absolute_error')
            cv_mae = -cv_scores.mean()
            
            print(f"   → CV MAE: ${cv_mae:.4f}")
            
            if cv_mae < best_score:
                best_score = cv_mae
                best_params = params
                # Train on full dataset
                model.fit(X, y)
                best_model = model
                print(f"   ✅ NEW BEST: ${cv_mae:.4f}")
        
        print(f"\n🏆 Best CV MAE: ${best_score:.4f}")
        print(f"🏆 Best params: {best_params}")
        
        return best_model, best_params, best_score
    
    def create_ensemble(self, X, y):
        """Create advanced ensemble of multiple high-precision models"""
        print("\n🎯 Creating Advanced Ensemble...")
        
        models = []
        weights = []
        
        # Model 1: Optimized Gradient Boosting
        gb_model, _, gb_score = self.optimize_hyperparameters(X, y)
        models.append(('gb', gb_model))
        weights.append(1.0 / (gb_score + 0.001))
        
        # Model 2: Extra Trees (different approach)
        et_model = ExtraTreesRegressor(
            n_estimators=1000, max_depth=20, random_state=42,
            min_samples_split=2, min_samples_leaf=1
        )
        et_model.fit(X, y)
        et_pred = et_model.predict(X)
        et_score = mean_absolute_error(y, et_pred)
        models.append(('et', et_model))
        weights.append(1.0 / (et_score + 0.001))
        print(f"Extra Trees MAE: ${et_score:.4f}")
        
        # Model 3: Random Forest (high variance reduction)
        rf_model = RandomForestRegressor(
            n_estimators=1500, max_depth=25, random_state=42,
            min_samples_split=2, min_samples_leaf=1
        )
        rf_model.fit(X, y)
        rf_pred = rf_model.predict(X)
        rf_score = mean_absolute_error(y, rf_pred)
        models.append(('rf', rf_model))
        weights.append(1.0 / (rf_score + 0.001))
        print(f"Random Forest MAE: ${rf_score:.4f}")
        
        # Normalize weights
        total_weight = sum(weights)
        weights = [w / total_weight for w in weights]
        
        print(f"📊 Ensemble weights: {dict(zip([m[0] for m in models], weights))}")
        
        return models, weights
    
    def evaluate_ensemble(self, models, weights, X, y):
        """Evaluate ensemble performance"""
        print("\n📈 Evaluating Ensemble Performance...")
        
        # Get predictions from each model
        predictions = []
        for name, model in models:
            pred = model.predict(X)
            predictions.append(pred)
        
        # Weighted ensemble prediction
        ensemble_pred = np.zeros(len(y))
        for i, (pred, weight) in enumerate(zip(predictions, weights)):
            ensemble_pred += weight * pred
        
        # Calculate metrics
        mae = mean_absolute_error(y, ensemble_pred)
        exact_matches = np.sum(np.abs(ensemble_pred - y) < 0.01)
        close_matches = np.sum(np.abs(ensemble_pred - y) < 1.0)
        
        print(f"🎯 Ensemble Results:")
        print(f"   MAE: ${mae:.6f}")
        print(f"   Exact matches: {exact_matches}/1000 ({exact_matches/10:.1f}%)")
        print(f"   Close matches: {close_matches}/1000 ({close_matches/10:.1f}%)")
        
        return ensemble_pred, mae, exact_matches
    
    def run_ultra_optimization(self):
        """Run complete ultra optimization pipeline"""
        start_time = time.time()
        
        # Step 1: Advanced feature engineering
        X = self.create_advanced_features(self.df)
        y = self.df['expected_output'].values
        print(f"✅ Created {X.shape[1]} features")
        
        # Step 2: Create ensemble
        models, weights = self.create_ensemble(X, y)
        
        # Step 3: Evaluate ensemble
        ensemble_pred, mae, exact_matches = self.evaluate_ensemble(models, weights, X, y)
        
        # Step 4: Save ultra-optimized model
        ultra_model = {
            'models': models,
            'weights': weights,
            'feature_count': X.shape[1]
        }
        joblib.dump(ultra_model, 'ultra_private_model.pkl')
        
        elapsed = time.time() - start_time
        print(f"\n🏁 Ultra Optimization Complete in {elapsed:.1f} seconds")
        print(f"🚀 Ready for private set evaluation!")
        
        return {
            'mae': mae,
            'exact_matches': exact_matches,
            'models': len(models),
            'features': X.shape[1]
        }

if __name__ == "__main__":
    optimizer = UltraPrivateOptimizer()
    results = optimizer.run_ultra_optimization() 