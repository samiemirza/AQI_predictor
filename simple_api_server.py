#!/usr/bin/env python3
"""
Simple Flask API server for the AQI Prediction System.
Uses subprocess to call existing Python scripts instead of complex imports.
"""
import os
import sys
import subprocess
import json
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

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
        
        print(f"🔄 Starting REAL prediction pipeline for ({lat}, {lng})")
        
        # Call the REAL prediction pipeline using the non-interactive script
        result = subprocess.run([
            sys.executable, 'api_predict.py', 
            '--lat', str(lat), 
            '--lng', str(lng)
        ], capture_output=True, text=True, cwd=Path(__file__).parent, timeout=120)
        
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
        
        # Get real data from OpenWeather API
        import requests
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        from config import get_api_key
        
        api_key = get_api_key()
        if not api_key:
            print("❌ No API key available")
            return jsonify({'error': 'OpenWeather API key not configured'}), 500
        
        # Call OpenWeather Air Pollution API
        url = f"http://api.openweathermap.org/data/2.5/air_pollution"
        params = {
            'lat': lat,
            'lon': lng,
            'appid': api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if 'list' in data and len(data['list']) > 0:
            current = data['list'][0]
            components = current['components']
            
            # US EPA AQI breakpoints and calculation
            def calculate_aqi_for_pollutant(concentration, pollutant):
                """Calculate AQI for a specific pollutant using US EPA standards"""
                
                # AQI breakpoints for different pollutants
                breakpoints = {
                    'pm2_5': [
                        (0, 12.0, 0, 50),
                        (12.1, 35.4, 51, 100),
                        (35.5, 55.4, 101, 150),
                        (55.5, 150.4, 151, 200),
                        (150.5, 250.4, 201, 300),
                        (250.5, 350.4, 301, 400),
                        (350.5, 500.4, 401, 500)
                    ],
                    'pm10': [
                        (0, 54, 0, 50),
                        (55, 154, 51, 100),
                        (155, 254, 101, 150),
                        (255, 354, 151, 200),
                        (355, 424, 201, 300),
                        (425, 504, 301, 400),
                        (505, 604, 401, 500)
                    ],
                    'o3': [
                        (0, 54, 0, 50),
                        (55, 70, 51, 100),
                        (71, 85, 101, 150),
                        (86, 105, 151, 200),
                        (106, 200, 201, 300)
                    ],
                    'no2': [
                        (0, 53, 0, 50),
                        (54, 100, 51, 100),
                        (101, 360, 101, 150),
                        (361, 649, 151, 200),
                        (650, 1249, 201, 300),
                        (1250, 1649, 301, 400),
                        (1650, 2049, 401, 500)
                    ],
                    'so2': [
                        (0, 35, 0, 50),
                        (36, 75, 51, 100),
                        (76, 185, 101, 150),
                        (186, 304, 151, 200),
                        (305, 604, 201, 300),
                        (605, 804, 301, 400),
                        (805, 1004, 401, 500)
                    ],
                    'co': [
                        (0, 4.4, 0, 50),
                        (4.5, 9.4, 51, 100),
                        (9.5, 12.4, 101, 150),
                        (12.5, 15.4, 151, 200),
                        (15.5, 30.4, 201, 300),
                        (30.5, 40.4, 301, 400),
                        (40.5, 50.4, 401, 500)
                    ]
                }
                
                if pollutant not in breakpoints:
                    return 0
                
                # Find the appropriate breakpoint range
                for bp_low, bp_high, aqi_low, aqi_high in breakpoints[pollutant]:
                    if bp_low <= concentration <= bp_high:
                        # Calculate AQI using linear interpolation
                        aqi = ((aqi_high - aqi_low) / (bp_high - bp_low)) * (concentration - bp_low) + aqi_low
                        return round(aqi)
                
                return 0
            
            # Calculate AQI for each pollutant
            aqi_values = {}
            aqi_values['pm2_5'] = calculate_aqi_for_pollutant(components.get('pm2_5', 0), 'pm2_5')
            aqi_values['pm10'] = calculate_aqi_for_pollutant(components.get('pm10', 0), 'pm10')
            aqi_values['o3'] = calculate_aqi_for_pollutant(components.get('o3', 0), 'o3')
            aqi_values['no2'] = calculate_aqi_for_pollutant(components.get('no2', 0), 'no2')
            aqi_values['so2'] = calculate_aqi_for_pollutant(components.get('so2', 0), 'so2')
            aqi_values['co'] = calculate_aqi_for_pollutant(components.get('co', 0), 'co')
            
            # Find the highest AQI value and its corresponding pollutant
            max_aqi = max(aqi_values.values())
            dominant_pollutant = max(aqi_values, key=aqi_values.get)
            
            # Determine category based on AQI value
            if max_aqi <= 50:
                category = "Good"
            elif max_aqi <= 100:
                category = "Moderate"
            elif max_aqi <= 150:
                category = "Unhealthy for Sensitive Groups"
            elif max_aqi <= 200:
                category = "Unhealthy"
            elif max_aqi <= 300:
                category = "Very Unhealthy"
            else:
                category = "Hazardous"
            
            print(f"✅ Real AQI data fetched: {max_aqi} ({category}) - Dominant: {dominant_pollutant}")
            print(f"📊 Individual AQIs: PM2.5={aqi_values['pm2_5']}, PM10={aqi_values['pm10']}, O3={aqi_values['o3']}, NO2={aqi_values['no2']}, SO2={aqi_values['so2']}, CO={aqi_values['co']}")
            
            return jsonify({
                'aqi_numerical': max_aqi,
                'aqi_category': category,
                'dominant_pollutant': dominant_pollutant,
                'timestamp': current.get('dt', '2024-01-15T12:00:00Z'),
                'pollutants': {
                    'co': float(components.get('co', 0)),
                    'no': float(components.get('no', 0)),
                    'no2': float(components.get('no2', 0)),
                    'o3': float(components.get('o3', 0)),
                    'so2': float(components.get('so2', 0)),
                    'pm2_5': float(components.get('pm2_5', 0)),
                    'pm10': float(components.get('pm10', 0)),
                    'nh3': float(components.get('nh3', 0))
                },
                'aqi_breakdown': aqi_values
            })
        else:
            print("❌ No data in API response")
            return jsonify({'error': 'No air pollution data available for this location'}), 404
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching real AQI data: {e}")
        return jsonify({'error': f'Failed to fetch air pollution data: {str(e)}'}), 500
    except Exception as e:
        print(f"❌ Error in current AQI endpoint: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/predictions', methods=['GET'])
def get_predictions():
    """Return predictions for a location using the latest saved model only (no retraining)."""
    try:
        lat = float(request.args.get('lat'))
        lng = float(request.args.get('lng'))

        # Import pipeline for inference only (as package import)
        sys.path.insert(0, str(Path(__file__).parent))
        from src.pipeline import run_inference_pipeline  # type: ignore

        pred_df = run_inference_pipeline(lat, lng)
        if pred_df is None or pred_df.empty:
            return jsonify({'error': 'No predictions available'}), 404

        formatted_predictions = []
        for i, (_, row) in enumerate(pred_df.iterrows()):
            ts = row['timestamp']
            try:
                ts_iso = ts.isoformat()
            except Exception:
                ts_iso = str(ts)

            formatted_predictions.append({
                'timestamp': ts_iso,
                'predicted_aqi': float(row['predicted_aqi']),
                'aqi_category': row.get('aqi_category', 'Unknown'),
                'aqi_color': row.get('aqi_color', 'gray'),
                'hour_ahead': i + 1
            })

        return jsonify(formatted_predictions)

    except Exception as e:
        print(f"❌ Error getting predictions: {e}")
        return jsonify({'error': str(e)}), 500

def generate_realistic_predictions():
    """Generate realistic predictions based on typical AQI patterns"""
    import datetime
    
    predictions = []
    now = datetime.datetime.now()
    
    # Generate realistic AQI patterns
    for i in range(1, 121):  # 5 days * 24 hours
        timestamp = now + datetime.timedelta(hours=i)
        
        # Create realistic patterns:
        # - Lower AQI at night (midnight to 6 AM)
        # - Higher AQI during rush hours (7-9 AM, 5-7 PM)
        # - Moderate AQI during day
        hour = timestamp.hour
        
        if 0 <= hour <= 6:  # Night time - lower AQI
            base_aqi = 30 + (hour * 2)
        elif 7 <= hour <= 9:  # Morning rush hour
            base_aqi = 70 + (hour - 7) * 10
        elif 17 <= hour <= 19:  # Evening rush hour
            base_aqi = 80 + (hour - 17) * 8
        else:  # Day time
            base_aqi = 50 + (hour % 12) * 3
        
        # Add some realistic variation
        variation = (i % 7) * 3  # Weekly pattern
        aqi = max(20, min(180, base_aqi + variation))
        
        # Determine category and color
        if aqi <= 50:
            category = "Good"
            color = "#00e400"
        elif aqi <= 100:
            category = "Moderate"
            color = "#ffff00"
        elif aqi <= 150:
            category = "Unhealthy for Sensitive Groups"
            color = "#ff7e00"
        elif aqi <= 200:
            category = "Unhealthy"
            color = "#ff0000"
        elif aqi <= 300:
            category = "Very Unhealthy"
            color = "#8f3f97"
        else:
            category = "Hazardous"
            color = "#7e0023"
        
        predictions.append({
            'timestamp': timestamp.isoformat(),
            'predicted_aqi': int(aqi),
            'aqi_category': category,
            'aqi_color': color,
            'hour_ahead': i
        })
    
    return predictions

if __name__ == '__main__':
    print("🚀 Starting AQI Prediction API Server...")
    print("📡 API will be available at: http://localhost:5001")
    print("🌐 React frontend should be at: http://localhost:3000")
    print("📊 Using REAL data from OpenWeather API and ML pipeline")
    
    app.run(host='0.0.0.0', port=5001, debug=True) 