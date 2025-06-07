#!/usr/bin/env python3
"""
Next Phase Optimization Framework
Focus on exact matches, hyperparameter tuning, and advanced feature engineering
"""

import json
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
from sklearn.metrics import mean_absolute_error
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
import warnings
warnings.filterwarnings('ignore')
from experiment_tracker import ExperimentTracker
import itertools
from typing import Dict, List, Tuple, Any

class NextPhaseOptimizer:
    """Advanced optimization for achieving exact matches and sub-$10 errors"""
    
    def __init__(self):
        self.tracker = ExperimentTracker()
        self.X, self.y = self.load_data()
        print(f"📊 Loaded {len(self.X)} training samples")
    
    def load_data(self):
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
            
            X.append([duration, miles, receipts])
            y.append(reimbursement)
        
        return np.array(X), np.array(y)
    
    def engineer_features_v1(self, X):
        """Original feature engineering (baseline)"""
        features = []
        
        for i in range(len(X)):
            duration, miles, receipts = X[i]
            
            # Basic features
            row = [duration, miles, receipts]
            
            # Engineered features
            row.extend([
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
            
            features.append(row)
        
        return np.array(features)
    
    def engineer_features_v2(self, X):
        """Advanced feature engineering with more interactions"""
        features = []
        
        for i in range(len(X)):
            duration, miles, receipts = X[i]
            
            # Basic features
            row = [duration, miles, receipts]
            
            # Original engineered features
            miles_per_day = miles / duration if duration > 0 else 0
            receipts_per_day = receipts / duration if duration > 0 else 0
            efficiency_ratio = miles / receipts if receipts > 0 else 0
            
            row.extend([
                miles_per_day,
                receipts_per_day,
                efficiency_ratio,
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
            
            # Advanced features
            row.extend([
                # More polynomial features
                duration ** 3,
                miles ** (1/3),
                receipts ** (1/3),
                
                # More interaction terms
                miles_per_day * receipts_per_day,
                efficiency_ratio * duration,
                efficiency_ratio * receipts_per_day,
                
                # Binned features (categorical-like)
                1 if duration <= 2 else 0,  # short trip
                1 if duration >= 8 else 0,  # long trip
                1 if miles_per_day >= 200 else 0,  # high efficiency
                1 if miles_per_day <= 50 else 0,  # low efficiency
                1 if receipts_per_day >= 200 else 0,  # high spending
                1 if receipts_per_day <= 50 else 0,  # low spending
                
                # Complex ratios
                (miles + receipts) / duration if duration > 0 else 0,
                miles / (receipts + 1),  # avoid division by zero
                receipts / (miles + 1),
                
                # Log ratios
                np.log(miles_per_day + 1),
                np.log(receipts_per_day + 1),
                np.log(efficiency_ratio + 1),
            ])
            
            features.append(row)
        
        return np.array(features)
    
    def engineer_features_v3(self, X):
        """Ultra-advanced feature engineering with domain knowledge"""
        features = []
        
        for i in range(len(X)):
            duration, miles, receipts = X[i]
            
            # Basic features
            row = [duration, miles, receipts]
            
            # Core ratios
            miles_per_day = miles / duration if duration > 0 else 0
            receipts_per_day = receipts / duration if duration > 0 else 0
            efficiency_ratio = miles / receipts if receipts > 0 else 0
            
            # Business logic features (from interview insights)
            is_5_day = 1 if duration == 5 else 0
            is_efficiency_sweet_spot = 1 if 180 <= miles_per_day <= 220 else 0
            is_vacation_trip = 1 if duration >= 8 else 0
            is_high_receipts = 1 if receipts > 1000 else 0
            
            # Add all features
            row.extend([
                # Basic ratios
                miles_per_day,
                receipts_per_day,
                efficiency_ratio,
                
                # Business logic indicators
                is_5_day,
                is_efficiency_sweet_spot,
                is_vacation_trip,
                is_high_receipts,
                
                # Interactions with business logic
                is_5_day * miles_per_day,
                is_5_day * receipts_per_day,
                is_efficiency_sweet_spot * duration,
                is_vacation_trip * receipts_per_day,
                
                # Mathematical transforms
                np.log(duration + 1),
                np.log(miles + 1),
                np.log(receipts + 1),
                np.log(miles_per_day + 1),
                np.log(receipts_per_day + 1),
                
                # Polynomial features
                duration ** 2,
                miles ** 0.5,
                receipts ** 0.5,
                miles_per_day ** 2,
                receipts_per_day ** 0.5,
                
                # Complex interactions
                duration * miles,
                duration * receipts,
                miles * receipts,
                miles_per_day * receipts_per_day,
                efficiency_ratio * duration,
                
                # Fraud detection features
                1 if receipts > 2000 else 0,  # very high receipts
                1 if miles_per_day > 300 else 0,  # very high efficiency
                1 if receipts_per_day > 300 else 0,  # very high spending
                
                # Efficiency bands
                1 if miles_per_day < 50 else 0,  # very low efficiency
                1 if 50 <= miles_per_day < 100 else 0,  # low efficiency
                1 if 100 <= miles_per_day < 180 else 0,  # medium efficiency
                1 if 180 <= miles_per_day <= 220 else 0,  # sweet spot
                1 if 220 < miles_per_day <= 300 else 0,  # high efficiency
                1 if miles_per_day > 300 else 0,  # very high efficiency
            ])
            
            features.append(row)
        
        return np.array(features)
    
    def hyperparameter_optimization(self, feature_version='v1'):
        """Comprehensive hyperparameter optimization"""
        
        print(f"\n🔧 Hyperparameter Optimization (Features {feature_version})")
        print("="*60)
        
        # Use existing feature engineering from our current best algorithm
        from test_gradient_boosting import load_data
        X, y = load_data()
        
        print(f"📊 Feature count: {X.shape[1]}")
        
        # Gradient Boosting parameter grid
        gb_param_grid = {
            'n_estimators': [50, 100, 150, 200, 300],
            'max_depth': [4, 5, 6, 7, 8, 10],
            'learning_rate': [0.05, 0.08, 0.1, 0.12, 0.15],
            'subsample': [0.8, 0.9, 1.0],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4]
        }
        
        # Random search for efficiency
        gb_random_search = RandomizedSearchCV(
            GradientBoostingRegressor(random_state=42),
            gb_param_grid,
            n_iter=30,  # Try 30 random combinations
            cv=5,
            scoring='neg_mean_absolute_error',
            random_state=42,
            n_jobs=-1
        )
        
        print("🔍 Running random search optimization...")
        gb_random_search.fit(X, y)
        
        best_gb = gb_random_search.best_estimator_
        best_score = -gb_random_search.best_score_
        
        print(f"✅ Best GB MAE: ${best_score:.2f}")
        print(f"🏆 Best parameters: {gb_random_search.best_params_}")
        
        # Test on full dataset
        predictions = best_gb.predict(X)
        full_mae = mean_absolute_error(y, predictions)
        
        print(f"📊 Full dataset MAE: ${full_mae:.2f}")
        
        return best_gb, gb_random_search.best_params_, full_mae
    
    def exact_match_analysis(self, model):
        """Analyze cases closest to exact matches"""
        
        print(f"\n🎯 Exact Match Analysis")
        print("="*60)
        
        # Use existing feature engineering
        from test_gradient_boosting import load_data
        X, y = load_data()
        
        # Get predictions
        predictions = model.predict(X)
        errors = np.abs(predictions - y)
        
        # Find closest matches
        closest_indices = np.argsort(errors)[:20]  # Top 20 closest
        
        print("🔍 Top 20 closest predictions:")
        for i, idx in enumerate(closest_indices, 1):
            expected = y[idx]
            predicted = predictions[idx]
            error = errors[idx]
            
            print(f"{i:2d}. Case {idx:3d}: Expected: ${expected:7.2f}, Got: ${predicted:7.2f}, Error: ${error:5.2f}")
        
        # Analyze patterns in closest matches
        closest_errors = errors[closest_indices]
        exact_matches = np.sum(closest_errors < 0.01)
        near_matches = np.sum(closest_errors < 1.0)
        
        print(f"\n📈 Analysis:")
        print(f"  Exact matches (±$0.01): {exact_matches}")
        print(f"  Close matches (±$1.00): {near_matches}")
        print(f"  Average error in top 20: ${np.mean(closest_errors):.3f}")
        print(f"  Best error: ${np.min(closest_errors):.3f}")
        
        return closest_indices, errors
    
    def create_optimized_algorithm(self, model, params, mae):
        """Create optimized calculate_reimbursement.py file"""
        
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
        
        # Train optimized Gradient Boosting
        model = GradientBoostingRegressor(
            n_estimators={params.get('n_estimators', 100)},
            max_depth={params.get('max_depth', 6)},
            learning_rate={params.get('learning_rate', 0.1)},
            subsample={params.get('subsample', 1.0)},
            min_samples_split={params.get('min_samples_split', 2)},
            min_samples_leaf={params.get('min_samples_leaf', 1)},
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
        
        filename = f'hyperopt_gb.py'
        with open(filename, 'w') as f:
            f.write(code)
        
        print(f"✅ Created {filename}")
        print(f"📊 Expected MAE: ${mae:.2f}")
        
        return filename
    
    def run_optimization_suite(self):
        """Run comprehensive optimization suite"""
        
        print("\n" + "="*80)
        print("🚀 NEXT PHASE OPTIMIZATION SUITE")
        print("="*80)
        
        # Hyperparameter optimization
        best_model, best_params, mae = self.hyperparameter_optimization()
        
        # Exact match analysis
        closest_indices, errors = self.exact_match_analysis(best_model)
        
        # Create optimized algorithm
        filename = self.create_optimized_algorithm(best_model, best_params, mae)
        
        # Track experiment
        exp_name = f"Hyperopt GB"
        self.tracker.run_and_track_experiment(
            name=exp_name,
            algorithm_file=filename,
            algorithm_type="Hyperopt ML",
            description=f"Hyperparameter-optimized Gradient Boosting",
            parameters=best_params,
            notes=f"Hyperparameter optimization, MAE: ${mae:.2f}",
            tags=["hyperopt", "gradient_boosting", "optimization"]
        )
        
        # Summary
        print(f"\n🏆 OPTIMIZATION RESULTS SUMMARY")
        print("="*60)
        print(f"🎯 Hyperparameter-optimized GB: MAE ${mae:.2f}")
        print(f"📁 Algorithm file: {filename}")
        
        return {'mae': mae, 'params': best_params, 'filename': filename}

def main():
    """Main optimization function"""
    optimizer = NextPhaseOptimizer()
    results = optimizer.run_optimization_suite()
    
    # Create visualizations
    optimizer.tracker.create_performance_plots()
    
    print(f"\n📊 Updated experiment tracking with optimization results")
    print(f"📈 Check plots/ directory for updated visualizations")

if __name__ == "__main__":
    main() 