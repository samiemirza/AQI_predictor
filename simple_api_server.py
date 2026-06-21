#!/usr/bin/env python3
"""
Simple Flask API server for the AQI Prediction System.
Uses subprocess to call existing Python scripts instead of complex imports.
"""
import os
import sys
import subprocess
import json
from datetime import datetime, timezone
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend


def _get_request_api_key():
    """Read the OpenWeather API key from the backend environment."""
    return os.getenv("OPENWEATHER_API_KEY")


def _format_prediction_row(row):
    ts = row["timestamp"]
    try:
        ts_iso = ts.isoformat()
    except Exception:
        ts_iso = str(ts)

    return {
        "timestamp": ts_iso,
        "predicted_aqi": float(row["predicted_aqi"]),
        "aqi_category": row.get("aqi_category", "Unknown"),
        "aqi_color": row.get("aqi_color", "gray"),
        "hour_ahead": int(row.get("horizon_hours", 0)),
    }

@app.route('/', methods=['GET'])
def index():
    """Basic index route to avoid confusing 404s on API root."""
    return jsonify({
        'message': 'AQI Prediction API server is running',
        'health': '/api/health'
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'AQI Prediction API is running'
    })

@app.route('/api/generate-predictions', methods=['POST'])
def generate_predictions():
    """Generate AQI predictions for a location using the REAL prediction pipeline only"""
    try:
        data = request.get_json()
        lat = float(data.get('lat'))
        lng = float(data.get('lng'))
        api_key = _get_request_api_key()

        print(f"🔄 Starting REAL prediction pipeline for ({lat}, {lng})")
        if not api_key:
            return jsonify({'error': 'OpenWeather API key not configured'}), 500

        env = os.environ.copy()
        env["OPENWEATHER_API_KEY"] = api_key

        # Call the REAL prediction pipeline using the non-interactive script
        result = subprocess.run([
            sys.executable, 'api_predict.py',
            '--lat', str(lat),
            '--lng', str(lng)
        ], capture_output=True, text=True, cwd=Path(__file__).parent, timeout=120, env=env)

        if result.returncode == 0:
            print("✅ REAL prediction pipeline completed successfully!")

            # Parse the JSON output
            try:
                prediction_data = json.loads(result.stdout)
                if prediction_data.get('success'):
                    print(f"📊 Generated {len(prediction_data['predictions'])} predictions")
                    return jsonify(prediction_data['predictions'])
                else:
                    print(f"❌ Prediction failed: {prediction_data.get('error')}")
                    return jsonify({'error': prediction_data.get('error', 'Unknown error')}), 500
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse prediction output: {e}")
                return jsonify({'error': 'Failed to parse prediction results'}), 500
        else:
            print(f"❌ Real pipeline failed: {result.stderr}")
            print(f"Return code: {result.returncode}")
            return jsonify({'error': f'Prediction pipeline failed: {result.stderr}'}), 500

    except subprocess.TimeoutExpired:
        print("❌ Real pipeline timed out")
        return jsonify({'error': 'Prediction pipeline timed out'}), 500
    except Exception as e:
        print(f"❌ Error generating predictions: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/current-aqi', methods=['GET'])
def get_current_aqi():
    """Get current AQI for a location from REAL API only"""
    try:
        lat = float(request.args.get('lat'))
        lng = float(request.args.get('lng'))

        print(f"🌡️ Fetching REAL current AQI for ({lat}, {lng})")

        sys.path.insert(0, str(Path(__file__).parent))
        from src.data_fetcher import fetch_current_air_pollution  # type: ignore
        from src.aqi_calculator import calculate_aqi_from_api_data  # type: ignore

        api_key = _get_request_api_key()
        if not api_key:
            print("❌ No API key available")
            return jsonify({'error': 'OpenWeather API key not configured'}), 500

        current_df = fetch_current_air_pollution(lat, lng, api_key=api_key)
        if current_df.empty:
            print("❌ No data in API response")
            return jsonify({'error': 'No air pollution data available for this location'}), 404

        current = current_df.iloc[-1]
        components = {
            'co': float(current.get('co', 0)),
            'no': float(current.get('no', 0)),
            'no2': float(current.get('no2', 0)),
            'o3': float(current.get('o3', 0)),
            'so2': float(current.get('so2', 0)),
            'pm2_5': float(current.get('pm2_5', 0)),
            'pm10': float(current.get('pm10', 0)),
            'nh3': float(current.get('nh3', 0)),
        }
        aqi_result = calculate_aqi_from_api_data(components)
        timestamp = datetime.fromtimestamp(float(current.get('dt')), tz=timezone.utc).isoformat()

        print(
            f"✅ Real AQI data fetched: {aqi_result['aqi']} "
            f"({aqi_result['category']}) - Dominant: {aqi_result['dominant_pollutant']}"
        )

        return jsonify({
            'aqi_numerical': aqi_result['aqi'],
            'aqi_category': aqi_result['category'],
            'aqi_color': aqi_result['color'],
            'dominant_pollutant': aqi_result['dominant_pollutant'],
            'timestamp': timestamp,
            'pollutants': components,
            'aqi_breakdown': aqi_result['sub_indices'],
        })

    except Exception as e:
        print(f"❌ Error in current AQI endpoint: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/predictions', methods=['GET'])
def get_predictions():
    """Return predictions for a location using the latest saved model only (no retraining)."""
    try:
        lat = float(request.args.get('lat'))
        lng = float(request.args.get('lng'))

        # Import pipeline and run inference only; do NOT retrain or update features here
        sys.path.insert(0, str(Path(__file__).parent))
        from src.pipeline import run_inference_pipeline  # type: ignore

        pred_df = run_inference_pipeline(
            lat,
            lng,
            api_key=_get_request_api_key(),
            prefer_direct_forecast=True,
        )
        if pred_df is None or pred_df.empty:
            return jsonify({'error': 'No predictions available'}), 404

        return jsonify([_format_prediction_row(row) for _, row in pred_df.iterrows()])

    except Exception as e:
        print(f"❌ Error getting predictions: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting AQI Prediction API Server...")
    print("📡 API will be available at: http://localhost:5001")
    print("🌐 React frontend should be at: http://localhost:3000")
    print("📊 Using REAL data from OpenWeather API and ML pipeline")

    app.run(host='0.0.0.0', port=5001, debug=os.getenv("FLASK_DEBUG") == "1")
