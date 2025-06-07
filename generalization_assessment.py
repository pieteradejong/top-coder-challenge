#!/usr/bin/env python3
"""
Generalization Assessment Tool - Measure overfitting vs generalization trade-off
"""

import json
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import cross_val_score, KFold, learning_curve, validation_curve
from sklearn.metrics import mean_absolute_error
import matplotlib.pyplot as plt
import joblib
import warnings
warnings.filterwarnings('ignore')

class GeneralizationAssessment:
    def __init__(self):
        print("📊 GENERALIZATION ASSESSMENT TOOL")
        print("=" * 50)
        print("Measuring overfitting vs generalization trade-off")
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
    
    def create_features(self, df, complexity_level='balanced'):
        """Create features with different complexity levels"""
        X = []
        
        for _, row in df.iterrows():
            duration = row['trip_duration_days']
            miles = row['miles_traveled']
            receipts = row['total_receipts_amount']
            
            if complexity_level == 'simple':
                # 8 simple features
                features = [
                    duration, miles, receipts,
                    miles / duration if duration > 0 else 0,
                    receipts / duration if duration > 0 else 0,
                    np.log1p(receipts),
                    duration * miles,
                    1 if duration >= 8 else 0
                ]
            elif complexity_level == 'balanced':
                # 12 balanced features
                features = [
                    duration, miles, receipts,
                    miles / duration if duration > 0 else 0,
                    receipts / duration if duration > 0 else 0,
                    miles / (receipts + 1),
                    np.log1p(receipts),
                    np.log1p(miles),
                    np.sqrt(receipts),
                    duration * miles,
                    1 if duration >= 8 else 0,
                    1 if duration == 5 else 0
                ]
            elif complexity_level == 'complex':
                # 15 complex features (original perfect model)
                features = [
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
            
            X.append(features)
        
        return np.array(X)
    
    def assess_overfitting_risk(self):
        """Comprehensive overfitting risk assessment"""
        print("\n🔍 OVERFITTING RISK ASSESSMENT")
        print("=" * 40)
        
        y = self.df['expected_output'].values
        
        # Test different complexity levels
        complexity_configs = [
            {
                'name': 'Simple',
                'features': 'simple',
                'model_params': {'n_estimators': 100, 'max_depth': 4, 'learning_rate': 0.1}
            },
            {
                'name': 'Balanced',
                'features': 'balanced', 
                'model_params': {'n_estimators': 400, 'max_depth': 7, 'learning_rate': 0.04}
            },
            {
                'name': 'Complex',
                'features': 'complex',
                'model_params': {'n_estimators': 750, 'max_depth': 15, 'learning_rate': 0.02}
            }
        ]
        
        results = []
        
        for config in complexity_configs:
            print(f"\n📊 Testing {config['name']} Configuration...")
            
            # Create features
            X = self.create_features(self.df, config['features'])
            
            # Create model with regularization
            model = GradientBoostingRegressor(
                random_state=42,
                min_samples_split=5,
                min_samples_leaf=3,
                subsample=0.9,
                **config['model_params']
            )
            
            # Cross-validation assessment
            kfold = KFold(n_splits=10, shuffle=True, random_state=42)
            cv_scores = cross_val_score(model, X, y, cv=kfold, scoring='neg_mean_absolute_error')
            cv_mae = -cv_scores.mean()
            cv_std = cv_scores.std()
            
            # Training performance
            model.fit(X, y)
            train_pred = model.predict(X)
            train_mae = mean_absolute_error(y, train_pred)
            train_exact = np.sum(np.abs(train_pred - y) < 0.01)
            
            # Overfitting metrics
            generalization_gap = cv_mae - train_mae
            overfitting_ratio = generalization_gap / train_mae if train_mae > 0 else float('inf')
            
            result = {
                'name': config['name'],
                'features': X.shape[1],
                'cv_mae': cv_mae,
                'cv_std': cv_std,
                'train_mae': train_mae,
                'train_exact': train_exact,
                'generalization_gap': generalization_gap,
                'overfitting_ratio': overfitting_ratio,
                'model': model
            }
            results.append(result)
            
            print(f"   Features: {X.shape[1]}")
            print(f"   CV MAE: ${cv_mae:.2f} ± ${cv_std:.2f}")
            print(f"   Train MAE: ${train_mae:.2f}")
            print(f"   Exact Matches: {train_exact}/1000")
            print(f"   Gen Gap: ${generalization_gap:.2f}")
            print(f"   Overfitting Ratio: {overfitting_ratio:.2f}")
            
            # Risk assessment
            if overfitting_ratio < 1.0:
                risk = "LOW"
            elif overfitting_ratio < 3.0:
                risk = "MODERATE" 
            else:
                risk = "HIGH"
            print(f"   Overfitting Risk: {risk}")
        
        return results
    
    def learning_curve_analysis(self, model_config):
        """Analyze learning curves to detect overfitting"""
        print(f"\n📈 LEARNING CURVE ANALYSIS - {model_config['name']}")
        print("=" * 45)
        
        X = self.create_features(self.df, model_config['features'])
        y = self.df['expected_output'].values
        
        model = GradientBoostingRegressor(
            random_state=42,
            min_samples_split=5,
            min_samples_leaf=3,
            subsample=0.9,
            **model_config['model_params']
        )
        
        # Generate learning curve
        train_sizes = np.linspace(0.1, 1.0, 10)
        train_sizes_abs, train_scores, val_scores = learning_curve(
            model, X, y, 
            train_sizes=train_sizes,
            cv=5,
            scoring='neg_mean_absolute_error',
            random_state=42
        )
        
        train_mae = -train_scores.mean(axis=1)
        val_mae = -val_scores.mean(axis=1)
        
        print(f"Training sizes tested: {len(train_sizes_abs)}")
        print(f"Final training MAE: ${train_mae[-1]:.2f}")
        print(f"Final validation MAE: ${val_mae[-1]:.2f}")
        print(f"Final gap: ${val_mae[-1] - train_mae[-1]:.2f}")
        
        # Detect overfitting pattern
        gap_trend = np.diff(val_mae - train_mae)
        if np.mean(gap_trend[-3:]) > 0:
            print("⚠️  Overfitting detected: validation gap increasing")
        else:
            print("✅ Good generalization: stable validation gap")
        
        return train_sizes_abs, train_mae, val_mae
    
    def optimal_complexity_search(self):
        """Search for optimal model complexity"""
        print("\n🎯 OPTIMAL COMPLEXITY SEARCH")
        print("=" * 35)
        
        X = self.create_features(self.df, 'balanced')
        y = self.df['expected_output'].values
        
        # Test different complexity parameters
        param_ranges = {
            'n_estimators': [100, 200, 400, 600, 800],
            'max_depth': [4, 6, 8, 10, 12],
            'learning_rate': [0.02, 0.04, 0.06, 0.08, 0.1]
        }
        
        best_score = float('inf')
        best_config = None
        
        for param_name, param_range in param_ranges.items():
            print(f"\n🔧 Testing {param_name}...")
            
            base_params = {
                'n_estimators': 400,
                'max_depth': 7,
                'learning_rate': 0.04,
                'random_state': 42,
                'min_samples_split': 5,
                'min_samples_leaf': 3,
                'subsample': 0.9
            }
            
            scores = []
            for param_value in param_range:
                base_params[param_name] = param_value
                
                model = GradientBoostingRegressor(**base_params)
                cv_scores = cross_val_score(model, X, y, cv=5, scoring='neg_mean_absolute_error')
                cv_mae = -cv_scores.mean()
                scores.append(cv_mae)
                
                if cv_mae < best_score:
                    best_score = cv_mae
                    best_config = base_params.copy()
                
                print(f"   {param_name}={param_value}: CV MAE=${cv_mae:.2f}")
        
        print(f"\n🏆 Best Configuration Found:")
        print(f"   CV MAE: ${best_score:.2f}")
        for param, value in best_config.items():
            print(f"   {param}: {value}")
        
        return best_config, best_score
    
    def final_recommendation(self, assessment_results):
        """Generate final recommendation based on all assessments"""
        print("\n🎯 FINAL GENERALIZATION RECOMMENDATION")
        print("=" * 45)
        
        # Analyze results
        for result in assessment_results:
            print(f"\n{result['name']} Model:")
            print(f"   Overfitting Ratio: {result['overfitting_ratio']:.2f}")
            print(f"   CV Stability: ±${result['cv_std']:.2f}")
            print(f"   Training Performance: {result['train_exact']} exact matches")
            
            # Risk scoring
            risk_score = 0
            if result['overfitting_ratio'] > 3.0:
                risk_score += 3
            elif result['overfitting_ratio'] > 1.0:
                risk_score += 1
            
            if result['cv_std'] > 15:
                risk_score += 2
            elif result['cv_std'] > 10:
                risk_score += 1
            
            if result['train_exact'] > 500:
                risk_score += 2
            elif result['train_exact'] > 100:
                risk_score += 1
            
            result['risk_score'] = risk_score
        
        # Select best model
        best_model = min(assessment_results, key=lambda x: x['risk_score'] + x['cv_mae']/100)
        
        print(f"\n🏆 RECOMMENDED MODEL: {best_model['name']}")
        print(f"   Risk Score: {best_model['risk_score']}/7 (lower is better)")
        print(f"   Expected Private MAE: ${best_model['cv_mae']:.2f}")
        print(f"   Confidence Level: {max(30, 100 - best_model['risk_score'] * 10)}%")
        
        return best_model
    
    def run_complete_assessment(self):
        """Run complete generalization assessment"""
        print("\n🚀 COMPLETE GENERALIZATION ASSESSMENT")
        print("=" * 50)
        
        # Step 1: Overfitting risk assessment
        assessment_results = self.assess_overfitting_risk()
        
        # Step 2: Learning curve analysis for each model
        for result in assessment_results:
            config = {
                'name': result['name'],
                'features': 'simple' if result['features'] == 8 else 'balanced' if result['features'] == 12 else 'complex',
                'model_params': {'n_estimators': 100 if result['features'] == 8 else 400 if result['features'] == 12 else 750,
                               'max_depth': 4 if result['features'] == 8 else 7 if result['features'] == 12 else 15,
                               'learning_rate': 0.1 if result['features'] == 8 else 0.04 if result['features'] == 12 else 0.02}
            }
            self.learning_curve_analysis(config)
        
        # Step 3: Optimal complexity search
        optimal_config, optimal_score = self.optimal_complexity_search()
        
        # Step 4: Final recommendation
        recommendation = self.final_recommendation(assessment_results)
        
        return {
            'assessment_results': assessment_results,
            'optimal_config': optimal_config,
            'recommendation': recommendation
        }

if __name__ == "__main__":
    assessor = GeneralizationAssessment()
    results = assessor.run_complete_assessment() 