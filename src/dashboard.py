"""
Enhanced Streamlit dashboard for AQI prediction and monitoring.

This dashboard provides a modern interface with:
- Home page: World map for city selection and prediction display
- About page: Project details and information
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
import json

# Add the parent directory to the path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from streamlit_folium import folium_static
import folium
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable

# Import local modules
try:
    from . import config
    from .data_fetcher import fetch_current_air_pollution, fetch_forecast_air_pollution
    from .feature_engineering import compute_features
    from .pipeline import run_inference_pipeline, run_feature_pipeline, run_training_pipeline
    from .model_registry import ModelRegistry
except ImportError:
    # Fallback for direct script execution
    import config
    from data_fetcher import fetch_current_air_pollution, fetch_forecast_air_pollution
    from feature_engineering import compute_features
    from pipeline import run_inference_pipeline, run_feature_pipeline, run_training_pipeline
    from model_registry import ModelRegistry

# Page configuration
st.set_page_config(
    page_title="AQI Predictor",
    page_icon="🌬️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'selected_city' not in st.session_state:
    st.session_state.selected_city = None
if 'selected_coords' not in st.session_state:
    st.session_state.selected_coords = None
if 'predictions' not in st.session_state:
    st.session_state.predictions = None

def load_latest_model() -> Tuple[Optional[object], Optional[str]]:
    """Load the latest available model from the registry."""
    registry = ModelRegistry()
    for name in ["random_forest", "ridge_regression", "mlp_regressor", "keras_mlp"]:
        try:
            entry = registry.get_latest_model(name)
            if entry is not None:
                model, metadata = entry
                return model, name
        except Exception:
            continue
    return None, None

def get_city_coordinates(city_name: str) -> Optional[Tuple[float, float]]:
    """Get coordinates for a city name using geocoding."""
    try:
        geolocator = Nominatim(user_agent="aqi_predictor")
        location = geolocator.geocode(city_name)
        if location:
            return (location.latitude, location.longitude)
    except (GeocoderTimedOut, GeocoderUnavailable):
        st.error("Geocoding service unavailable. Please try again.")
    return None

def create_world_map(selected_coords: Optional[Tuple[float, float]] = None) -> folium.Map:
    """Create a world map with city selection functionality."""
    # Create a map centered on the world
    m = folium.Map(
        location=[20, 0],
        zoom_start=2,
        tiles='OpenStreetMap'
    )
    
    # Add some major cities as clickable markers
    major_cities = {
        "New York": (40.7128, -74.0060),
        "London": (51.5074, -0.1278),
        "Tokyo": (35.6762, 139.6503),
        "Mumbai": (19.0760, 72.8777),
        "Karachi": (24.8607, 67.0011),
        "Beijing": (39.9042, 116.4074),
        "Sydney": (-33.8688, 151.2093),
        "Cairo": (30.0444, 31.2357),
        "São Paulo": (-23.5505, -46.6333),
        "Moscow": (55.7558, 37.6176)
    }
    
    for city, coords in major_cities.items():
        folium.Marker(
            coords,
            popup=f"<b>{city}</b><br>Click to select",
            tooltip=city,
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(m)
    
    # Add selected location marker if available
    if selected_coords:
        folium.Marker(
            selected_coords,
            popup="<b>Selected Location</b>",
            tooltip="Selected Location",
            icon=folium.Icon(color='red', icon='star')
        ).add_to(m)
    
    return m

def display_predictions(pred_df: pd.DataFrame) -> None:
    """Display AQI predictions in a nice format."""
    if pred_df is None or pred_df.empty:
        st.warning("No predictions available. Please run the prediction pipeline first.")
        return
    
    # Create two columns for layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 AQI Predictions for Next 5 Days")
        
        # Create a line chart of predictions
        fig = px.line(
            pred_df, 
            x='timestamp', 
            y='predicted_aqi',
            title='AQI Forecast',
            labels={'predicted_aqi': 'Predicted AQI', 'timestamp': 'Date'},
            color_discrete_sequence=['#1f77b4']
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Display predictions table
        st.subheader("📋 Detailed Predictions")
        display_df = pred_df.copy()
        display_df['timestamp'] = display_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M')
        display_df['predicted_aqi'] = display_df['predicted_aqi'].round(1)
        st.dataframe(display_df[['timestamp', 'predicted_aqi', 'aqi_category']], use_container_width=True)
    
    with col2:
        st.subheader("📈 Summary Statistics")
        
        # Calculate statistics
        avg_aqi = pred_df['predicted_aqi'].mean()
        max_aqi = pred_df['predicted_aqi'].max()
        min_aqi = pred_df['predicted_aqi'].min()
        
        # Display metrics
        st.metric("Average AQI", f"{avg_aqi:.1f}")
        st.metric("Maximum AQI", f"{max_aqi:.1f}")
        st.metric("Minimum AQI", f"{min_aqi:.1f}")
        
        # Health alerts
        st.subheader("⚠️ Health Alerts")
        hazardous = pred_df[pred_df['predicted_aqi'] > 150]
        if not hazardous.empty:
            st.error(f"🚨 {len(hazardous)} hazardous readings predicted")
            for _, row in hazardous.iterrows():
                timestamp = row['timestamp'].strftime('%Y-%m-%d %H:%M')
                st.write(f"• {timestamp}: AQI {row['predicted_aqi']:.1f}")
        else:
            st.success("✅ No hazardous levels predicted")

def home_page():
    """Home page with world map and predictions."""
    st.title("🌬️ AQI Prediction Dashboard")
    st.markdown("Select a location on the map or search for a city to get air quality predictions.")
    
    # Sidebar configuration
    st.sidebar.header("🔧 Configuration")
    
    # API Key input
    api_key_input = st.sidebar.text_input(
        "OpenWeatherMap API Key",
        value=os.getenv("OPENWEATHER_API_KEY", ""),
        help="API key for fetching air pollution data",
        type="password",
    )
    if api_key_input:
        os.environ["OPENWEATHER_API_KEY"] = api_key_input
    
    # City search
    st.sidebar.subheader("🏙️ City Search")
    city_search = st.sidebar.text_input("Search for a city:", placeholder="e.g., New York, London, Tokyo")
    
    if st.sidebar.button("🔍 Search City"):
        if city_search:
            coords = get_city_coordinates(city_search)
            if coords:
                st.session_state.selected_city = city_search
                st.session_state.selected_coords = coords
                st.success(f"📍 Found {city_search} at coordinates: {coords[0]:.4f}, {coords[1]:.4f}")
            else:
                st.error(f"❌ Could not find coordinates for {city_search}")
    
    # Manual coordinates input
    st.sidebar.subheader("📍 Manual Coordinates")
    lat = st.sidebar.number_input("Latitude", value=24.8607, format="%.4f")
    lon = st.sidebar.number_input("Longitude", value=67.0011, format="%.4f")
    
    if st.sidebar.button("📍 Use These Coordinates"):
        st.session_state.selected_coords = (lat, lon)
        st.session_state.selected_city = f"Custom Location ({lat:.4f}, {lon:.4f})"
    
    # Display the world map
    st.subheader("🗺️ World Map - Click on a city or search above")
    map_obj = create_world_map(st.session_state.selected_coords)
    folium_static(map_obj, width=800, height=500)
    
    # Prediction section
    if st.session_state.selected_coords:
        st.subheader(f"🎯 Predictions for {st.session_state.selected_city or 'Selected Location'}")
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Update Data"):
                with st.spinner("Collecting latest data..."):
                    try:
                        df_features = run_feature_pipeline(
                            lat=st.session_state.selected_coords[0], 
                            lon=st.session_state.selected_coords[1], 
                            days_back=5
                        )
                        if not df_features.empty:
                            st.success(f"✅ Collected {len(df_features)} data points")
                        else:
                            st.error("❌ No data collected")
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
        
        with col2:
            if st.button("🤖 Train Models"):
                with st.spinner("Training models..."):
                    try:
                        result = run_training_pipeline()
                        if result:
                            st.success(f"✅ Best model: {result.name} (RMSE: {result.metrics['rmse']:.3f})")
                        else:
                            st.error("❌ Training failed")
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
        
        with col3:
            if st.button("🔮 Generate Predictions"):
                with st.spinner("Generating predictions..."):
                    try:
                        pred_df = run_inference_pipeline(
                            lat=st.session_state.selected_coords[0], 
                            lon=st.session_state.selected_coords[1]
                        )
                        if pred_df is not None and not pred_df.empty:
                            st.session_state.predictions = pred_df
                            st.success("✅ Predictions generated!")
                        else:
                            st.error("❌ Prediction failed")
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
        
        # Display current air quality
        st.subheader("🌡️ Current Air Quality")
        try:
            current_df = fetch_current_air_pollution(
                lat=st.session_state.selected_coords[0], 
                lon=st.session_state.selected_coords[1]
            )
            if not current_df.empty and "aqi_numerical" in current_df.columns:
                aqi_value = current_df["aqi_numerical"].iloc[0]
                aqi_category = current_df["aqi_category"].iloc[0]
                
                # Color coding for AQI
                if aqi_value <= 50:
                    color = "green"
                elif aqi_value <= 100:
                    color = "yellow"
                elif aqi_value <= 150:
                    color = "orange"
                elif aqi_value <= 200:
                    color = "red"
                else:
                    color = "purple"
                
                st.metric(
                    label="Current AQI",
                    value=f"{aqi_value:.0f}",
                    delta=f"{aqi_category}",
                    delta_color="normal" if color in ["green", "yellow"] else "inverse"
                )
            else:
                st.warning("⚠️ Current air quality data not available")
        except Exception as e:
            st.error(f"❌ Error fetching current air quality: {e}")
        
        # Display predictions if available
        if st.session_state.predictions is not None:
            display_predictions(st.session_state.predictions)

def about_page():
    """About page with project details."""
    st.title("ℹ️ About AQI Prediction Project")
    
    st.markdown("""
    ## 🌬️ Air Quality Index (AQI) Prediction System
    
    This project uses machine learning to predict air quality index values for locations worldwide.
    It combines real-time air pollution data with advanced forecasting algorithms to provide
    accurate predictions up to 5 days in advance.
    
    ### 🎯 Key Features
    
    - **🌍 Global Coverage**: Predict AQI for any location worldwide
    - **🤖 Machine Learning**: Uses multiple ML models (Random Forest, Neural Networks)
    - **📊 Real-time Data**: Fetches live air pollution data from OpenWeatherMap API
    - **🔮 5-Day Forecast**: Predicts air quality up to 5 days in advance
    - **📈 Interactive Dashboard**: Beautiful visualizations and real-time updates
    - **⚡ Automated Pipeline**: Complete ML pipeline from data collection to predictions
    
    ### 🧠 How It Works
    
    1. **Data Collection**: Fetches historical air pollution data (CO, NO2, PM2.5, PM10, O3, SO2, etc.)
    2. **Feature Engineering**: Creates time-based features, ratios, and rolling statistics
    3. **Model Training**: Trains multiple ML models and selects the best performer
    4. **Prediction**: Uses the trained model to forecast future AQI values
    5. **Visualization**: Displays results with interactive charts and health alerts
    
    ### 📊 Model Performance
    
    - **Current Model**: Random Forest (v6)
    - **RMSE**: 8.26 (Root Mean Square Error)
    - **MAE**: 4.96 (Mean Absolute Error)
    - **R²**: 0.796 (79.6% variance explained)
    
    ### 🛠️ Technical Stack
    
    - **Python**: Core programming language
    - **Streamlit**: Web dashboard framework
    - **Scikit-learn**: Machine learning library
    - **Pandas**: Data manipulation
    - **Plotly**: Interactive visualizations
    - **Folium**: Interactive maps
    - **OpenWeatherMap API**: Air pollution data source
    
    ### 🎓 Data Science Pipeline
    
    This project demonstrates a complete data science workflow:
    
    - **Data Ingestion**: Real-time API integration
    - **Data Processing**: Feature engineering and cleaning
    - **Model Development**: Multiple algorithm comparison
    - **Model Evaluation**: Cross-validation and metrics
    - **Model Deployment**: Production-ready inference pipeline
    - **Monitoring**: Performance tracking and model versioning
    
    ### 🌟 Use Cases
    
    - **Public Health**: Early warning systems for air quality
    - **Urban Planning**: City air quality management
    - **Personal Health**: Planning outdoor activities
    - **Environmental Monitoring**: Regulatory compliance
    - **Research**: Air quality pattern analysis
    
    ### 📝 API Reference
    
    The system uses the OpenWeatherMap Air Pollution API to fetch:
    - Current air pollution data
    - Historical air pollution data (5 days)
    - Forecast air pollution data (5 days)
    
    ### 🔧 Getting Started
    
    1. Set your OpenWeatherMap API key in the sidebar
    2. Select a location on the map or search for a city
    3. Click "Update Data" to collect latest air pollution data
    4. Click "Train Models" to train the prediction models
    5. Click "Generate Predictions" to get 5-day AQI forecasts
    
    ### 📞 Support
    
    For questions or issues, please refer to the project documentation or create an issue in the repository.
    
    ---
    
    **Built with ❤️ for better air quality monitoring and prediction**
    """)

def main():
    """Main dashboard function with navigation."""
    # Navigation
    st.sidebar.title("🌬️ AQI Predictor")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["🏠 Home", "ℹ️ About"]
    )
    
    # Display selected page
    if page == "🏠 Home":
        home_page()
    elif page == "ℹ️ About":
        about_page()

if __name__ == "__main__":
    main()