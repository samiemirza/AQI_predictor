#!/usr/bin/env python3
"""
Main entry point for the AQI prediction system.

This script provides a convenient interface to run the various
pipeline stages and access the dashboard.
"""

import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pipeline import run_feature_pipeline, run_training_pipeline, run_inference_pipeline
from scheduler import start_scheduler


def main():
    """Main entry point with command-line interface."""
    parser = argparse.ArgumentParser(
        description="AQI Prediction System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate features for a location
  python main.py features --lat 24.86 --lon 67.00

  # Train models
  python main.py train

  # Generate predictions
  python main.py predict --lat 24.86 --lon 67.00

  # Start scheduler
  python main.py schedule --lat 24.86 --lon 67.00

  # Launch dashboard
  python main.py dashboard
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Features command
    features_parser = subparsers.add_parser("features", help="Generate features from raw data")
    features_parser.add_argument("--lat", type=float, required=True, help="Latitude")
    features_parser.add_argument("--lon", type=float, required=True, help="Longitude")
    features_parser.add_argument("--days-back", type=int, default=5, help="Days of historical data")
    
    # Train command
    subparsers.add_parser("train", help="Train models using stored features")
    
    # Predict command
    predict_parser = subparsers.add_parser("predict", help="Generate predictions")
    predict_parser.add_argument("--lat", type=float, required=True, help="Latitude")
    predict_parser.add_argument("--lon", type=float, required=True, help="Longitude")
    
    # Schedule command
    schedule_parser = subparsers.add_parser("schedule", help="Start the scheduler")
    schedule_parser.add_argument("--lat", type=float, required=True, help="Latitude")
    schedule_parser.add_argument("--lon", type=float, required=True, help="Longitude")
    
    # Dashboard command
    subparsers.add_parser("dashboard", help="Launch the Streamlit dashboard")
    
    args = parser.parse_args()
    
    if args.command == "features":
        print(f"Generating features for location ({args.lat}, {args.lon})...")
        df = run_feature_pipeline(lat=args.lat, lon=args.lon, days_back=args.days_back)
        print(f"Generated {len(df)} feature rows.")
        
    elif args.command == "train":
        print("Training models...")
        result = run_training_pipeline()
        if result:
            print(f"Best model: {result.name} with RMSE={result.metrics['rmse']:.3f}")
        else:
            print("Training failed. Check if you have sufficient data.")
            
    elif args.command == "predict":
        print(f"Generating predictions for location ({args.lat}, {args.lon})...")
        df = run_inference_pipeline(lat=args.lat, lon=args.lon)
        if df is not None:
            print("Predictions:")
            print(df.head())
        else:
            print("Prediction failed. Ensure you have trained models.")
            
    elif args.command == "schedule":
        print(f"Starting scheduler for location ({args.lat}, {args.lon})...")
        start_scheduler(lat=args.lat, lon=args.lon)
        
    elif args.command == "dashboard":
        print("Launching Streamlit dashboard...")
        import subprocess
        import sys
        subprocess.run([sys.executable, "-m", "streamlit", "run", "src/dashboard.py"])
        
    else:
        parser.print_help()


if __name__ == "__main__":
    main() 