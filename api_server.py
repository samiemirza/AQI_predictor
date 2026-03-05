#!/usr/bin/env python3
"""
Flask API server for the AQI Prediction System.
Provides REST endpoints for the React frontend.
"""
import os
import sys
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Now import the modules
try:
    from pipeline import run_feature_pipeline, run_training_pipeline, run_inference_pipeline
    from data_fetcher import fetch_air_pollution_history
    from config import get_api_key
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'AQI Prediction API is running'
    })

@app.route('/api/current-aqi', methods=['GET'])
def get_current_aqi():
    """Get current AQI for a location"""
    try:
        lat = float(request.args.get('lat'))
        lng = float(request.args.get('lng'))
        
        # Fetch current air pollution data (last 24h history)
        from datetime import datetime, timedelta, timezone
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(days=1)
        data = fetch_air_pollution_history(lat, lng, start_time, end_time)
        
        if data.empty:
            return jsonify({'error': 'No data available for this location'}), 404
        
        # Get the most recent data point
        latest = data.iloc[-1]
        
        # Calculate AQI
        from aqi_calculator import calculate_aqi_numerical, get_aqi_category
        
        aqi_numerical = calculate_aqi_numerical(latest)
        aqi_category = get_aqi_category(aqi_numerical)
        
        return jsonify({
            'aqi_numerical': int(aqi_numerical),
            'aqi_category': aqi_category,
            'dominant_pollutant': 'pm2_5',  # Simplified
            'timestamp': latest.name.isoformat(),
            'pollutants': {
                'co': float(latest.get('co', 0)),
                'no': float(latest.get('no', 0)),
                'no2': float(latest.get('no2', 0)),
                'o3': float(latest.get('o3', 0)),
                'so2': float(latest.get('so2', 0)),
                'pm2_5': float(latest.get('pm2_5', 0)),
                'pm10': float(latest.get('pm10', 0)),
                'nh3': float(latest.get('nh3', 0))
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-predictions', methods=['POST'])
def generate_predictions():
    """Generate AQI predictions for a location"""
    try:
        data = request.get_json()
        lat = float(data.get('lat'))
        lng = float(data.get('lng'))
        
        # Run the complete pipeline
        print(f"🔄 Starting prediction pipeline for ({lat}, {lng})")
        
        # Step 1: Update data
        print("📊 Updating air pollution data...")
        run_feature_pipeline(lat, lng, days_back=5)
        
        # Step 2: Train models (if needed)
        print("🤖 Training models...")
        run_training_pipeline()
        
        # Step 3: Generate predictions (returns DataFrame with exactly 3 horizons: 24/48/72h)
        print("🔮 Generating predictions...")
        predictions = run_inference_pipeline(lat, lng)
        
        if predictions is None:
            return jsonify({'error': 'Failed to generate predictions'}), 500
        
        # Format predictions for frontend
        formatted_predictions = []
        from aqi_calculator import get_aqi_category
        for _, row in predictions.iterrows():
            category_info = get_aqi_category(row['predicted_aqi'])
            formatted_predictions.append({
                'timestamp': row['timestamp'].isoformat() if hasattr(row['timestamp'], 'isoformat') else str(row['timestamp']),
                'predicted_aqi': int(row['predicted_aqi']),
                'aqi_category': category_info.get('category'),
                'aqi_color': category_info.get('color'),
                'hour_ahead': int(row.get('horizon_hours', 0)),
            })
        return jsonify(formatted_predictions)
        
    except Exception as e:
        print(f"❌ Error generating predictions: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/predictions', methods=['GET'])
def get_predictions():
    """Get predictions for a location (simplified version)"""
    try:
        lat = float(request.args.get('lat'))
        lng = float(request.args.get('lng'))
        
        # Run inference only (returns DataFrame with exactly 3 horizons: 24/48/72h)
        predictions = run_inference_pipeline(lat, lng)
        
        if predictions is None:
            return jsonify({'error': 'No predictions available'}), 404
        
        # Format predictions
        formatted_predictions = []
        from aqi_calculator import get_aqi_category
        for _, row in predictions.iterrows():
            category_info = get_aqi_category(row['predicted_aqi'])
            formatted_predictions.append({
                'timestamp': row['timestamp'].isoformat() if hasattr(row['timestamp'], 'isoformat') else str(row['timestamp']),
                'predicted_aqi': int(row['predicted_aqi']),
                'aqi_category': category_info.get('category'),
                'aqi_color': category_info.get('color'),
                'hour_ahead': int(row.get('horizon_hours', 0)),
            })
        return jsonify(formatted_predictions)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/update-data', methods=['POST'])
def update_data():
    """Update air pollution data for a location"""
    try:
        data = request.get_json()
        lat = float(data.get('lat'))
        lng = float(data.get('lng'))
        days_back = int(data.get('days_back', 5))
        
        run_feature_pipeline(lat, lng, days_back=days_back)
        
        return jsonify({
            'message': 'Data updated successfully',
            'location': {'lat': lat, 'lng': lng},
            'days_back': days_back
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/train-models', methods=['POST'])
def train_models():
    """Train the ML models"""
    try:
        result = run_training_pipeline()
        
        return jsonify({
            'message': 'Models trained successfully',
            'best_model': result.name if result else 'Unknown',
            'rmse': result.metrics.get('rmse', 0) if result else 0
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Check if API key is available
    if not get_api_key():
        print("❌ Warning: OPENWEATHER_API_KEY not set. Some features may not work.")
    
    print("🚀 Starting AQI Prediction API Server...")
    print("📡 API will be available at: http://localhost:5001")
    print("🌐 React frontend should be at: http://localhost:3000")
    
    app.run(host='0.0.0.0', port=5001, debug=True) 