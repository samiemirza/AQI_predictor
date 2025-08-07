#!/usr/bin/env python3
"""
Terminal-based AQI prediction script.

This script runs the prediction pipeline and displays results directly in the terminal
without launching the Streamlit dashboard.
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.pipeline import run_feature_pipeline, run_training_pipeline, run_inference_pipeline
from src.config import get_api_key

def main():
    """Run prediction pipeline and display results in terminal."""
    print("🚀 AQI Prediction System - Terminal Mode")
    print("=" * 50)
    
    # Check API key
    api_key = get_api_key()
    if not api_key:
        print("❌ OPENWEATHER_API_KEY not found in environment or .env file")
        return
    
    print("✅ API key configured")
    
    # Get location coordinates
    print("\n📍 Enter your location coordinates:")
    try:
        lat = float(input("Latitude (e.g., 24.8607): ").strip())
        lon = float(input("Longitude (e.g., 67.0011): ").strip())
    except ValueError:
        print("❌ Invalid coordinates. Using default (Karachi, Pakistan)")
        lat, lon = 24.8607, 67.0011
    
    print(f"\n🔄 Collecting data for location ({lat}, {lon})...")
    
    # Run feature pipeline
    try:
        df_features = run_feature_pipeline(lat=lat, lon=lon, days_back=5)
        if df_features.empty:
            print("❌ No data collected. Check your API key and network connection.")
            return
        print(f"✅ Collected {len(df_features)} data points")
    except Exception as e:
        print(f"❌ Error collecting data: {e}")
        return
    
    # Train models if needed
    print("\n🔄 Training models...")
    try:
        result = run_training_pipeline()
        if result:
            print(f"✅ Best model: {result.name} with RMSE={result.metrics['rmse']:.3f}")
        else:
            print("❌ Training failed. Check if you have sufficient data.")
            return
    except Exception as e:
        print(f"❌ Error training models: {e}")
        return
    
    # Generate predictions
    print(f"\n🔄 Generating predictions for location ({lat}, {lon})...")
    try:
        pred_df = run_inference_pipeline(lat=lat, lon=lon)
        if pred_df is None or pred_df.empty:
            print("❌ Prediction failed. Ensure the model and data are available.")
            return
        
        # Display predictions
        print("\n📊 AQI Predictions for Next 5 Days:")
        print("=" * 60)
        print(f"{'Timestamp':<20} {'Predicted AQI':<15} {'Category':<15} {'Color':<10}")
        print("-" * 60)
        
        for _, row in pred_df.iterrows():
            timestamp = row['timestamp'].strftime('%Y-%m-%d %H:%M')
            aqi = f"{row['predicted_aqi']:.1f}"
            category = row.get('aqi_category', 'Unknown')
            color = row.get('aqi_color', 'gray')
            
            print(f"{timestamp:<20} {aqi:<15} {category:<15} {color:<10}")
        
        print("-" * 60)
        
        # Summary statistics
        avg_aqi = pred_df['predicted_aqi'].mean()
        max_aqi = pred_df['predicted_aqi'].max()
        min_aqi = pred_df['predicted_aqi'].min()
        
        print(f"\n📈 Summary:")
        print(f"   Average AQI: {avg_aqi:.1f}")
        print(f"   Maximum AQI: {max_aqi:.1f}")
        print(f"   Minimum AQI: {min_aqi:.1f}")
        
        # Health alerts
        print(f"\n⚠️  Health Alerts:")
        hazardous = pred_df[pred_df['predicted_aqi'] > 150]
        if not hazardous.empty:
            print(f"   ⚠️  {len(hazardous)} readings exceed hazardous threshold (AQI > 150)")
            for _, row in hazardous.iterrows():
                timestamp = row['timestamp'].strftime('%Y-%m-%d %H:%M')
                print(f"      - {timestamp}: AQI {row['predicted_aqi']:.1f} ({row.get('aqi_category', 'Unknown')})")
        else:
            print("   ✅ No hazardous AQI levels predicted")
        
        print(f"\n🎉 Prediction complete! Check your browser at http://localhost:8501 for the interactive dashboard.")
        
    except Exception as e:
        print(f"❌ Error generating predictions: {e}")

if __name__ == "__main__":
    main() 