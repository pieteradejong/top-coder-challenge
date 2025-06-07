#!/usr/bin/env python3

import json
import datetime
import shutil
import os
from typing import Dict, List

class AlgorithmManager:
    """Manage multiple algorithm variants with easy switching and comparison"""
    
    def __init__(self):
        self.algorithms_dir = "algorithms"
        self.results_file = "variant_results.json"
        self.current_algorithm_file = "calculate_reimbursement.py"
        
        # Create algorithms directory if it doesn't exist
        os.makedirs(self.algorithms_dir, exist_ok=True)
    
    def save_current_algorithm(self, variant_name: str, description: str, performance: Dict = None):
        """Save the current algorithm as a named variant"""
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{variant_name}_{timestamp}.py"
        filepath = os.path.join(self.algorithms_dir, filename)
        
        # Copy current algorithm
        shutil.copy2(self.current_algorithm_file, filepath)
        
        # Save metadata
        metadata = {
            'variant_name': variant_name,
            'description': description,
            'timestamp': datetime.datetime.now().isoformat(),
            'filename': filename,
            'filepath': filepath,
            'performance': performance or {}
        }
        
        metadata_file = os.path.join(self.algorithms_dir, f"{variant_name}_{timestamp}_metadata.json")
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"✅ Saved algorithm '{variant_name}' to {filepath}")
        return filepath
    
    def load_algorithm(self, variant_name: str):
        """Load a saved algorithm variant as the current algorithm"""
        
        # Find the most recent version of this variant
        algorithm_files = []
        for filename in os.listdir(self.algorithms_dir):
            if filename.startswith(variant_name) and filename.endswith('.py'):
                algorithm_files.append(filename)
        
        if not algorithm_files:
            print(f"❌ No algorithm found for variant '{variant_name}'")
            return False
        
        # Get the most recent
        algorithm_files.sort(reverse=True)
        latest_file = algorithm_files[0]
        source_path = os.path.join(self.algorithms_dir, latest_file)
        
        # Backup current algorithm
        backup_path = f"{self.current_algorithm_file}.backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(self.current_algorithm_file, backup_path)
        
        # Load the variant
        shutil.copy2(source_path, self.current_algorithm_file)
        
        print(f"✅ Loaded algorithm '{variant_name}' from {latest_file}")
        print(f"📁 Backup saved to {backup_path}")
        return True
    
    def list_algorithms(self):
        """List all saved algorithm variants"""
        
        print("📚 SAVED ALGORITHM VARIANTS")
        print("=" * 60)
        
        # Get all metadata files
        metadata_files = []
        for filename in os.listdir(self.algorithms_dir):
            if filename.endswith('_metadata.json'):
                metadata_files.append(filename)
        
        if not metadata_files:
            print("No saved algorithms found.")
            return
        
        # Load and display metadata
        algorithms = []
        for metadata_file in metadata_files:
            try:
                with open(os.path.join(self.algorithms_dir, metadata_file), 'r') as f:
                    metadata = json.load(f)
                    algorithms.append(metadata)
            except Exception as e:
                print(f"Error reading {metadata_file}: {e}")
        
        # Sort by timestamp (newest first)
        algorithms.sort(key=lambda x: x['timestamp'], reverse=True)
        
        print(f"{'Variant':<20} {'Date':<12} {'Score':<10} {'Avg Error':<10} {'Description'}")
        print("-" * 80)
        
        for algo in algorithms:
            variant = algo['variant_name'][:19]
            date = algo['timestamp'][:10]
            perf = algo.get('performance', {})
            score = f"{perf.get('score', 'N/A')}"
            avg_error = f"${perf.get('avg_error', 'N/A')}"
            desc = algo['description'][:30] + "..." if len(algo['description']) > 30 else algo['description']
            
            print(f"{variant:<20} {date:<12} {score:<10} {avg_error:<10} {desc}")
    
    def compare_algorithms(self, variant_names: List[str] = None):
        """Compare performance of multiple algorithm variants"""
        
        # Load variant results
        try:
            with open(self.results_file, 'r') as f:
                results = json.load(f)
        except FileNotFoundError:
            print(f"❌ Results file {self.results_file} not found. Run algorithm_variants.py first.")
            return
        
        if variant_names:
            # Filter to specific variants
            results = [r for r in results if r['variant_id'] in variant_names]
        
        if not results:
            print("No results to compare.")
            return
        
        print("🔍 ALGORITHM COMPARISON")
        print("=" * 80)
        
        # Sort by score
        results.sort(key=lambda x: x.get('performance', {}).get('score', float('inf')))
        
        print(f"{'Variant':<20} {'Score':<10} {'Avg Error':<10} {'Exact':<6} {'Close':<6} {'Max Error':<10}")
        print("-" * 80)
        
        for result in results:
            if 'error' in result['performance']:
                continue
                
            perf = result['performance']
            variant = result['variant_id'][:19]
            score = f"{perf['score']:,.0f}"
            avg_error = f"${perf['avg_error']}"
            exact = perf['exact_matches']
            close = perf['close_matches']
            max_error = f"${perf['max_error']}"
            
            print(f"{variant:<20} {score:<10} {avg_error:<10} {exact:<6} {close:<6} {max_error:<10}")
    
    def create_hybrid_algorithm(self, base_variant: str, modifications: Dict):
        """Create a hybrid algorithm by modifying a base variant"""
        
        print(f"🔬 Creating hybrid algorithm based on {base_variant}")
        
        # This would require more sophisticated code generation
        # For now, just document the approach
        hybrid_config = {
            'base_variant': base_variant,
            'modifications': modifications,
            'timestamp': datetime.datetime.now().isoformat(),
            'type': 'hybrid'
        }
        
        hybrid_file = f"hybrid_{base_variant}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(os.path.join(self.algorithms_dir, hybrid_file), 'w') as f:
            json.dump(hybrid_config, f, indent=2)
        
        print(f"✅ Hybrid configuration saved to {hybrid_file}")
        print("💡 Manual implementation required based on configuration")
    
    def get_best_performers(self, metric: str = 'score'):
        """Get the best performing algorithms by a specific metric"""
        
        try:
            with open(self.results_file, 'r') as f:
                results = json.load(f)
        except FileNotFoundError:
            print(f"❌ Results file {self.results_file} not found.")
            return []
        
        # Filter successful results
        successful = [r for r in results if 'error' not in r['performance']]
        
        if metric == 'score':
            successful.sort(key=lambda x: x['performance']['score'])
        elif metric == 'avg_error':
            successful.sort(key=lambda x: x['performance']['avg_error'])
        elif metric == 'exact_matches':
            successful.sort(key=lambda x: x['performance']['exact_matches'], reverse=True)
        elif metric == 'close_matches':
            successful.sort(key=lambda x: x['performance']['close_matches'], reverse=True)
        
        return successful[:5]  # Top 5
    
    def generate_ensemble_config(self, top_n: int = 3):
        """Generate configuration for an ensemble of top performers"""
        
        best_score = self.get_best_performers('score')[:top_n]
        best_exact = self.get_best_performers('exact_matches')[:top_n]
        
        ensemble_config = {
            'type': 'ensemble',
            'timestamp': datetime.datetime.now().isoformat(),
            'components': {
                'score_based': [r['variant_id'] for r in best_score],
                'exact_based': [r['variant_id'] for r in best_exact]
            },
            'suggested_weights': {
                'score_weight': 0.7,
                'exact_weight': 0.3
            }
        }
        
        ensemble_file = f"ensemble_config_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(os.path.join(self.algorithms_dir, ensemble_file), 'w') as f:
            json.dump(ensemble_config, f, indent=2)
        
        print(f"🎯 ENSEMBLE CONFIGURATION")
        print("=" * 40)
        print(f"Best by Score: {', '.join(ensemble_config['components']['score_based'])}")
        print(f"Best by Exact: {', '.join(ensemble_config['components']['exact_based'])}")
        print(f"Configuration saved to: {ensemble_file}")
        
        return ensemble_config

