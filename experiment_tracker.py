#!/usr/bin/env python3
"""
Advanced Experiment Tracking Framework
Comprehensive tracking, visualization, and analysis of algorithm experiments
"""

import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os
import subprocess
from typing import Dict, List, Any, Optional

class ExperimentTracker:
    """Advanced experiment tracking with visualizations"""
    
    def __init__(self, experiment_file='experiments.json'):
        self.experiment_file = experiment_file
        self.experiments = self.load_experiments()
        
    def load_experiments(self) -> List[Dict]:
        """Load existing experiments"""
        if os.path.exists(self.experiment_file):
            with open(self.experiment_file, 'r') as f:
                return json.load(f)
        return []
    
    def save_experiments(self):
        """Save experiments to file"""
        with open(self.experiment_file, 'w') as f:
            json.dump(self.experiments, f, indent=2)
    
    def add_experiment(self, 
                      name: str,
                      algorithm_type: str,
                      description: str,
                      parameters: Dict,
                      results: Dict,
                      notes: str = "",
                      tags: List[str] = None) -> int:
        """Add a new experiment"""
        
        experiment = {
            'id': len(self.experiments) + 1,
            'name': name,
            'algorithm_type': algorithm_type,
            'description': description,
            'parameters': parameters,
            'results': results,
            'notes': notes,
            'tags': tags or [],
            'timestamp': datetime.now().isoformat(),
            'status': 'completed'
        }
        
        self.experiments.append(experiment)
        self.save_experiments()
        
        print(f"✅ Experiment {experiment['id']} '{name}' added successfully")
        return experiment['id']
    
    def run_and_track_experiment(self, 
                                name: str,
                                algorithm_file: str,
                                algorithm_type: str,
                                description: str,
                                parameters: Dict,
                                notes: str = "",
                                tags: List[str] = None) -> Dict:
        """Run an experiment and automatically track results"""
        
        print(f"\n🧪 Running Experiment: {name}")
        print(f"📝 Description: {description}")
        print(f"🔧 Algorithm: {algorithm_file}")
        
        # Backup current algorithm
        if os.path.exists('calculate_reimbursement.py'):
            subprocess.run(['cp', 'calculate_reimbursement.py', 'calculate_reimbursement_backup.py'])
        
        # Copy experiment algorithm
        subprocess.run(['cp', algorithm_file, 'calculate_reimbursement.py'])
        
        try:
            # Run evaluation
            result = subprocess.run(['python', 'fast_eval.py'], 
                                  capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                # Parse results
                output = result.stdout.strip()
                results = self.parse_evaluation_output(output)
                
                # Add experiment
                exp_id = self.add_experiment(
                    name=name,
                    algorithm_type=algorithm_type,
                    description=description,
                    parameters=parameters,
                    results=results,
                    notes=notes,
                    tags=tags
                )
                
                print(f"✅ Experiment completed successfully!")
                print(f"📊 Score: {results.get('score', 'N/A')}")
                print(f"💰 Average Error: ${results.get('average_error', 'N/A')}")
                print(f"🎯 Close Matches: {results.get('close_matches', 'N/A')}")
                
                return results
                
            else:
                print(f"❌ Experiment failed: {result.stderr}")
                return {'error': result.stderr}
                
        except subprocess.TimeoutExpired:
            print("⏰ Experiment timed out")
            return {'error': 'timeout'}
        except Exception as e:
            print(f"💥 Experiment error: {e}")
            return {'error': str(e)}
        finally:
            # Restore backup
            if os.path.exists('calculate_reimbursement_backup.py'):
                subprocess.run(['cp', 'calculate_reimbursement_backup.py', 'calculate_reimbursement.py'])
    
    def parse_evaluation_output(self, output: str) -> Dict:
        """Parse evaluation output into structured results"""
        results = {}
        
        lines = output.split('\n')
        for line in lines:
            if 'Average error:' in line:
                try:
                    results['average_error'] = float(line.split('$')[1])
                except:
                    pass
            elif 'Close matches' in line:
                try:
                    results['close_matches'] = int(line.split('(')[0].split(':')[1].strip())
                except:
                    pass
            elif 'Exact matches' in line:
                try:
                    results['exact_matches'] = int(line.split('(')[0].split(':')[1].strip())
                except:
                    pass
            elif 'Your Score:' in line:
                try:
                    results['score'] = float(line.split(':')[1].split('(')[0].strip())
                except:
                    pass
            elif 'Maximum error:' in line:
                try:
                    results['max_error'] = float(line.split('$')[1])
                except:
                    pass
        
        return results
    
    def get_experiments_df(self) -> pd.DataFrame:
        """Convert experiments to pandas DataFrame for analysis"""
        if not self.experiments:
            return pd.DataFrame()
        
        data = []
        for exp in self.experiments:
            row = {
                'id': exp['id'],
                'name': exp['name'],
                'algorithm_type': exp['algorithm_type'],
                'description': exp['description'],
                'timestamp': exp['timestamp'],
                'tags': ', '.join(exp.get('tags', [])),
                'notes': exp.get('notes', ''),
            }
            
            # Add results
            results = exp.get('results', {})
            row.update({
                'score': results.get('score'),
                'average_error': results.get('average_error'),
                'close_matches': results.get('close_matches', 0),
                'exact_matches': results.get('exact_matches', 0),
                'max_error': results.get('max_error'),
            })
            
            # Add key parameters
            params = exp.get('parameters', {})
            for key, value in params.items():
                row[f'param_{key}'] = value
            
            data.append(row)
        
        return pd.DataFrame(data)
    
    def create_performance_plots(self, save_dir='plots'):
        """Create comprehensive performance visualizations using matplotlib"""
        
        df = self.get_experiments_df()
        if df.empty:
            print("No experiments to visualize")
            return
        
        # Create plots directory
        os.makedirs(save_dir, exist_ok=True)
        
        # Set style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # 1. Performance over time
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('🧪 Experiment Performance Dashboard', fontsize=16, fontweight='bold')
        
        # Score over time
        axes[0,0].plot(df['id'], df['score'], marker='o', linewidth=2, markersize=6)
        axes[0,0].set_title('Score Over Time (Lower is Better)')
        axes[0,0].set_xlabel('Experiment ID')
        axes[0,0].set_ylabel('Score')
        axes[0,0].grid(True, alpha=0.3)
        
        # Average error over time
        axes[0,1].plot(df['id'], df['average_error'], marker='s', linewidth=2, markersize=6, color='red')
        axes[0,1].set_title('Average Error Over Time')
        axes[0,1].set_xlabel('Experiment ID')
        axes[0,1].set_ylabel('Average Error ($)')
        axes[0,1].grid(True, alpha=0.3)
        
        # Close matches over time
        axes[1,0].plot(df['id'], df['close_matches'], marker='^', linewidth=2, markersize=6, color='green')
        axes[1,0].set_title('Close Matches Over Time')
        axes[1,0].set_xlabel('Experiment ID')
        axes[1,0].set_ylabel('Close Matches')
        axes[1,0].grid(True, alpha=0.3)
        
        # Score distribution
        axes[1,1].hist(df['score'], bins=10, alpha=0.7, color='purple', edgecolor='black')
        axes[1,1].set_title('Score Distribution')
        axes[1,1].set_xlabel('Score')
        axes[1,1].set_ylabel('Frequency')
        axes[1,1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'{save_dir}/performance_dashboard.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. Algorithm comparison
        if 'algorithm_type' in df.columns and df['algorithm_type'].nunique() > 1:
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle('🔬 Algorithm Performance Comparison', fontsize=16, fontweight='bold')
            
            # Average score by algorithm
            algo_scores = df.groupby('algorithm_type')['score'].mean().sort_values()
            axes[0,0].barh(algo_scores.index, algo_scores.values, color='skyblue')
            axes[0,0].set_title('Average Score by Algorithm Type')
            axes[0,0].set_xlabel('Average Score')
            
            # Average error by algorithm
            algo_errors = df.groupby('algorithm_type')['average_error'].mean().sort_values()
            axes[0,1].barh(algo_errors.index, algo_errors.values, color='lightcoral')
            axes[0,1].set_title('Average Error by Algorithm Type')
            axes[0,1].set_xlabel('Average Error ($)')
            
            # Close matches by algorithm
            algo_matches = df.groupby('algorithm_type')['close_matches'].mean().sort_values(ascending=False)
            axes[1,0].barh(algo_matches.index, algo_matches.values, color='lightgreen')
            axes[1,0].set_title('Average Close Matches by Algorithm Type')
            axes[1,0].set_xlabel('Average Close Matches')
            
            # Score vs Error scatter
            for algo in df['algorithm_type'].unique():
                algo_data = df[df['algorithm_type'] == algo]
                axes[1,1].scatter(algo_data['average_error'], algo_data['score'], 
                                label=algo, s=60, alpha=0.7)
            axes[1,1].set_title('Score vs Average Error by Algorithm')
            axes[1,1].set_xlabel('Average Error ($)')
            axes[1,1].set_ylabel('Score')
            axes[1,1].legend()
            axes[1,1].grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig(f'{save_dir}/algorithm_comparison.png', dpi=300, bbox_inches='tight')
            plt.close()
        
        # 3. Detailed performance metrics
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('📊 Detailed Performance Metrics', fontsize=16, fontweight='bold')
        
        # Error distribution
        axes[0,0].hist(df['average_error'], bins=15, alpha=0.7, color='orange', edgecolor='black')
        axes[0,0].set_title('Average Error Distribution')
        axes[0,0].set_xlabel('Average Error ($)')
        axes[0,0].set_ylabel('Frequency')
        axes[0,0].grid(True, alpha=0.3)
        
        # Close matches distribution
        axes[0,1].hist(df['close_matches'], bins=10, alpha=0.7, color='green', edgecolor='black')
        axes[0,1].set_title('Close Matches Distribution')
        axes[0,1].set_xlabel('Close Matches')
        axes[0,1].set_ylabel('Frequency')
        axes[0,1].grid(True, alpha=0.3)
        
        # Performance improvement over time
        if len(df) > 1:
            score_improvement = df['score'].iloc[0] - df['score']
            axes[1,0].plot(df['id'], score_improvement, marker='o', linewidth=2, color='purple')
            axes[1,0].set_title('Cumulative Score Improvement')
            axes[1,0].set_xlabel('Experiment ID')
            axes[1,0].set_ylabel('Score Improvement from Baseline')
            axes[1,0].grid(True, alpha=0.3)
        
        # Top experiments
        top_5 = df.nsmallest(5, 'score')
        axes[1,1].barh(range(len(top_5)), top_5['score'], color='gold')
        axes[1,1].set_yticks(range(len(top_5)))
        axes[1,1].set_yticklabels([f"{row['name'][:20]}..." if len(row['name']) > 20 else row['name'] 
                                  for _, row in top_5.iterrows()])
        axes[1,1].set_title('Top 5 Experiments (by Score)')
        axes[1,1].set_xlabel('Score')
        
        plt.tight_layout()
        plt.savefig(f'{save_dir}/detailed_metrics.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"📊 Visualizations saved to {save_dir}/:")
        print(f"  - performance_dashboard.png")
        print(f"  - algorithm_comparison.png") 
        print(f"  - detailed_metrics.png")
    
    def get_best_experiments(self, n=5, metric='score') -> pd.DataFrame:
        """Get top N experiments by metric"""
        df = self.get_experiments_df()
        if df.empty:
            return df
        
        ascending = True if metric == 'score' or metric == 'average_error' else False
        return df.nsmallest(n, metric) if ascending else df.nlargest(n, metric)
    
    def get_experiment_summary(self) -> Dict:
        """Get comprehensive experiment summary"""
        df = self.get_experiments_df()
        if df.empty:
            return {}
        
        summary = {
            'total_experiments': len(df),
            'algorithm_types': df['algorithm_type'].nunique(),
            'best_score': df['score'].min(),
            'best_avg_error': df['average_error'].min(),
            'max_close_matches': df['close_matches'].max(),
            'total_exact_matches': df['exact_matches'].sum(),
            'latest_experiment': df.iloc[-1]['name'],
            'performance_trend': 'improving' if df['score'].iloc[-1] < df['score'].iloc[0] else 'declining'
        }
        
        return summary
    
    def print_summary(self):
        """Print experiment summary"""
        summary = self.get_experiment_summary()
        
        print("\n" + "="*60)
        print("🧪 EXPERIMENT TRACKING SUMMARY")
        print("="*60)
        
        if not summary:
            print("No experiments tracked yet.")
            return
        
        print(f"📊 Total Experiments: {summary['total_experiments']}")
        print(f"🔬 Algorithm Types: {summary['algorithm_types']}")
        print(f"🏆 Best Score: {summary['best_score']:.2f}")
        print(f"💰 Best Avg Error: ${summary['best_avg_error']:.2f}")
        print(f"🎯 Max Close Matches: {summary['max_close_matches']}")
        print(f"✅ Total Exact Matches: {summary['total_exact_matches']}")
        print(f"🕐 Latest: {summary['latest_experiment']}")
        print(f"📈 Trend: {summary['performance_trend']}")
        
        # Show top 3 experiments
        print(f"\n🏅 TOP 3 EXPERIMENTS (by score):")
        top_3 = self.get_best_experiments(3, 'score')
        for i, (_, exp) in enumerate(top_3.iterrows(), 1):
            print(f"  {i}. {exp['name']} - Score: {exp['score']:.2f}, Error: ${exp['average_error']:.2f}")

def main():
    """Main function for testing"""
    tracker = ExperimentTracker()
    
    # Add some sample experiments if none exist
    if not tracker.experiments:
        print("Adding sample experiments...")
        
        # Add our recent ML breakthrough results
        tracker.add_experiment(
            name="Gradient Boosting Breakthrough",
            algorithm_type="Machine Learning",
            description="Gradient Boosting with engineered features",
            parameters={
                "n_estimators": 100,
                "max_depth": 6,
                "learning_rate": 0.1,
                "features": 15
            },
            results={
                "score": 1877.15,
                "average_error": 17.77,
                "close_matches": 45,
                "exact_matches": 0,
                "max_error": 113.12
            },
            notes="Major breakthrough - 89% improvement over rule-based",
            tags=["breakthrough", "ml", "gradient_boosting"]
        )
        
        tracker.add_experiment(
            name="Random Forest",
            algorithm_type="Machine Learning", 
            description="Random Forest with engineered features",
            parameters={
                "n_estimators": 200,
                "max_depth": 12,
                "features": 15
            },
            results={
                "score": 3108.01,
                "average_error": 30.08,
                "close_matches": 25,
                "exact_matches": 0,
                "max_error": 445.90
            },
            notes="Excellent performance, second best ML algorithm",
            tags=["ml", "random_forest"]
        )
        
        tracker.add_experiment(
            name="Best Rule-Based Algorithm",
            algorithm_type="Rule-Based",
            description="Optimized rule-based with moderate penalties",
            parameters={
                "base_rates": "inverse_relationship",
                "mileage_tiers": 3,
                "receipt_tiers": 3,
                "penalties": "moderate"
            },
            results={
                "score": 16922,
                "average_error": 168.22,
                "close_matches": 9,
                "exact_matches": 0
            },
            notes="Best rule-based approach before ML breakthrough",
            tags=["rule_based", "baseline"]
        )
    
    # Print summary
    tracker.print_summary()
    
    # Create visualizations
    tracker.create_performance_plots()

if __name__ == "__main__":
    main() 