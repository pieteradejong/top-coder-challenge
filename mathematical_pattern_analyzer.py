#!/usr/bin/env python3
"""
Mathematical Pattern Analyzer
============================

Analyze the 1,000 public cases to discover exact mathematical patterns
and business rules that could explain the legacy system behavior.

Goal: Find the true mathematical formula instead of ML approximation
"""

import json
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

class MathematicalPatternAnalyzer:
    def __init__(self):
        self.patterns = {}
        self.df = None
        
    def load_and_prepare_data(self):
        """Load and prepare data for analysis"""
        print("📊 Loading and preparing data...")
        
        with open('public_cases.json', 'r') as f:
            cases = json.load(f)
        
        # Create comprehensive DataFrame
        data = []
        for case in cases:
            data.append({
                'duration': case['input']['trip_duration_days'],
                'miles': case['input']['miles_traveled'],
                'receipts': case['input']['total_receipts_amount'],
                'reimbursement': case['expected_output']
            })
        
        self.df = pd.DataFrame(data)
        
        # Add derived features
        self.df['miles_per_day'] = self.df['miles'] / self.df['duration']
        self.df['receipts_per_day'] = self.df['receipts'] / self.df['duration']
        self.df['reimbursement_per_day'] = self.df['reimbursement'] / self.df['duration']
        self.df['efficiency_ratio'] = self.df['miles'] / self.df['receipts']
        self.df['mileage_rate'] = self.df['reimbursement'] / self.df['miles']
        self.df['receipt_rate'] = self.df['reimbursement'] / self.df['receipts']
        
        print(f"Loaded {len(self.df)} cases")
        return self.df
    
    def analyze_duration_patterns(self):
        """Analyze patterns by trip duration"""
        print("\n🔍 Analyzing Duration Patterns...")
        
        duration_stats = self.df.groupby('duration').agg({
            'reimbursement_per_day': ['mean', 'std', 'min', 'max', 'count'],
            'reimbursement': ['mean', 'std', 'min', 'max']
        }).round(2)
        
        print("Per-day reimbursement by duration:")
        print(duration_stats['reimbursement_per_day'])
        
        # Test inverse relationship
        durations = self.df['duration'].unique()
        avg_per_day = self.df.groupby('duration')['reimbursement_per_day'].mean()
        
        def inverse_func(x, a, b):
            return a / x + b
        
        try:
            popt, pcov = curve_fit(inverse_func, durations, avg_per_day)
            predicted = inverse_func(durations, *popt)
            r_squared = 1 - np.sum((avg_per_day - predicted)**2) / np.sum((avg_per_day - avg_per_day.mean())**2)
            
            self.patterns['inverse_relationship'] = {
                'formula': f'per_day_rate = {popt[0]:.2f} / duration + {popt[1]:.2f}',
                'r_squared': r_squared,
                'parameters': {'a': popt[0], 'b': popt[1]},
                'fit_quality': 'excellent' if r_squared > 0.99 else 'good' if r_squared > 0.95 else 'poor'
            }
            
            print(f"Inverse relationship: R² = {r_squared:.4f}")
            print(f"Formula: per_day_rate = {popt[0]:.2f} / duration + {popt[1]:.2f}")
            
        except Exception as e:
            print(f"Could not fit inverse relationship: {e}")
    
    def analyze_mileage_tiers(self):
        """Analyze mileage rate tiers"""
        print("\n🛣️ Analyzing Mileage Tiers...")
        
        # Sort by miles and analyze rate changes
        df_sorted = self.df.sort_values('miles')
        
        # Look for breakpoints in mileage rates
        mileage_bins = [0, 100, 200, 300, 500, 750, 1000, 1500, 2000, float('inf')]
        self.df['mileage_bin'] = pd.cut(self.df['miles'], bins=mileage_bins)
        
        mileage_analysis = self.df.groupby('mileage_bin').agg({
            'mileage_rate': ['mean', 'std', 'count'],
            'miles': ['mean', 'min', 'max']
        }).round(3)
        
        print("Mileage rates by distance ranges:")
        print(mileage_analysis)
        
        # Detect tier structure
        mean_rates = self.df.groupby('mileage_bin')['mileage_rate'].mean()
        self.patterns['mileage_tiers'] = {
            'tier_rates': mean_rates.to_dict(),
            'breakpoints': mileage_bins[:-1],
            'analysis': mileage_analysis.to_dict()
        }
    
    def analyze_receipt_patterns(self):
        """Analyze receipt reimbursement patterns"""
        print("\n🧾 Analyzing Receipt Patterns...")
        
        # Receipt rate analysis
        receipt_bins = [0, 50, 100, 150, 200, 300, 500, 1000, float('inf')]
        self.df['receipt_bin'] = pd.cut(self.df['receipts'], bins=receipt_bins)
        
        receipt_analysis = self.df.groupby('receipt_bin').agg({
            'receipt_rate': ['mean', 'std', 'count'],
            'receipts': ['mean', 'min', 'max']
        }).round(3)
        
        print("Receipt rates by amount ranges:")
        print(receipt_analysis)
        
        self.patterns['receipt_tiers'] = {
            'tier_rates': self.df.groupby('receipt_bin')['receipt_rate'].mean().to_dict(),
            'breakpoints': receipt_bins[:-1],
            'analysis': receipt_analysis.to_dict()
        }
    
    def analyze_efficiency_sweet_spots(self):
        """Analyze efficiency sweet spots"""
        print("\n⚡ Analyzing Efficiency Sweet Spots...")
        
        # Miles per day analysis
        efficiency_bins = [0, 50, 100, 150, 180, 200, 220, 250, 300, 400, float('inf')]
        self.df['efficiency_bin'] = pd.cut(self.df['miles_per_day'], bins=efficiency_bins)
        
        efficiency_analysis = self.df.groupby('efficiency_bin').agg({
            'reimbursement_per_day': ['mean', 'std', 'count'],
            'miles_per_day': ['mean', 'min', 'max']
        }).round(2)
        
        print("Reimbursement per day by efficiency (miles/day):")
        print(efficiency_analysis)
        
        # Look for the 180-220 sweet spot
        sweet_spot_mask = (self.df['miles_per_day'] >= 180) & (self.df['miles_per_day'] <= 220)
        sweet_spot_avg = self.df[sweet_spot_mask]['reimbursement_per_day'].mean()
        overall_avg = self.df['reimbursement_per_day'].mean()
        
        self.patterns['efficiency_sweet_spot'] = {
            'range': '180-220 miles/day',
            'sweet_spot_avg': sweet_spot_avg,
            'overall_avg': overall_avg,
            'bonus': sweet_spot_avg - overall_avg,
            'analysis': efficiency_analysis.to_dict()
        }
        
        print(f"Sweet spot (180-220 mi/day) avg: ${sweet_spot_avg:.2f}")
        print(f"Overall average: ${overall_avg:.2f}")
        print(f"Sweet spot bonus: ${sweet_spot_avg - overall_avg:.2f}")
    
    def analyze_five_day_bonus(self):
        """Analyze 5-day trip bonus"""
        print("\n🎯 Analyzing 5-Day Bonus...")
        
        five_day_trips = self.df[self.df['duration'] == 5]
        other_trips = self.df[self.df['duration'] != 5]
        
        # Compare 5-day trips to similar duration trips
        similar_duration = self.df[self.df['duration'].isin([4, 6])]
        
        five_day_avg = five_day_trips['reimbursement_per_day'].mean()
        similar_avg = similar_duration['reimbursement_per_day'].mean()
        
        self.patterns['five_day_bonus'] = {
            'five_day_avg': five_day_avg,
            'similar_duration_avg': similar_avg,
            'bonus': five_day_avg - similar_avg,
            'five_day_count': len(five_day_trips),
            'evidence': 'strong' if five_day_avg > similar_avg + 10 else 'weak'
        }
        
        print(f"5-day trips average: ${five_day_avg:.2f}")
        print(f"4&6-day trips average: ${similar_avg:.2f}")
        print(f"5-day bonus: ${five_day_avg - similar_avg:.2f}")
    
    def analyze_vacation_penalties(self):
        """Analyze vacation penalties for long trips"""
        print("\n🏖️ Analyzing Vacation Penalties...")
        
        # Compare long trips (8+ days) to shorter ones
        long_trips = self.df[self.df['duration'] >= 8]
        short_trips = self.df[self.df['duration'] < 8]
        
        long_avg = long_trips['reimbursement_per_day'].mean()
        short_avg = short_trips['reimbursement_per_day'].mean()
        
        # Look at very long trips (12+ days)
        very_long_trips = self.df[self.df['duration'] >= 12]
        very_long_avg = very_long_trips['reimbursement_per_day'].mean() if len(very_long_trips) > 0 else 0
        
        self.patterns['vacation_penalties'] = {
            'long_trips_avg': long_avg,
            'short_trips_avg': short_avg,
            'penalty': short_avg - long_avg,
            'very_long_avg': very_long_avg,
            'long_trip_count': len(long_trips),
            'very_long_count': len(very_long_trips)
        }
        
        print(f"Long trips (8+ days) average: ${long_avg:.2f}")
        print(f"Short trips (<8 days) average: ${short_avg:.2f}")
        print(f"Vacation penalty: ${short_avg - long_avg:.2f}")
    
    def discover_exact_formulas(self):
        """Try to discover exact mathematical formulas"""
        print("\n🔬 Discovering Exact Formulas...")
        
        # Test various formula structures
        formulas_to_test = [
            {
                'name': 'Linear Combination',
                'func': lambda d, m, r, a, b, c, d_coef: a * d + b * m + c * r + d_coef,
                'params': 4
            },
            {
                'name': 'Inverse Duration Base',
                'func': lambda d, m, r, a, b, c, d_coef: (a / d + b) * d + c * m + d_coef * r,
                'params': 4
            },
            {
                'name': 'Tiered Structure',
                'func': lambda d, m, r, base, mile_rate, receipt_rate: base * d + mile_rate * m + receipt_rate * r,
                'params': 3
            }
        ]
        
        best_formula = None
        best_r_squared = 0
        
        for formula in formulas_to_test:
            try:
                # Prepare data
                X = np.column_stack([self.df['duration'], self.df['miles'], self.df['receipts']])
                y = self.df['reimbursement']
                
                # Simple linear regression for tiered structure
                if formula['name'] == 'Tiered Structure':
                    from sklearn.linear_model import LinearRegression
                    model = LinearRegression()
                    model.fit(X, y)
                    predicted = model.predict(X)
                    r_squared = 1 - np.sum((y - predicted)**2) / np.sum((y - y.mean())**2)
                    
                    if r_squared > best_r_squared:
                        best_r_squared = r_squared
                        best_formula = {
                            'name': formula['name'],
                            'r_squared': r_squared,
                            'coefficients': {
                                'duration_coef': model.coef_[0],
                                'miles_coef': model.coef_[1],
                                'receipts_coef': model.coef_[2],
                                'intercept': model.intercept_
                            },
                            'formula': f'reimbursement = {model.coef_[0]:.3f} * duration + {model.coef_[1]:.3f} * miles + {model.coef_[2]:.3f} * receipts + {model.intercept_:.3f}'
                        }
                    
                    print(f"{formula['name']}: R² = {r_squared:.4f}")
                    
            except Exception as e:
                print(f"Error testing {formula['name']}: {e}")
        
        self.patterns['best_formula'] = best_formula
        
        if best_formula:
            print(f"\nBest formula: {best_formula['name']} (R² = {best_formula['r_squared']:.4f})")
            print(f"Formula: {best_formula['formula']}")
    
    def generate_business_rules(self):
        """Generate business rules based on patterns"""
        print("\n📋 Generating Business Rules...")
        
        rules = []
        
        # Duration-based rules
        if 'inverse_relationship' in self.patterns:
            inv = self.patterns['inverse_relationship']
            if inv['fit_quality'] in ['excellent', 'good']:
                rules.append(f"Base per-day rate follows inverse relationship: {inv['formula']}")
        
        # Efficiency rules
        if 'efficiency_sweet_spot' in self.patterns:
            eff = self.patterns['efficiency_sweet_spot']
            if eff['bonus'] > 5:
                rules.append(f"Efficiency bonus: {eff['range']} gets ${eff['bonus']:.2f} extra per day")
        
        # 5-day bonus
        if 'five_day_bonus' in self.patterns:
            bonus = self.patterns['five_day_bonus']
            if bonus['evidence'] == 'strong':
                rules.append(f"5-day trip bonus: ${bonus['bonus']:.2f} extra per day")
        
        # Vacation penalty
        if 'vacation_penalties' in self.patterns:
            penalty = self.patterns['vacation_penalties']
            if penalty['penalty'] > 5:
                rules.append(f"Long trip penalty: 8+ days get ${penalty['penalty']:.2f} less per day")
        
        self.patterns['business_rules'] = rules
        
        print("Discovered Business Rules:")
        for i, rule in enumerate(rules, 1):
            print(f"{i}. {rule}")
    
    def run_complete_analysis(self):
        """Run complete mathematical pattern analysis"""
        print("🔬 Starting Mathematical Pattern Analysis")
        print("=" * 60)
        
        start_time = datetime.now()
        
        # Load data
        self.load_and_prepare_data()
        
        # Run all analyses
        self.analyze_duration_patterns()
        self.analyze_mileage_tiers()
        self.analyze_receipt_patterns()
        self.analyze_efficiency_sweet_spots()
        self.analyze_five_day_bonus()
        self.analyze_vacation_penalties()
        self.discover_exact_formulas()
        self.generate_business_rules()
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f'mathematical_patterns_{timestamp}.json'
        
        with open(results_file, 'w') as f:
            json.dump(self.patterns, f, indent=2, default=str)
        
        print(f"\n💾 Analysis saved to: {results_file}")
        
        duration = datetime.now() - start_time
        print(f"⏱️ Analysis completed in {duration.total_seconds():.1f} seconds")
        
        return self.patterns

if __name__ == "__main__":
    analyzer = MathematicalPatternAnalyzer()
    patterns = analyzer.run_complete_analysis() 