#!/usr/bin/env python3

import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
from calculate_reimbursement import calculate_reimbursement

# Set style for better-looking plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def load_data():
    """Load and prepare data for visualization"""
    with open('public_cases.json', 'r') as f:
        data = json.load(f)
    
    cases = []
    for i, case in enumerate(data):
        duration = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        expected = case['expected_output']
        
        # Calculate our prediction
        predicted = calculate_reimbursement(duration, miles, receipts)
        
        cases.append({
            'case_id': i + 1,
            'duration': duration,
            'miles': miles,
            'receipts': receipts,
            'expected': expected,
            'predicted': predicted,
            'error': abs(predicted - expected),
            'per_day_rate': expected / duration,
            'miles_per_day': miles / duration,
            'receipts_per_day': receipts / duration,
            'receipt_ratio': expected / receipts if receipts > 0 else 0
        })
    
    return cases

def plot_inverse_relationship(cases):
    """Plot the inverse relationship between trip duration and per-day rates"""
    
    # Group by duration
    by_duration = defaultdict(list)
    for case in cases:
        by_duration[case['duration']].append(case['per_day_rate'])
    
    durations = sorted(by_duration.keys())
    mean_rates = [np.mean(by_duration[d]) for d in durations]
    std_rates = [np.std(by_duration[d]) for d in durations]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Plot 1: Mean per-day rates with error bars
    ax1.errorbar(durations, mean_rates, yerr=std_rates, 
                marker='o', capsize=5, capthick=2, linewidth=2)
    ax1.set_xlabel('Trip Duration (days)')
    ax1.set_ylabel('Mean Per-Day Rate ($)')
    ax1.set_title('Inverse Relationship: Duration vs Per-Day Rate')
    ax1.grid(True, alpha=0.3)
    
    # Add fitted curve
    x_smooth = np.linspace(1, 14, 100)
    y_smooth = 814.88 / x_smooth + 79.20
    ax1.plot(x_smooth, y_smooth, 'r--', alpha=0.7, 
             label='Fitted: rate = 814.88/duration + 79.20')
    ax1.legend()
    
    # Plot 2: Scatter plot of all data points
    durations_all = [case['duration'] for case in cases]
    rates_all = [case['per_day_rate'] for case in cases]
    
    ax2.scatter(durations_all, rates_all, alpha=0.6, s=20)
    ax2.plot(x_smooth, y_smooth, 'r-', linewidth=2, 
             label='R² = 0.9926')
    ax2.set_xlabel('Trip Duration (days)')
    ax2.set_ylabel('Per-Day Rate ($)')
    ax2.set_title('All Data Points: Duration vs Per-Day Rate')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    plt.tight_layout()
    plt.savefig('inverse_relationship.png', dpi=300, bbox_inches='tight')
    plt.show()

