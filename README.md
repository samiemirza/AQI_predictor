# Air Quality Index (AQI) Prediction System

This repository implements an end‑to‑end system for predicting the Air
Quality Index (AQI) of a given location over the coming days. Inspired
by the problem brief provided in the "Pearls AQI Predictor" document,
the solution uses a 100 % Python stack to fetch raw pollution data,
engineer features, train multiple models, register the best model
automatically and serve predictions via an interactive dashboard.

## Features

* **Data ingestion:** Downloads current, historical and forecasted air
  pollution data from the [OpenWeatherMap Air Pollution API](https://openweathermap.org/api/air-pollution).
* **AQI calculation:** Implements US EPA AQI calculation formula to convert
  pollutant concentrations into numerical AQI values (0-500) with proper
  categories and health impact assessments.
* **Feature engineering:** Extracts calendar features, computes change
  rates, ratios and rolling statistics to enrich the raw sensor data.
* **Feature store:** Stores engineered features in a Parquet file on
  disk, deduplicating by timestamp for incremental updates.
* **Model training:** Fits several models (Random Forest, Ridge
  Regression, MLP regressors and a Keras neural network) and selects
  the one with the lowest RMSE. Evaluation metrics (RMSE, MAE and
  R²) are computed on a hold‑out set.
* **Model registry:** Registers trained models with version numbers and
  metrics. Supports both scikit‑learn and Keras models.
* **Scheduling:** Includes a simple scheduler that runs the feature
  extraction every hour and re‑trains models daily. You can replace
  this with a more robust solution (Airflow, GitHub Actions, etc.).
* **Dashboard:** Offers a Streamlit dashboard to display current
  conditions, forecasted AQI and SHAP‑based feature importance. Users
  can set hazardous thresholds and receive alerts when forecasts
  exceed them.
* **Containerisation:** A `Dockerfile` is provided to run the entire
  application in a consistent environment.

## Project structure

```
aqi_project/
├── data/                # Parquet file containing engineered features
├── models/              # Saved models and registry metadata
├── notebooks/           # Notebooks for EDA and experimentation
├── src/
│   ├── config.py        # Central configuration constants
│   ├── data_fetcher.py  # API wrappers for pollution data
│   ├── feature_engineering.py
│   ├── feature_store.py
│   ├── model_registry.py
│   ├── pipeline.py      # Orchestration functions
│   ├── scheduler.py     # Hourly/daily scheduler using schedule
│   ├── training.py
│   └── dashboard.py     # Streamlit app
├── requirements.txt     # Python dependencies
├── Dockerfile           # Container definition
├── README.md            # This file
└── report.md            # Project report (to be completed)
```

## Getting started

### Quick Start (Recommended)

For the fastest setup, use our quick start script:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your API key
export OPENWEATHER_API_KEY=your_api_key_here

# 3. Run quick start
python quick_start.py
```

This will guide you through the entire setup process and launch the dashboard automatically.

### Test AQI Calculation

To see how the numerical AQI calculation works:

```bash
# Test the AQI calculation with sample data
python3 test_aqi_calculation.py

# See a comprehensive demo with real-world examples
python3 demo_numerical_aqi.py
```

### Manual Setup

#### 1. Obtain an API key

Sign up for a free [OpenWeatherMap API](https://openweathermap.org/api) account and
obtain an **API key**. This key is required to access the air
pollution endpoints. The key can be supplied in two ways:

1. Set the environment variable `OPENWEATHER_API_KEY` before running
   any scripts.
2. Provide it interactively within the Streamlit dashboard sidebar.

#### 2. Install dependencies

Create a virtual environment and install the requirements:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

#### 3. Generate initial features and train models

**Option A: Using the main script (recommended)**
```bash
# Generate features
python main.py features --lat 24.86 --lon 67.00

# Train models
python main.py train

# Generate predictions
python main.py predict --lat 24.86 --lon 67.00
```

**Option B: Using the original pipeline commands**
```bash
# Generate features
python -m src.pipeline run_feature_pipeline --lat <LAT> --lon <LON>

# Train models
python -m src.pipeline run_training_pipeline
```

**Option C: Using the scheduler**
```bash
python main.py schedule --lat <LAT> --lon <LON>
```

#### 4. Launch the dashboard

```bash
python main.py dashboard
```

Or directly with Streamlit:
```bash
streamlit run src/dashboard.py
```

Navigate to the displayed URL in your browser. Use the sidebar to
enter your latitude/longitude, API key and forecast hazard threshold.

## Docker usage

Build the Docker image:

```bash
docker build -t aqi-predictor .
```

Run the container, exposing the Streamlit port (default 8501):

```bash
docker run -e OPENWEATHER_API_KEY=<your_key> -p 8501:8501 aqi-predictor
```

## Limitations and future work

* The free OpenWeatherMap Air Pollution API only provides five days of
  historical data and five days of forecasts. Extending the lookback
  period may require batching or a paid plan.
* The feature store is implemented as a single Parquet file, which is
  sufficient for demonstration but lacks the scalability and
  concurrency guarantees of managed feature stores (Hopsworks,
  Vertex AI, etc.).
* Advanced models (LSTM, Prophet, etc.) could further improve
  forecasting performance. Integrating probabilistic forecasts would
  offer uncertainty estimates.
* The CI/CD pipeline provided via `schedule` is basic. Deploying on
  Airflow, Prefect or GitHub Actions would enable more robust,
  cloud‑native automation.

## Reporting

A detailed report describing the data exploration, model comparisons
and insights should be provided in `report.md`. Use this file to
document the EDA results, visualisations, hyperparameter searches and
interpretations of the model outputs.# AQI_predictor
