"""
AQI Calculator module for computing numerical AQI values.

This module implements the US EPA Air Quality Index calculation formula
to convert pollutant concentrations into numerical AQI values (0-500).
The calculation follows the EPA's breakpoint methodology for each
pollutant and returns the highest sub-index as the overall AQI.
"""

from __future__ import annotations

import numpy as np
from typing import Dict, List, Optional, Tuple, Union

# US EPA AQI Breakpoints
# Format: (low_breakpoint, high_breakpoint, low_aqi, high_aqi)
AQI_BREAKPOINTS = {
    "pm2_5": [
        (0.0, 12.0, 0, 50),
        (12.1, 35.4, 51, 100),
        (35.5, 55.4, 101, 150),
        (55.5, 150.4, 151, 200),
        (150.5, 250.4, 201, 300),
        (250.5, 350.4, 301, 400),
        (350.5, 500.4, 401, 500),
    ],
    "pm10": [
        (0, 54, 0, 50),
        (55, 154, 51, 100),
        (155, 254, 101, 150),
        (255, 354, 151, 200),
        (355, 424, 201, 300),
        (425, 504, 301, 400),
        (505, 604, 401, 500),
    ],
    "o3": [
        (0, 54, 0, 50),
        (55, 70, 51, 100),
        (71, 85, 101, 150),
        (86, 105, 151, 200),
        (106, 200, 201, 300),
    ],
    "no2": [
        (0, 53, 0, 50),
        (54, 100, 51, 100),
        (101, 360, 101, 150),
        (361, 649, 151, 200),
        (650, 1249, 201, 300),
        (1250, 1649, 301, 400),
        (1650, 2049, 401, 500),
    ],
    "co": [
        (0, 4.4, 0, 50),
        (4.5, 9.4, 51, 100),
        (9.5, 12.4, 101, 150),
        (12.5, 15.4, 151, 200),
        (15.5, 30.4, 201, 300),
        (30.5, 40.4, 301, 400),
        (40.5, 50.4, 401, 500),
    ],
    "so2": [
        (0, 35, 0, 50),
        (36, 75, 51, 100),
        (76, 185, 101, 150),
        (186, 304, 151, 200),
        (305, 604, 201, 300),
        (605, 804, 301, 400),
        (805, 1004, 401, 500),
    ],
}

# AQI categories and colors
AQI_CATEGORIES = {
    (0, 50): {"category": "Good", "color": "green", "health_impact": "Air quality is considered satisfactory"},
    (51, 100): {"category": "Moderate", "color": "yellow", "health_impact": "Some concern for sensitive groups"},
    (101, 150): {"category": "Unhealthy for Sensitive Groups", "color": "orange", "health_impact": "May cause health effects in sensitive groups"},
    (151, 200): {"category": "Unhealthy", "color": "red", "health_impact": "May cause health effects in everyone"},
    (201, 300): {"category": "Very Unhealthy", "color": "purple", "health_impact": "May cause serious health effects"},
    (301, 500): {"category": "Hazardous", "color": "maroon", "health_impact": "May cause serious health effects"},
}


def calculate_sub_index(concentration: float, pollutant: str) -> Optional[float]:
    """
    Calculate the AQI sub-index for a single pollutant.
    
    Parameters
    ----------
    concentration : float
        Pollutant concentration in appropriate units.
    pollutant : str
        Pollutant name (pm2_5, pm10, o3, no2, co, so2).
        
    Returns
    -------
    float or None
        AQI sub-index value, or None if concentration is out of range.
    """
    if pollutant not in AQI_BREAKPOINTS:
        return None
    
    breakpoints = AQI_BREAKPOINTS[pollutant]
    
    for bp_low, bp_high, aqi_low, aqi_high in breakpoints:
        if bp_low <= concentration <= bp_high:
            # Linear interpolation formula
            aqi = ((aqi_high - aqi_low) / (bp_high - bp_low)) * (concentration - bp_low) + aqi_low
            return round(aqi)
    
    return None


def calculate_aqi(pollutants: Dict[str, float]) -> Dict[str, Union[float, str, Dict]]:
    """
    Calculate the overall AQI from pollutant concentrations.
    
    Parameters
    ----------
    pollutants : dict
        Dictionary of pollutant concentrations with keys:
        - pm2_5: PM2.5 concentration (μg/m³)
        - pm10: PM10 concentration (μg/m³) 
        - o3: Ozone concentration (ppb)
        - no2: Nitrogen dioxide concentration (ppb)
        - co: Carbon monoxide concentration (ppm)
        - so2: Sulfur dioxide concentration (ppb)
        
    Returns
    -------
    dict
        Dictionary containing:
        - aqi: Overall AQI value (0-500)
        - category: AQI category name
        - color: Category color
        - health_impact: Health impact description
        - sub_indices: Dictionary of individual pollutant sub-indices
        - dominant_pollutant: Pollutant with highest sub-index
    """
    sub_indices = {}
    
    # Calculate sub-indices for each pollutant
    for pollutant, concentration in pollutants.items():
        if concentration is not None and not np.isnan(concentration):
            sub_index = calculate_sub_index(concentration, pollutant)
            if sub_index is not None:
                sub_indices[pollutant] = sub_index
    
    if not sub_indices:
        return {
            "aqi": None,
            "category": "Unknown",
            "color": "gray",
            "health_impact": "Insufficient data",
            "sub_indices": {},
            "dominant_pollutant": None
        }
    
    # Find the highest sub-index (overall AQI)
    overall_aqi = max(sub_indices.values())
    dominant_pollutant = max(sub_indices, key=sub_indices.get)
    
    # Determine category
    category_info = None
    for (low, high), info in AQI_CATEGORIES.items():
        if low <= overall_aqi <= high:
            category_info = info
            break
    
    if category_info is None:
        category_info = AQI_CATEGORIES[(301, 500)]  # Default to hazardous
    
    return {
        "aqi": overall_aqi,
        "category": category_info["category"],
        "color": category_info["color"],
        "health_impact": category_info["health_impact"],
        "sub_indices": sub_indices,
        "dominant_pollutant": dominant_pollutant
    }


def calculate_aqi_from_api_data(api_data: Dict[str, float]) -> Dict[str, Union[float, str, Dict]]:
    """
    Calculate AQI from OpenWeatherMap API data format.
    
    Parameters
    ----------
    api_data : dict
        Dictionary from OpenWeatherMap API with pollutant concentrations.
        Expected keys: pm2_5, pm10, o3, no2, co, so2, nh3
        
    Returns
    -------
    dict
        AQI calculation result
    """
    # Convert API data to our format
    pollutants = {
        "pm2_5": api_data.get("pm2_5"),
        "pm10": api_data.get("pm10"),
        "o3": api_data.get("o3"),
        "no2": api_data.get("no2"),
        "co": api_data.get("co"),
        "so2": api_data.get("so2"),
    }
    
    return calculate_aqi(pollutants)


def get_aqi_category(aqi_value: float) -> Dict[str, str]:
    """
    Get AQI category information for a given AQI value.
    
    Parameters
    ----------
    aqi_value : float
        AQI value (0-500)
        
    Returns
    -------
    dict
        Category information
    """
    for (low, high), info in AQI_CATEGORIES.items():
        if low <= aqi_value <= high:
            return info
    return AQI_CATEGORIES[(301, 500)]  # Default to hazardous 