def plot_receipt_penalties(cases):
    """Plot receipt penalty patterns"""
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    
    # Plot 1: Receipt amount vs Receipt ratio
    receipts = [case['receipts'] for case in cases]
    ratios = [case['receipt_ratio'] for case in cases]
    
    ax1.scatter(receipts, ratios, alpha=0.6, s=20)
    ax1.set_xlabel('Receipt Amount ($)')
    ax1.set_ylabel('Reimbursement/Receipt Ratio')
    ax1.set_title('Receipt Penalties: Amount vs Ratio')
    ax1.grid(True, alpha=0.3)
    
    # Add threshold lines
    ax1.axvline(x=500, color='orange', linestyle='--', alpha=0.7, label='$500 threshold')
    ax1.axvline(x=1500, color='red', linestyle='--', alpha=0.7, label='$1500 threshold')
    ax1.axvline(x=2000, color='darkred', linestyle='--', alpha=0.7, label='$2000 threshold')
    ax1.legend()
    
    # Plot 2: Receipt ranges and mean ratios
    ranges = [(0, 500), (500, 1000), (1000, 1500), (1500, 2000), (2000, 2500), (2500, float('inf'))]
    range_names = ['$0-500', '$500-1000', '$1000-1500', '$1500-2000', '$2000-2500', '$2500+']
    mean_ratios = []
    
    for min_r, max_r in ranges:
        range_ratios = [case['receipt_ratio'] for case in cases 
                       if min_r <= case['receipts'] < max_r]
        mean_ratios.append(np.mean(range_ratios) if range_ratios else 0)
    
    bars = ax2.bar(range_names, mean_ratios, color=sns.color_palette("viridis", len(ranges)))
    ax2.set_xlabel('Receipt Amount Range')
    ax2.set_ylabel('Mean Reimbursement/Receipt Ratio')
    ax2.set_title('Receipt Penalty by Amount Range')
    ax2.tick_params(axis='x', rotation=45)
    
    # Add value labels on bars
    for bar, ratio in zip(bars, mean_ratios):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                f'{ratio:.2f}', ha='center', va='bottom')
    
    # Plot 3: High-error cases analysis
    high_error_cases = sorted(cases, key=lambda x: x['error'], reverse=True)[:20]
    
    error_receipts = [case['receipts'] for case in high_error_cases]
    error_durations = [case['duration'] for case in high_error_cases]
    errors = [case['error'] for case in high_error_cases]
    
    scatter = ax3.scatter(error_receipts, error_durations, c=errors, 
                         s=100, cmap='Reds', alpha=0.8)
    ax3.set_xlabel('Receipt Amount ($)')
    ax3.set_ylabel('Trip Duration (days)')
    ax3.set_title('High-Error Cases: Receipts vs Duration')
    ax3.grid(True, alpha=0.3)
    
    # Add colorbar
    cbar = plt.colorbar(scatter, ax=ax3)
    cbar.set_label('Error Amount ($)')
    
    # Plot 4: Performance comparison
    predicted = [case['predicted'] for case in cases]
    expected = [case['expected'] for case in cases]
    
    ax4.scatter(expected, predicted, alpha=0.6, s=20)
    
    # Perfect prediction line
    min_val = min(min(expected), min(predicted))
    max_val = max(max(expected), max(predicted))
    ax4.plot([min_val, max_val], [min_val, max_val], 'r--', alpha=0.8, label='Perfect Prediction')
    
    ax4.set_xlabel('Expected Reimbursement ($)')
    ax4.set_ylabel('Predicted Reimbursement ($)')
    ax4.set_title('Algorithm Performance: Expected vs Predicted')
    ax4.grid(True, alpha=0.3)
    ax4.legend()
    
    plt.tight_layout()
    plt.savefig('receipt_penalties.png', dpi=300, bbox_inches='tight')
    plt.show()