def main():
    """Main interface for algorithm management"""
    
    manager = AlgorithmManager()
    
    print("🎛️  ALGORITHM MANAGEMENT SYSTEM")
    print("=" * 50)
    
    while True:
        print("\nOptions:")
        print("1. Save current algorithm")
        print("2. Load algorithm variant")
        print("3. List all algorithms")
        print("4. Compare algorithms")
        print("5. Show best performers")
        print("6. Generate ensemble config")
        print("7. Exit")
        
        choice = input("\nEnter choice (1-7): ").strip()
        
        if choice == '1':
            name = input("Variant name: ").strip()
            desc = input("Description: ").strip()
            manager.save_current_algorithm(name, desc)
        
        elif choice == '2':
            name = input("Variant name to load: ").strip()
            manager.load_algorithm(name)
        
        elif choice == '3':
            manager.list_algorithms()
        
        elif choice == '4':
            variants = input("Variant names (comma-separated, or empty for all): ").strip()
            variant_list = [v.strip() for v in variants.split(',')] if variants else None
            manager.compare_algorithms(variant_list)
        
        elif choice == '5':
            metric = input("Metric (score/avg_error/exact_matches/close_matches): ").strip() or 'score'
            best = manager.get_best_performers(metric)
            print(f"\n🏆 Top 5 by {metric}:")
            for i, result in enumerate(best):
                perf = result['performance']
                print(f"{i+1}. {result['variant_id']}: {perf.get(metric, 'N/A')}")
        
        elif choice == '6':
            n = input("Number of top performers to include (default 3): ").strip()
            n = int(n) if n.isdigit() else 3
            manager.generate_ensemble_config(n)
        
        elif choice == '7':
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    # Quick demo of capabilities
    manager = AlgorithmManager()
    
    print("🎯 ALGORITHM MANAGEMENT DEMO")
    print("=" * 40)
    
    # Save current best algorithm
    manager.save_current_algorithm(
        "moderate_penalties_v13", 
        "Current best with moderate penalties - Score 16,922",
        {'score': 16922, 'avg_error': 168.22, 'exact_matches': 0, 'close_matches': 9}
    )
    
    # Show comparison
    manager.compare_algorithms()
    
    # Generate ensemble config
    manager.generate_ensemble_config()
    
    print(f"\n💡 Use 'python3 algorithm_manager.py' for interactive mode") 