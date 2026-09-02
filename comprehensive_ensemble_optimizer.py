#!/usr/bin/env python3
"""
Comprehensive Ensemble Optimizer - Testing All Untested Approaches
================================================================

This script implements all the approaches we haven't tried yet:
1. Multiple Dozen Decision Trees (Bagging)
2. Voting Ensemble 
3. Stacking Ensemble
4. Cross-Validation Analysis for Optimal Complexity
5. Mathematical Pattern Analysis for Rule Discovery

Goal: Bridge the gap between 0.0000 public MAE and 8,124 private MAE
"""

import json
import numpy as np
import pandas as pd
from sklearn.ensemble import (
    BaggingRegressor, VotingRegressor, StackingRegressor,
    GradientBoostingRegressor, RandomForestRegressor, ExtraTreesRegressor
)
from sklearn.tree import DecisionTreeRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.model_selection import cross_val_score, GridSearchCV
from sklearn.metrics import mean_absolute_error
import pickle
import time
from datetime import datetime

class ComprehensiveEnsembleOptimizer:
    def __init__(self):
        self.results = {}
        self.models = {}
        self.best_model = None
        self.best_score = float('inf')
        
    def load_data(self):
        """Load and prepare the data"""
        print("📊 Loading data...")
        with open('public_cases.json', 'r') as f:
            cases = json.load(f)
        
        # Extract features and targets
        X = []
        y = []
        
        for case in cases:
            duration = case['input']['trip_duration_days']
            miles = case['input']['miles_traveled'] 
            receipts = case['input']['total_receipts_amount']
            target = case['expected_output']
            
            # Create comprehensive feature set (38 features)
            features = self.engineer_features(duration, miles, receipts)
            X.append(features)
            y.append(target)
            
        return np.array(X), np.array(y)
    
    def engineer_features(self, duration, miles, receipts):
        """Engineer comprehensive feature set"""
        features = [duration, miles, receipts]
        
        # Basic ratios
        features.extend([
            miles / duration if duration > 0 else 0,  # miles per day
            receipts / duration if duration > 0 else 0,  # receipts per day
            miles / receipts if receipts > 0 else 0,  # efficiency ratio
        ])
        
        # Interaction terms
        features.extend([
            duration * miles,
            duration * receipts, 
            miles * receipts,
            duration * miles * receipts,
        ])
        
        # Log transforms
        features.extend([
            np.log(duration + 1),
            np.log(miles + 1),
            np.log(receipts + 1),
        ])
        
        # Square root transforms
        features.extend([
            np.sqrt(duration),
            np.sqrt(miles),
            np.sqrt(receipts),
        ])
        
        # Polynomial features
        features.extend([
            duration ** 2,
            miles ** 2,
            receipts ** 2,
            duration ** 3,
            miles ** 0.5,
            receipts ** 0.5,
        ])
        
        # Inverse relationships
        features.extend([
            1 / (duration + 1),
            1 / (miles + 1), 
            1 / (receipts + 1),
        ])
        
        # Categorical encodings
        features.extend([
            1 if duration == 1 else 0,  # single day
            1 if duration <= 5 else 0,  # short trip
            1 if duration >= 8 else 0,  # long trip
            1 if miles < 100 else 0,    # low mileage
            1 if miles > 500 else 0,    # high mileage
            1 if receipts < 50 else 0,  # low receipts
            1 if receipts > 200 else 0, # high receipts
        ])
        
        # Business logic features
        features.extend([
            miles / duration if duration > 0 and 180 <= miles/duration <= 220 else 0,  # sweet spot
            1 if duration == 5 else 0,  # 5-day bonus
            max(0, receipts - 100 * duration),  # excess receipts
        ])
        
        return features

    def test_bagging_multiple_trees(self, X, y):
        """Test Multiple Dozen Decision Trees (Bagging)"""
        print("\n🌳 Testing Multiple Dozen Decision Trees (Bagging)...")
        
        # Test different configurations
        configs = [
            {'n_estimators': 24, 'max_depth': 15},
            {'n_estimators': 36, 'max_depth': 20}, 
            {'n_estimators': 48, 'max_depth': 25},
            {'n_estimators': 60, 'max_depth': None},
        ]
        
        best_bagging = None
        best_bagging_score = float('inf')
        
        for i, config in enumerate(configs):
            print(f"  Testing Config {i+1}: {config['n_estimators']} trees, depth {config['max_depth']}")
            
            model = BaggingRegressor(
                base_estimator=DecisionTreeRegressor(
                    max_depth=config['max_depth'],
                    min_samples_leaf=1
                ),
                n_estimators=config['n_estimators'],
                random_state=42,
                n_jobs=-1
            )
            
            # Cross-validation
            cv_scores = cross_val_score(model, X, y, cv=5, scoring='neg_mean_absolute_error')
            cv_mae = -cv_scores.mean()
            
            # Full training
            model.fit(X, y)
            train_pred = model.predict(X)
            train_mae = mean_absolute_error(y, train_pred)
            
            exact_matches = np.sum(np.abs(y - train_pred) < 0.01)
            close_matches = np.sum(np.abs(y - train_pred) < 1.0)
            
            result = {
                'config': config,
                'cv_mae': cv_mae,
                'train_mae': train_mae,
                'exact_matches': exact_matches,
                'close_matches': close_matches,
                'overfitting_ratio': cv_mae / train_mae if train_mae > 0 else float('inf')
            }
            
            print(f"    CV MAE: ${cv_mae:.2f}, Train MAE: ${train_mae:.2f}")
            print(f"    Exact: {exact_matches}, Close: {close_matches}")
            print(f"    Overfitting Ratio: {result['overfitting_ratio']:.2f}")
            
            if cv_mae < best_bagging_score:
                best_bagging_score = cv_mae
                best_bagging = model
                
            self.results[f'bagging_config_{i+1}'] = result
            
        self.models['best_bagging'] = best_bagging
        return best_bagging

    def test_voting_ensemble(self, X, y):
        """Test Voting Ensemble of Best Models"""
        print("\n🗳️ Testing Voting Ensemble...")
        
        # Create base models
        gb_model = GradientBoostingRegressor(
            n_estimators=400, max_depth=10, learning_rate=0.05,
            random_state=42
        )
        
        rf_model = RandomForestRegressor(
            n_estimators=300, max_depth=10,
            random_state=42, n_jobs=-1
        )
        
        et_model = ExtraTreesRegressor(
            n_estimators=300, max_depth=10,
            random_state=42, n_jobs=-1
        )
        
        # Test different voting strategies
        voting_models = {
            'voting_uniform': VotingRegressor([
                ('gb', gb_model), ('rf', rf_model), ('et', et_model)
            ]),
            'voting_weighted': VotingRegressor([
                ('gb', gb_model), ('rf', rf_model), ('et', et_model)
            ], weights=[0.5, 0.3, 0.2])  # Weight GB higher
        }
        
        best_voting = None
        best_voting_score = float('inf')
        
        for name, model in voting_models.items():
            print(f"  Testing {name}...")
            
            # Cross-validation
            cv_scores = cross_val_score(model, X, y, cv=5, scoring='neg_mean_absolute_error')
            cv_mae = -cv_scores.mean()
            
            # Full training
            model.fit(X, y)
            train_pred = model.predict(X)
            train_mae = mean_absolute_error(y, train_pred)
            
            exact_matches = np.sum(np.abs(y - train_pred) < 0.01)
            close_matches = np.sum(np.abs(y - train_pred) < 1.0)
            
            result = {
                'cv_mae': cv_mae,
                'train_mae': train_mae,
                'exact_matches': exact_matches,
                'close_matches': close_matches,
                'overfitting_ratio': cv_mae / train_mae if train_mae > 0 else float('inf')
            }
            
            print(f"    CV MAE: ${cv_mae:.2f}, Train MAE: ${train_mae:.2f}")
            print(f"    Exact: {exact_matches}, Close: {close_matches}")
            
            if cv_mae < best_voting_score:
                best_voting_score = cv_mae
                best_voting = model
                
            self.results[name] = result
            self.models[name] = model
            
        self.models['best_voting'] = best_voting
        return best_voting

    def test_stacking_ensemble(self, X, y):
        """Test Stacking Ensemble"""
        print("\n📚 Testing Stacking Ensemble...")
        
        # Base models
        base_models = [
            ('gb', GradientBoostingRegressor(n_estimators=400, max_depth=10, random_state=42)),
            ('rf', RandomForestRegressor(n_estimators=300, max_depth=10, random_state=42)),
            ('et', ExtraTreesRegressor(n_estimators=300, max_depth=10, random_state=42)),
        ]
        
        # Test different meta-learners
        meta_learners = {
            'stacking_linear': LinearRegression(),
            'stacking_ridge': Ridge(alpha=1.0),
            'stacking_gb': GradientBoostingRegressor(n_estimators=50, max_depth=3, random_state=42)
        }
        
        best_stacking = None
        best_stacking_score = float('inf')
        
        for name, meta_learner in meta_learners.items():
            print(f"  Testing {name}...")
            
            model = StackingRegressor(
                estimators=base_models,
                final_estimator=meta_learner,
                cv=3,  # Use 3-fold CV for stacking
                n_jobs=-1
            )
            
            # Cross-validation
            cv_scores = cross_val_score(model, X, y, cv=5, scoring='neg_mean_absolute_error')
            cv_mae = -cv_scores.mean()
            
            # Full training
            model.fit(X, y)
            train_pred = model.predict(X)
            train_mae = mean_absolute_error(y, train_pred)
            
            exact_matches = np.sum(np.abs(y - train_pred) < 0.01)
            close_matches = np.sum(np.abs(y - train_pred) < 1.0)
            
            result = {
                'cv_mae': cv_mae,
                'train_mae': train_mae,
                'exact_matches': exact_matches,
                'close_matches': close_matches,
                'overfitting_ratio': cv_mae / train_mae if train_mae > 0 else float('inf')
            }
            
            print(f"    CV MAE: ${cv_mae:.2f}, Train MAE: ${train_mae:.2f}")
            print(f"    Exact: {exact_matches}, Close: {close_matches}")
            
            if cv_mae < best_stacking_score:
                best_stacking_score = cv_mae
                best_stacking = model
                
            self.results[name] = result
            self.models[name] = model
            
        self.models['best_stacking'] = best_stacking
        return best_stacking

    def analyze_mathematical_patterns(self, X, y):
        """Analyze mathematical patterns in the data"""
        print("\n🔍 Analyzing Mathematical Patterns...")
        
        with open('public_cases.json', 'r') as f:
            cases = json.load(f)
        
        # Create DataFrame for analysis
        df = pd.DataFrame([
            {
                'duration': case['trip_duration_days'],
                'miles': case['miles_traveled'],
                'receipts': case['total_receipts_amount'],
                'reimbursement': case['expected_reimbursement']
            }
            for case in cases
        ])
        
        # Add derived features
        df['miles_per_day'] = df['miles'] / df['duration']
        df['receipts_per_day'] = df['receipts'] / df['duration']
        df['efficiency_ratio'] = df['miles'] / df['receipts']
        df['reimbursement_per_day'] = df['reimbursement'] / df['duration']
        
        patterns = {}
        
        # Pattern 1: Per-day rates by duration
        print("  Analyzing per-day rates by duration...")
        duration_analysis = df.groupby('duration').agg({
            'reimbursement_per_day': ['mean', 'std', 'min', 'max', 'count']
        }).round(2)
        patterns['duration_rates'] = duration_analysis.to_dict()
        
        # Pattern 2: Mileage rate analysis
        print("  Analyzing mileage patterns...")
        df['mileage_rate'] = df['reimbursement'] / df['miles']
        mileage_bins = pd.cut(df['miles'], bins=[0, 100, 300, 500, 1000, 2000], labels=['0-100', '100-300', '300-500', '500-1000', '1000+'])
        mileage_analysis = df.groupby(mileage_bins).agg({
            'mileage_rate': ['mean', 'std', 'count']
        }).round(3)
        patterns['mileage_rates'] = mileage_analysis.to_dict()
        
        # Pattern 3: Receipt rate analysis
        print("  Analyzing receipt patterns...")
        df['receipt_rate'] = df['reimbursement'] / df['receipts']
        receipt_bins = pd.cut(df['receipts'], bins=[0, 50, 100, 200, 500, 1000], labels=['0-50', '50-100', '100-200', '200-500', '500+'])
        receipt_analysis = df.groupby(receipt_bins).agg({
            'receipt_rate': ['mean', 'std', 'count']
        }).round(3)
        patterns['receipt_rates'] = receipt_analysis.to_dict()
        
        # Pattern 4: Efficiency sweet spots
        print("  Analyzing efficiency sweet spots...")
        efficiency_bins = pd.cut(df['miles_per_day'], bins=[0, 50, 100, 150, 200, 250, 300, 500], 
                                labels=['0-50', '50-100', '100-150', '150-200', '200-250', '250-300', '300+'])
        efficiency_analysis = df.groupby(efficiency_bins).agg({
            'reimbursement_per_day': ['mean', 'std', 'count']
        }).round(2)
        patterns['efficiency_sweet_spots'] = efficiency_analysis.to_dict()
        
        # Pattern 5: Exact mathematical relationships
        print("  Looking for exact mathematical relationships...")
        
        # Test inverse relationship: reimbursement = a/duration + b
        from scipy.optimize import curve_fit
        
        def inverse_func(duration, a, b):
            return a / duration + b
            
        try:
            popt, _ = curve_fit(inverse_func, df['duration'], df['reimbursement_per_day'])
            r_squared = 1 - np.sum((df['reimbursement_per_day'] - inverse_func(df['duration'], *popt))**2) / np.sum((df['reimbursement_per_day'] - df['reimbursement_per_day'].mean())**2)
            patterns['inverse_relationship'] = {
                'formula': f'reimbursement_per_day = {popt[0]:.2f} / duration + {popt[1]:.2f}',
                'r_squared': r_squared,
                'parameters': {'a': popt[0], 'b': popt[1]}
            }
            print(f"    Found inverse relationship: R² = {r_squared:.4f}")
        except:
            patterns['inverse_relationship'] = {'error': 'Could not fit inverse relationship'}
        
        # Save patterns
        with open('mathematical_patterns.json', 'w') as f:
            json.dump(patterns, f, indent=2, default=str)
            
        self.results['mathematical_patterns'] = patterns
        return patterns

    def cross_validation_complexity_analysis(self, X, y):
        """Systematic CV analysis to find optimal complexity"""
        print("\n📊 Cross-Validation Complexity Analysis...")
        
        # Test different complexity levels for Gradient Boosting
        param_grid = {
            'n_estimators': [100, 300, 500, 750, 1000],
            'max_depth': [3, 6, 10, 15, 20],
            'learning_rate': [0.01, 0.05, 0.1, 0.2],
            'min_samples_leaf': [1, 2, 5, 10]
        }
        
        print("  Testing Gradient Boosting complexity...")
        gb_model = GradientBoostingRegressor(random_state=42)
        
        # Use smaller grid for speed
        reduced_grid = {
            'n_estimators': [300, 500, 750],
            'max_depth': [6, 10, 15],
            'learning_rate': [0.02, 0.05, 0.1]
        }
        
        grid_search = GridSearchCV(
            gb_model, reduced_grid, cv=5, 
            scoring='neg_mean_absolute_error',
            n_jobs=-1, verbose=1
        )
        
        grid_search.fit(X, y)
        
        best_params = grid_search.best_params_
        best_cv_score = -grid_search.best_score_
        
        # Test best model
        best_model = grid_search.best_estimator_
        train_pred = best_model.predict(X)
        train_mae = mean_absolute_error(y, train_pred)
        
        exact_matches = np.sum(np.abs(y - train_pred) < 0.01)
        close_matches = np.sum(np.abs(y - train_pred) < 1.0)
        
        cv_analysis = {
            'best_params': best_params,
            'cv_mae': best_cv_score,
            'train_mae': train_mae,
            'exact_matches': exact_matches,
            'close_matches': close_matches,
            'overfitting_ratio': best_cv_score / train_mae if train_mae > 0 else float('inf')
        }
        
        print(f"  Best CV MAE: ${best_cv_score:.2f}")
        print(f"  Best params: {best_params}")
        print(f"  Train MAE: ${train_mae:.2f}")
        print(f"  Exact matches: {exact_matches}")
        
        self.results['cv_complexity_analysis'] = cv_analysis
        self.models['cv_optimized'] = best_model
        
        return best_model

    def run_comprehensive_analysis(self):
        """Run all untested approaches"""
        print("🚀 Starting Comprehensive Ensemble Analysis")
        print("=" * 60)
        
        start_time = time.time()
        
        # Load data
        X, y = self.load_data()
        print(f"Loaded {len(X)} cases with {len(X[0])} features each")
        
        # Run all approaches
        approaches = [
            ('Mathematical Pattern Analysis', self.analyze_mathematical_patterns),
            ('Multiple Dozen Decision Trees', self.test_bagging_multiple_trees),
            ('Voting Ensemble', self.test_voting_ensemble), 
            ('Stacking Ensemble', self.test_stacking_ensemble),
            ('CV Complexity Analysis', self.cross_validation_complexity_analysis)
        ]
        
        for name, method in approaches:
            try:
                print(f"\n{'='*20} {name} {'='*20}")
                if name == 'Mathematical Pattern Analysis':
                    method(X, y)
                else:
                    model = method(X, y)
                    if model is not None:
                        # Update best model if this one is better
                        train_pred = model.predict(X)
                        train_mae = mean_absolute_error(y, train_pred)
                        if train_mae < self.best_score:
                            self.best_score = train_mae
                            self.best_model = model
                            
            except Exception as e:
                print(f"❌ Error in {name}: {str(e)}")
                self.results[f'{name}_error'] = str(e)
        
        # Generate comprehensive report
        self.generate_comprehensive_report()
        
        total_time = time.time() - start_time
        print(f"\n✅ Comprehensive analysis completed in {total_time:.1f} seconds")
        
        return self.results

    def generate_comprehensive_report(self):
        """Generate comprehensive results report"""
        print("\n📋 COMPREHENSIVE RESULTS SUMMARY")
        print("=" * 60)
        
        # Find best performing approaches
        performance_summary = []
        
        for approach, result in self.results.items():
            if isinstance(result, dict) and 'train_mae' in result:
                performance_summary.append({
                    'approach': approach,
                    'train_mae': result['train_mae'],
                    'cv_mae': result.get('cv_mae', 'N/A'),
                    'exact_matches': result['exact_matches'],
                    'close_matches': result['close_matches'],
                    'overfitting_ratio': result.get('overfitting_ratio', 'N/A')
                })
        
        # Sort by training MAE
        performance_summary.sort(key=lambda x: x['train_mae'])
        
        print("\n🏆 PERFORMANCE RANKING:")
        print("-" * 80)
        print(f"{'Rank':<4} {'Approach':<25} {'Train MAE':<10} {'CV MAE':<10} {'Exact':<6} {'Close':<6} {'Overfit':<8}")
        print("-" * 80)
        
        for i, result in enumerate(performance_summary[:10]):  # Top 10
            rank = f"{i+1}."
            approach = result['approach'][:24]
            train_mae = f"${result['train_mae']:.2f}"
            cv_mae = f"${result['cv_mae']:.2f}" if result['cv_mae'] != 'N/A' else 'N/A'
            exact = str(result['exact_matches'])
            close = str(result['close_matches'])
            overfit = f"{result['overfitting_ratio']:.2f}" if result['overfitting_ratio'] != 'N/A' else 'N/A'
            
            print(f"{rank:<4} {approach:<25} {train_mae:<10} {cv_mae:<10} {exact:<6} {close:<6} {overfit:<8}")
        
        # Save detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f'comprehensive_ensemble_results_{timestamp}.json'
        
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\n💾 Detailed results saved to: {results_file}")
        
        # Save best model
        if self.best_model is not None:
            model_file = f'best_comprehensive_model_{timestamp}.pkl'
            with open(model_file, 'wb') as f:
                pickle.dump(self.best_model, f)
            print(f"💾 Best model saved to: {model_file}")
            print(f"🎯 Best training MAE: ${self.best_score:.2f}")

if __name__ == "__main__":
    optimizer = ComprehensiveEnsembleOptimizer()
    results = optimizer.run_comprehensive_analysis() 