def plot_efficiency_patterns(cases):
    """Plot efficiency and mileage patterns"""
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    
    # Plot 1: Miles per day vs per-day rate
    miles_per_day = [case['miles_per_day'] for case in cases]
    per_day_rates = [case['per_day_rate'] for case in cases]
    
    ax1.scatter(miles_per_day, per_day_rates, alpha=0.6, s=20)
    ax1.set_xlabel('Miles per Day')
    ax1.set_ylabel('Per-Day Rate ($)')
    ax1.set_title('Efficiency Pattern: Miles/Day vs Rate')
    ax1.grid(True, alpha=0.3)
    
    # Highlight sweet spot
    ax1.axvspan(180, 220, alpha=0.2, color='green', label='Sweet Spot (180-220 mi/day)')
    ax1.legend()
    
    # Plot 2: 5-day trip analysis
    five_day_cases = [case for case in cases if case['duration'] == 5]
    
    if five_day_cases:
        five_day_miles = [case['miles_per_day'] for case in five_day_cases]
        five_day_rates = [case['per_day_rate'] for case in five_day_cases]
        five_day_receipts = [case['receipts_per_day'] for case in five_day_cases]
        
        scatter = ax2.scatter(five_day_miles, five_day_rates, c=five_day_receipts, 
                             s=50, cmap='viridis', alpha=0.8)
        ax2.set_xlabel('Miles per Day')
        ax2.set_ylabel('Per-Day Rate ($)')
        ax2.set_title('5-Day Trips: Efficiency vs Rate (colored by receipts/day)')
        ax2.grid(True, alpha=0.3)
        
        # Sweet spot highlight
        ax2.axvspan(180, 220, alpha=0.2, color='green')
        
        # Add colorbar
        cbar = plt.colorbar(scatter, ax=ax2)
        cbar.set_label('Receipts per Day ($)')
    
    # Plot 3: Mileage distribution by duration
    durations = sorted(set(case['duration'] for case in cases))
    mileage_by_duration = []
    
    for duration in durations:
        duration_miles = [case['miles'] for case in cases if case['duration'] == duration]
        mileage_by_duration.append(duration_miles)
    
    ax3.boxplot(mileage_by_duration, labels=durations)
    ax3.set_xlabel('Trip Duration (days)')
    ax3.set_ylabel('Total Miles')
    ax3.set_title('Mileage Distribution by Trip Duration')
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Error distribution
    errors = [case['error'] for case in cases]
    
    ax4.hist(errors, bins=50, alpha=0.7, edgecolor='black')
    ax4.set_xlabel('Prediction Error ($)')
    ax4.set_ylabel('Number of Cases')
    ax4.set_title('Error Distribution')
    ax4.grid(True, alpha=0.3)
    
    # Add statistics
    mean_error = np.mean(errors)
    median_error = np.median(errors)
    ax4.axvline(mean_error, color='red', linestyle='--', label=f'Mean: ${mean_error:.2f}')
    ax4.axvline(median_error, color='orange', linestyle='--', label=f'Median: ${median_error:.2f}')
    ax4.legend()
    
    plt.tight_layout()
    plt.savefig('efficiency_patterns.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_summary_dashboard(cases):
    """Create a comprehensive dashboard"""
    
    fig = plt.figure(figsize=(20, 12))
    
    # Create a grid layout
    gs = fig.add_gridspec(3, 4, hspace=0.3, wspace=0.3)
    
    # Key metrics
    ax1 = fig.add_subplot(gs[0, 0])
    total_cases = len(cases)
    avg_error = np.mean([case['error'] for case in cases])
    close_matches = sum(1 for case in cases if case['error'] < 1.0)
    
    metrics = ['Total Cases', 'Avg Error ($)', 'Close Matches', 'Success Rate (%)']
    values = [total_cases, avg_error, close_matches, (close_matches/total_cases)*100]
    
    ax1.bar(metrics, values, color=['skyblue', 'lightcoral', 'lightgreen', 'gold'])
    ax1.set_title('Key Performance Metrics')
    ax1.tick_params(axis='x', rotation=45)
    
    # Duration distribution
    ax2 = fig.add_subplot(gs[0, 1])
    durations = [case['duration'] for case in cases]
    ax2.hist(durations, bins=range(1, 16), alpha=0.7, edgecolor='black')
    ax2.set_xlabel('Trip Duration (days)')
    ax2.set_ylabel('Count')
    ax2.set_title('Trip Duration Distribution')
    
    # Receipt amount distribution
    ax3 = fig.add_subplot(gs[0, 2])
    receipts = [case['receipts'] for case in cases]
    ax3.hist(receipts, bins=50, alpha=0.7, edgecolor='black')
    ax3.set_xlabel('Receipt Amount ($)')
    ax3.set_ylabel('Count')
    ax3.set_title('Receipt Amount Distribution')
    
    # Miles distribution
    ax4 = fig.add_subplot(gs[0, 3])
    miles = [case['miles'] for case in cases]
    ax4.hist(miles, bins=50, alpha=0.7, edgecolor='black')
    ax4.set_xlabel('Miles Traveled')
    ax4.set_ylabel('Count')
    ax4.set_title('Miles Distribution')
    
    # Large plots
    # Inverse relationship
    ax5 = fig.add_subplot(gs[1, :2])
    by_duration = defaultdict(list)
    for case in cases:
        by_duration[case['duration']].append(case['per_day_rate'])
    
    durations = sorted(by_duration.keys())
    mean_rates = [np.mean(by_duration[d]) for d in durations]
    
    ax5.plot(durations, mean_rates, 'o-', linewidth=2, markersize=8)
    x_smooth = np.linspace(1, 14, 100)
    y_smooth = 814.88 / x_smooth + 79.20
    ax5.plot(x_smooth, y_smooth, 'r--', alpha=0.7, label='Fitted Curve (R² = 0.9926)')
    ax5.set_xlabel('Trip Duration (days)')
    ax5.set_ylabel('Mean Per-Day Rate ($)')
    ax5.set_title('Inverse Relationship: Duration vs Per-Day Rate')
    ax5.grid(True, alpha=0.3)
    ax5.legend()
    
    # Performance scatter
    ax6 = fig.add_subplot(gs[1, 2:])
    expected = [case['expected'] for case in cases]
    predicted = [case['predicted'] for case in cases]
    errors = [case['error'] for case in cases]
    
    scatter = ax6.scatter(expected, predicted, c=errors, s=30, cmap='Reds', alpha=0.7)
    
    min_val = min(min(expected), min(predicted))
    max_val = max(max(expected), max(predicted))
    ax6.plot([min_val, max_val], [min_val, max_val], 'g--', alpha=0.8, label='Perfect Prediction')
    
    ax6.set_xlabel('Expected Reimbursement ($)')
    ax6.set_ylabel('Predicted Reimbursement ($)')
    ax6.set_title('Algorithm Performance (colored by error)')
    ax6.grid(True, alpha=0.3)
    ax6.legend()
    
    cbar = plt.colorbar(scatter, ax=ax6)
    cbar.set_label('Error ($)')
    
    # Bottom row: Receipt penalties
    ax7 = fig.add_subplot(gs[2, :])
    
    # Create receipt penalty visualization
    receipt_ranges = [(0, 500), (500, 1000), (1000, 1500), (1500, 2000), (2000, 2500), (2500, float('inf'))]
    range_names = ['$0-500', '$500-1K', '$1K-1.5K', '$1.5K-2K', '$2K-2.5K', '$2.5K+']
    mean_ratios = []
    case_counts = []
    
    for min_r, max_r in receipt_ranges:
        range_cases = [case for case in cases if min_r <= case['receipts'] < max_r]
        if range_cases:
            mean_ratios.append(np.mean([case['receipt_ratio'] for case in range_cases]))
            case_counts.append(len(range_cases))
        else:
            mean_ratios.append(0)
            case_counts.append(0)
    
    # Create dual y-axis plot
    ax7_twin = ax7.twinx()
    
    bars1 = ax7.bar(range_names, mean_ratios, alpha=0.7, color='skyblue', label='Mean Ratio')
    bars2 = ax7_twin.bar(range_names, case_counts, alpha=0.5, color='orange', label='Case Count')
    
    ax7.set_xlabel('Receipt Amount Range')
    ax7.set_ylabel('Mean Reimbursement/Receipt Ratio', color='blue')
    ax7_twin.set_ylabel('Number of Cases', color='orange')
    ax7.set_title('Receipt Penalty Analysis: Ratio and Case Distribution')
    
    # Add value labels
    for bar, ratio in zip(bars1, mean_ratios):
        height = bar.get_height()
        ax7.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                f'{ratio:.2f}', ha='center', va='bottom', fontsize=10)
    
    plt.suptitle('Legacy Reimbursement System - Reverse Engineering Dashboard', 
                 fontsize=16, fontweight='bold')
    
    plt.savefig('dashboard.png', dpi=300, bbox_inches='tight')
    plt.show()

def main():
    """Main visualization function"""
    print("🎨 Creating visualizations...")
    print("Loading data and calculating predictions...")
    
    cases = load_data()
    
    print(f"✅ Loaded {len(cases)} test cases")
    print(f"Average error: ${np.mean([case['error'] for case in cases]):.2f}")
    print()
    
    print("Creating plots...")
    
    # Create all visualizations
    plot_inverse_relationship(cases)
    plot_receipt_penalties(cases)
    plot_efficiency_patterns(cases)
    create_summary_dashboard(cases)
    
    print("✅ All visualizations saved!")
    print("Generated files:")
    print("  - inverse_relationship.png")
    print("  - receipt_penalties.png") 
    print("  - efficiency_patterns.png")
    print("  - dashboard.png")

if __name__ == "__main__":
    main() 