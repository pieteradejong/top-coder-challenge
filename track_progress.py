#!/usr/bin/env python3

import json
import datetime
from calculate_reimbursement import calculate_reimbursement

def track_progress():
    """Track our progress and update the progress log"""
    
    # Load test data
    with open('public_cases.json', 'r') as f:
        data = json.load(f)
    
    # Calculate current metrics
    total_error = 0
    exact_matches = 0
    close_matches = 0
    
    for case in data:
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
    
    avg_error = total_error / len(data)
    score = avg_error * 100 + (len(data) - exact_matches) * 0.1
    
    # Create progress entry
    progress_entry = {
        'timestamp': datetime.datetime.now().isoformat(),
        'attempt': 12,  # Current attempt number
        'avg_error': round(avg_error, 2),
        'exact_matches': exact_matches,
        'close_matches': close_matches,
        'score': round(score, 2),
        'total_cases': len(data),
        'description': 'Micro-tuned algorithm with systematic bias correction - FIRST EXACT MATCH!'
    }
    
    # Load existing progress or create new
    try:
        with open('progress_log.json', 'r') as f:
            progress_log = json.load(f)
    except FileNotFoundError:
        progress_log = []
    
    # Add new entry
    progress_log.append(progress_entry)
    
    # Save updated progress
    with open('progress_log.json', 'w') as f:
        json.dump(progress_log, f, indent=2)
    
    print(f"📊 Progress tracked:")
    print(f"  Attempt: {progress_entry['attempt']}")
    print(f"  Average Error: ${progress_entry['avg_error']}")
    print(f"  Exact Matches: {progress_entry['exact_matches']}")
    print(f"  Close Matches: {progress_entry['close_matches']}")
    print(f"  Score: {progress_entry['score']}")
    
    return progress_entry

def update_dashboard_with_real_data():
    """Update the dashboard with real progress data"""
    
    # Load progress log
    try:
        with open('progress_log.json', 'r') as f:
            progress_log = json.load(f)
    except FileNotFoundError:
        print("No progress log found. Run track_progress() first.")
        return
    
    # Load current test data for analysis
    with open('public_cases.json', 'r') as f:
        data = json.load(f)
    
    # Calculate current detailed metrics
    cases_data = []
    for i, case in enumerate(data[:100]):  # Limit for performance
        duration = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        expected = case['expected_output']
        
        predicted = calculate_reimbursement(duration, miles, receipts)
        error = abs(predicted - expected)
        
        cases_data.append({
            'case_id': i + 1,
            'duration': duration,
            'miles': miles,
            'receipts': receipts,
            'expected': expected,
            'predicted': predicted,
            'error': error,
            'miles_per_day': miles / duration,
            'receipts_per_day': receipts / duration
        })
    
    # Get latest metrics
    latest = progress_log[-1]
    
    # Generate updated HTML
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Legacy Reimbursement System - Live Dashboard</title>
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
        .timestamp {{ font-size: 0.9em; color: #7f8c8d; text-align: center; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧾 Legacy Reimbursement System</h1>
            <p>Live Reverse Engineering Dashboard - 60-Year-Old Black Box Challenge</p>
            <div class="timestamp">Last updated: {latest['timestamp'][:19].replace('T', ' ')}</div>
        </div>
        
        <div class="goal-tracker">
            <h2>🎯 Challenge Goal: Extremely High Fidelity</h2>
            <div style="background: rgba(255,255,255,0.2); border-radius: 10px; padding: 15px; margin: 15px 0;">
                <strong>Target:</strong> 1,000 exact matches (±$0.01) | <strong>Current:</strong> {latest['exact_matches']} exact matches
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {(latest['exact_matches']/1000)*100:.1f}%"></div>
                </div>
                <p>Progress: {(latest['exact_matches']/1000)*100:.1f}% toward perfect replication</p>
            </div>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">{latest['avg_error']}</div>
                <div class="metric-label">Average Error ($)</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{latest['exact_matches']}</div>
                <div class="metric-label">Exact Matches</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{latest['close_matches']}</div>
                <div class="metric-label">Close Matches (±$1)</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{latest['score']:.0f}</div>
                <div class="metric-label">Score (lower better)</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{latest['attempt']}</div>
                <div class="metric-label">Attempt #</div>
            </div>
        </div>
        
        <div class="chart-container">
            <div class="chart-title">📈 Algorithm Progress Over Time (Live Data)</div>
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
            <h3>🚨 Current Status Assessment</h3>
            
            <div class="problem-pattern">
                <strong>Zero Exact Matches - Critical Issue</strong><br>
                We're not achieving the "extremely high fidelity" requirement. Need to focus on exact replication rather than just minimizing average error.
            </div>
            
            <div class="problem-pattern">
                <strong>High Error on Long Trips</strong><br>
                Cases with 8+ days still showing high errors. Our vacation penalty logic needs refinement.
            </div>
            
            <div class="success-pattern">
                <strong>Some Targeted Improvements Working</strong><br>
                Fixed several 1-day high-mileage cases, but overall average error increased slightly.
            </div>
        </div>
        
        <div class="insights">
            <h3>🎯 Next Priority Actions</h3>
            <ol>
                <li><strong>Focus on exact matches:</strong> Analyze the closest cases to understand what makes them work</li>
                <li><strong>Reverse engineer specific patterns:</strong> Look for mathematical relationships in successful cases</li>
                <li><strong>Test incremental changes:</strong> Make smaller, more targeted adjustments</li>
                <li><strong>Analyze rounding behavior:</strong> The legacy system may have specific rounding quirks</li>
            </ol>
        </div>
    </div>
    
    <script>
        const progressData = {json.dumps(progress_log)};
        const casesData = {json.dumps(cases_data)};
        
        // Progress chart with real data
        Plotly.newPlot('progress-chart', [{{
            x: progressData.map(d => d.attempt),
            y: progressData.map(d => d.avg_error),
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Average Error',
            line: {{color: '#e74c3c', width: 3}},
            marker: {{size: 8}},
            text: progressData.map(d => d.description),
            hovertemplate: 'Attempt %{{x}}<br>Error: $%{{y:.2f}}<br>%{{text}}<extra></extra>'
        }}, {{
            x: progressData.map(d => d.attempt),
            y: progressData.map(d => d.close_matches),
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Close Matches',
            yaxis: 'y2',
            line: {{color: '#27ae60', width: 3}},
            marker: {{size: 8}},
            hovertemplate: 'Attempt %{{x}}<br>Close Matches: %{{y}}<extra></extra>'
        }}], {{
            title: 'Real Algorithm Performance Over Time',
            xaxis: {{title: 'Attempt Number'}},
            yaxis: {{title: 'Average Error ($)', side: 'left'}},
            yaxis2: {{title: 'Close Matches', side: 'right', overlaying: 'y'}},
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
            title: 'Distribution of Prediction Errors (Sample)',
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
    
    # Write updated HTML file
    with open('dashboard.html', 'w') as f:
        f.write(html_content)
    
    print("✅ Dashboard updated with real progress data")
    print("🌐 Open dashboard.html to view the live dashboard")

if __name__ == "__main__":
    track_progress()
    update_dashboard_with_real_data() 