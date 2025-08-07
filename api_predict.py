#!/usr/bin/env python3
"""
Non-interactive AQI prediction script for API use.

This script runs the prediction pipeline with command line arguments
and returns results in JSON format for the API server.
"""

import sys
import json
import argparse
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.pipeline import run_feature_pipeline, run_training_pipeline, run_inference_pipeline
from src.config import get_api_key

def main():
    """Run prediction pipeline with command line arguments."""
    parser = argparse.ArgumentParser(description='AQI Prediction Pipeline')
    parser.add_argument('--lat', type=float, required=True, help='Latitude')
    parser.add_argument('--lng', type=float, required=True, help='Longitude')
    parser.add_argument('--days-back', type=int, default=5, help='Days of historical data to fetch')
    
    args = parser.parse_args()
    
    # Check API key
    api_key = get_api_key()
    if not api_key:
        print(json.dumps({'error': 'API key not configured'}), file=sys.stderr)
        sys.exit(1)
    
    try:
        # Suppress all output during pipeline execution
        with open(os.devnull, 'w') as devnull:
            # Redirect stdout and stderr to suppress output
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            sys.stdout = devnull
            sys.stderr = devnull
            
            try:
                # Run feature pipeline
                df_features = run_feature_pipeline(lat=args.lat, lon=args.lng, days_back=args.days_back)
                if df_features.empty:
                    sys.stdout = old_stdout
                    sys.stderr = old_stderr
                    print(json.dumps({'error': 'No data collected'}), file=sys.stderr)
                    sys.exit(1)
                
                # Train models if needed
                result = run_training_pipeline()
                if not result:
                    sys.stdout = old_stdout
                    sys.stderr = old_stderr
                    print(json.dumps({'error': 'Training failed'}), file=sys.stderr)
                    sys.exit(1)
                
                # Generate predictions
                pred_df = run_inference_pipeline(lat=args.lat, lon=args.lng)
                if pred_df is None or pred_df.empty:
                    sys.stdout = old_stdout
                    sys.stderr = old_stderr
                    print(json.dumps({'error': 'Prediction failed'}), file=sys.stderr)
                    sys.exit(1)
                    
            finally:
                # Restore stdout and stderr
                sys.stdout = old_stdout
                sys.stderr = old_stderr
        
        # Convert predictions to JSON format
        predictions = []
        for _, row in pred_df.iterrows():
            predictions.append({
                'timestamp': row['timestamp'].isoformat(),
                'predicted_aqi': float(row['predicted_aqi']),
                'aqi_category': row.get('aqi_category', 'Unknown'),
                'aqi_color': row.get('aqi_color', 'gray'),
                'hour_ahead': len(predictions) + 1
            })
        
        # Output JSON result
        result = {
            'success': True,
            'predictions': predictions,
            'summary': {
                'average_aqi': float(pred_df['predicted_aqi'].mean()),
                'max_aqi': float(pred_df['predicted_aqi'].max()),
                'min_aqi': float(pred_df['predicted_aqi'].min()),
                'total_predictions': len(predictions)
            }
        }
        
        print(json.dumps(result))
        
    except Exception as e:
        print(json.dumps({'error': str(e)}), file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main() 