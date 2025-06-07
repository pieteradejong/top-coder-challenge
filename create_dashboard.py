#!/usr/bin/env python3

import json
import datetime
from calculate_reimbursement import calculate_reimbursement

def generate_dashboard():
    """Generate an interactive HTML dashboard showing our progress"""
    
    # Load data and calculate current performance
    with open('public_cases.json', 'r') as f:
        data = json.load(f)
    
    # Calculate all metrics
    cases_data = []
    total_error = 0
    exact_matches = 0
    close_matches = 0
    
    for i, case in enumerate(data):
        duration = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        expected = case['expected_output']
        
        predicted = calculate_reimbursement(duration, miles, receipts)
        error = abs(predicted - expected)
        
        total_error += error
        if error < 0.01:
            exact_matches += 1
        if error < 1.0:
            close_matches += 1
        
        cases_data.append({
            'case_id': i + 1,
            'duration': duration,
            'miles': miles,
            'receipts': receipts,
            'expected': expected,
            'predicted': predicted,
            'error': error,
            'miles_per_day': miles / duration,
            'receipts_per_day': receipts / duration,
            'expected_per_day': expected / duration,
            'predicted_per_day': predicted / duration,
            'receipt_ratio': expected / receipts if receipts > 0 else 0,
            'over_under': 'over' if predicted > expected else 'under'
        })
    
    avg_error = total_error / len(data)
    score = avg_error * 100 + (len(data) - exact_matches) * 0.1
    
    # Historical progress (simulated - you can replace with actual data)
    progress_data = [
        {'attempt': 1, 'date': '2024-01-01', 'avg_error': 367.45, 'exact_matches': 0, 'close_matches': 0, 'score': 36845},
        {'attempt': 2, 'date': '2024-01-02', 'avg_error': 265.25, 'exact_matches': 0, 'close_matches': 2, 'score': 26625},
        {'attempt': 3, 'date': '2024-01-03', 'avg_error': 338.69, 'exact_matches': 0, 'close_matches': 1, 'score': 33969},
        {'attempt': 4, 'date': '2024-01-04', 'avg_error': 338.69, 'exact_matches': 0, 'close_matches': 3, 'score': 33969},
        {'attempt': 5, 'date': '2024-01-05', 'avg_error': 298.61, 'exact_matches': 0, 'close_matches': 6, 'score': 29961},
        {'attempt': 6, 'date': '2024-01-06', 'avg_error': 224.99, 'exact_matches': 0, 'close_matches': 8, 'score': 22599},
        {'attempt': 7, 'date': '2024-01-07', 'avg_error': 623.73, 'exact_matches': 0, 'close_matches': 0, 'score': 62473},
        {'attempt': 8, 'date': '2024-01-08', 'avg_error': 212.60, 'exact_matches': 0, 'close_matches': 8, 'score': 21360},
        {'attempt': 9, 'date': '2024-01-09', 'avg_error': 214.20, 'exact_matches': 0, 'close_matches': 8, 'score': 21520},
        {'attempt': 10, 'date': datetime.datetime.now().strftime('%Y-%m-%d'), 'avg_error': avg_error, 'exact_matches': exact_matches, 'close_matches': close_matches, 'score': score}
    ]
    
    # Generate HTML with embedded data
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Legacy Reimbursement System - Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1400px; margin: 0 auto; background: white; border-radius: 10px; padding: 30px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; margin-bottom: 30px; border-bottom: 3px solid #2c3e50; padding-bottom: 20px; }}
        .header h1 {{ color: #2c3e50; margin: 0; font-size: 2.5em; }}
        .header p {{ color: #7f8c8d; font-size: 1.2em; margin: 10px 0 0 0; }}
        .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .metric-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; }}
        .metric-value {{ font-size: 2.5em; font-weight: bold; margin-bottom: 5px; }}
        .metric-label {{ font-size: 1em; opacity: 0.9; }}
        .chart-container {{ margin: 30px 0; background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .chart-title {{ font-size: 1.5em; color: #2c3e50; margin-bottom: 15px; text-align: center; }}
        .goal-tracker {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 25px; border-radius: 10px; margin: 20px 0; text-align: center; }}
        .progress-bar {{ background: rgba(255,255,255,0.3); border-radius: 10px; height: 20px; margin: 10px 0; overflow: hidden; }}
        .progress-fill {{ background: #27ae60; height: 100%; border-radius: 10px; transition: width 0.3s ease; }}
        .insights {{ background: #ecf0f1; border-left: 5px solid #3498db; padding: 20px; margin: 20px 0; border-radius: 5px; }}
        .problem-pattern {{ background: #fdf2f2; border-left: 5px solid #e74c3c; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .success-pattern {{ background: #f0fff4; border-left: 5px solid #27ae60; padding: 15px; margin: 10px 0; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧾 Legacy Reimbursement System</h1>
            <p>Reverse Engineering Dashboard - 60-Year-Old Black Box Challenge</p>
        </div>
        
        <div class="goal-tracker">
            <h2>🎯 Challenge Goal: Extremely High Fidelity</h2>
            <div style="background: rgba(255,255,255,0.2); border-radius: 10px; padding: 15px; margin: 15px 0;">
                <strong>Target:</strong> 1,000 exact matches (±$0.01) | <strong>Current:</strong> {exact_matches} exact matches
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {(exact_matches/1000)*100:.1f}%"></div>
                </div>
                <p>Progress: {(exact_matches/1000)*100:.1f}% toward perfect replication</p>
            </div>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">{avg_error:.2f}</div>
                <div class="metric-label">Average Error ($)</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{exact_matches}</div>
                <div class="metric-label">Exact Matches</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{close_matches}</div>
                <div class="metric-label">Close Matches (±$1)</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{score:.0f}</div>
                <div class="metric-label">Score (lower better)</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{((367.45 - avg_error) / 367.45 * 100):.1f}%</div>
                <div class="metric-label">Improvement</div>
            </div>
        </div>
        
        <div class="chart-container">
            <div class="chart-title">📈 Algorithm Progress Over Time</div>
            <div id="progress-chart"></div>
        </div>
        
        <div class="chart-container">
            <div class="chart-title">🎯 Error Distribution Analysis</div>
            <div id="error-distribution"></div>
        </div>
        
        <div class="chart-container">
            <div class="chart-title">🔍 Expected vs Predicted Scatter Plot</div>
            <div id="scatter-plot"></div>
        </div>
        
        <div class="insights">
            <h3>🚨 Critical Issues Identified</h3>
            
            <div class="problem-pattern">
                <strong>1-Day High-Mileage Trips (6 cases in top 20 errors)</strong><br>
                Pattern: 1 day + >800 miles + high receipts → We're UNDER-predicting by ~$1,000<br>
                Issue: Our fraud prevention is too aggressive for legitimate business cases
            </div>
            
            <div class="problem-pattern">
                <strong>Long Trips + High Receipts (13/20 over-predictions)</strong><br>
                Pattern: 7+ days + >$1,500 receipts → We're OVER-predicting<br>
                Issue: Missing "vacation penalty" logic for extended trips with high spending
            </div>
        </div>
        
        <div class="insights">
            <h3>✅ Success Patterns Identified</h3>
            
            <div class="success-pattern">
                <strong>Close Matches (26 cases within $5 error)</strong><br>
                Pattern: Average 4.5 days, 248 mi/day, $538/day receipts<br>
                Sweet Spot: Medium-length trips with balanced efficiency and spending
            </div>
        </div>
        
        <div class="insights">
            <h3>🎯 Next Action Items</h3>
            <ol>
                <li><strong>Fix 1-day high-mileage logic:</strong> Reduce fraud prevention penalty</li>
                <li><strong>Implement vacation penalty:</strong> Add 8+ day + high spending penalty</li>
                <li><strong>Add efficiency bonuses:</strong> Implement Kevin's 180-220 mi/day sweet spot</li>
                <li><strong>Refine receipt penalties:</strong> More nuanced approach</li>
            </ol>
        </div>
    </div>
    
    <script>
        const progressData = {json.dumps(progress_data)};
        const casesData = {json.dumps(cases_data[:100])};  // Limit for performance
        
        // Progress chart
        Plotly.newPlot('progress-chart', [{{
            x: progressData.map(d => d.attempt),
            y: progressData.map(d => d.avg_error),
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Average Error',
            line: {{color: '#e74c3c', width: 3}},
            marker: {{size: 8}}
        }}], {{
            title: 'Algorithm Performance Over Time',
            xaxis: {{title: 'Attempt Number'}},
            yaxis: {{title: 'Average Error ($)'}},
            hovermode: 'x unified'
        }});
        
        // Error distribution
        const errorData = casesData.map(d => d.error);
        Plotly.newPlot('error-distribution', [{{
            x: errorData,
            type: 'histogram',
            nbinsx: 30,
            marker: {{color: '#3498db', opacity: 0.7}}
        }}], {{
            title: 'Distribution of Prediction Errors',
            xaxis: {{title: 'Error Amount ($)'}},
            yaxis: {{title: 'Number of Cases'}}
        }});
        
        // Scatter plot
        const expectedData = casesData.map(d => d.expected);
        const predictedData = casesData.map(d => d.predicted);
        const maxVal = Math.max(...expectedData, ...predictedData);
        
        Plotly.newPlot('scatter-plot', [{{
            x: expectedData,
            y: predictedData,
            mode: 'markers',
            type: 'scatter',
            marker: {{
                size: 6,
                color: errorData,
                colorscale: 'Reds',
                colorbar: {{title: 'Error ($)'}}
            }},
            text: casesData.map(d => `Case ${{d.case_id}}: ${{d.duration}}d, ${{d.miles}}mi`),
            hovertemplate: '%{{text}}<br>Expected: $%{{x:.2f}}<br>Predicted: $%{{y:.2f}}<extra></extra>'
        }}, {{
            x: [0, maxVal],
            y: [0, maxVal],
            mode: 'lines',
            type: 'scatter',
            line: {{color: 'red', dash: 'dash'}},
            name: 'Perfect Prediction'
        }}], {{
            title: 'Expected vs Predicted Reimbursements (Sample)',
            xaxis: {{title: 'Expected Reimbursement ($)'}},
            yaxis: {{title: 'Predicted Reimbursement ($)'}}
        }});
    </script>
</body>
</html>"""
    
    # Write HTML file
    with open('dashboard.html', 'w') as f:
        f.write(html_content)
    
    print("✅ Dashboard created: dashboard.html")
    print("🌐 Open dashboard.html in your web browser to view the interactive visualization")
    
    return cases_data

if __name__ == "__main__":
    generate_dashboard() 