#!/usr/bin/env python3
"""
Quick start script for the AQI prediction system.

This script helps users get started by:
1. Checking dependencies
2. Setting up the environment
3. Running initial data collection
4. Training the first model
5. Launching the dashboard
"""

import os
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add src to path at the very beginning
sys.path.insert(0, str(Path(__file__).parent / "src"))

def check_dependencies():
    """Check if required packages are installed."""
    required_packages = [
        'pandas', 'numpy', 'sklearn', 'requests', 
        'streamlit', 'schedule', 'joblib', 'shap'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("Please install requirements: pip install -r requirements.txt")
        return False
    
    print("✅ All required packages are installed")
    return True

def check_api_key():
    """Check if API key is set."""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        print("❌ OPENWEATHER_API_KEY environment variable not set")
        print("Please set your OpenWeatherMap API key:")
        print("export OPENWEATHER_API_KEY=your_api_key_here")
        print("Or add it to your .env file")
        return False
    
    print("✅ API key is configured")
    return True

def setup_directories():
    """Create necessary directories."""
    directories = ["data", "models", "notebooks"]
    for dir_name in directories:
        Path(dir_name).mkdir(exist_ok=True)
    print("✅ Directories created")

def run_initial_pipeline(lat, lon):
    """Run the initial feature pipeline."""
    print(f"🔄 Collecting data for location ({lat}, {lon})...")
    
    try:
        from src.pipeline import run_feature_pipeline
        df = run_feature_pipeline(lat=lat, lon=lon, days_back=5)
        if not df.empty:
            print(f"✅ Collected {len(df)} data points")
            return True
        else:
            print("❌ No data collected. Check your API key and network connection.")
            return False
    except Exception as e:
        print(f"❌ Error collecting data: {e}")
        return False

def train_initial_model():
    """Train the initial model."""
    print("🔄 Training models...")
    
    try:
        from src.pipeline import run_training_pipeline
        result = run_training_pipeline()
        if result:
            print(f"✅ Best model: {result.name} with RMSE={result.metrics['rmse']:.3f}")
            return True
        else:
            print("❌ Training failed. Check if you have sufficient data.")
            return False
    except Exception as e:
        print(f"❌ Error training models: {e}")
        return False

def launch_dashboard():
    """Launch the Streamlit dashboard."""
    print("🚀 Launching dashboard...")
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "src/dashboard.py",
            "--server.port", "8501", "--server.address", "0.0.0.0"
        ])
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped")

def main():
    """Main quick start function."""
    print("🚀 AQI Prediction System - Quick Start")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Check API key
    if not check_api_key():
        return
    
    # Setup directories
    setup_directories()
    
    # Get location from user
    print("\n📍 Enter your location coordinates:")
    try:
        lat = float(input("Latitude (e.g., 24.8607): ").strip())
        lon = float(input("Longitude (e.g., 67.0011): ").strip())
    except ValueError:
        print("❌ Invalid coordinates. Using default (Karachi, Pakistan)")
        lat, lon = 24.8607, 67.0011
    
    # Run initial pipeline
    if not run_initial_pipeline(lat, lon):
        return
    
    # Train model
    if not train_initial_model():
        return
    
    # Launch dashboard
    print("\n🎉 Setup complete! Launching dashboard...")
    print("📊 Open your browser to http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop the dashboard")
    
    launch_dashboard()

if __name__ == "__main__":
    main() 