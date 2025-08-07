# AQI Prediction Project Report

> **Note:** This report serves as a template for documenting your work. Fill in
> the sections with findings from your exploratory data analysis,
> modelling experiments and final insights. Where appropriate, include
> charts and tables generated from your notebooks. Keep prose outside
> of tables; reserve tables for succinct information only. Use proper
> Markdown headings (`#`, `##`, `###`) to structure the narrative.

## Introduction

Describe the motivation behind predicting the Air Quality Index (AQI)
for your city. Explain why forecasting AQI is important for public
health, urban planning and environmental awareness. Briefly summarise
the goal of this project: to build a scalable, serverless pipeline that
fetches real‑time pollution data, learns patterns from historical
measurements and delivers accurate forecasts through an interactive
dashboard.

## Data collection

* **Source:** OpenWeatherMap Air Pollution API.
* **Variables:** Date/time, main AQI category, pollutant concentrations
  (CO, NO, NO₂, O₃, SO₂, PM₂.₅, PM₁₀, NH₃).
* **Temporal resolution:** Hourly.
* **Historical lookback:** Up to five days (free tier limitation).
* **Forecast horizon:** Five days.

Outline how you obtained the data using the API wrappers in
`data_fetcher.py`. Mention any challenges (rate limits, missing
values) and how you addressed them.

## Exploratory data analysis (EDA)

Summarise your EDA findings. Consider the following questions:

* How do pollutant levels and the AQI vary throughout the day, week
  and month? Are there discernible patterns or cycles?
* What correlations exist between the different pollutant components
  and the AQI? Identify which pollutants are most predictive of the
  index.
* Are there any outliers or anomalies in the data? How did you
  handle them?

Present key plots (time series plots, correlation heatmaps, box plots)
and discuss the insights gleaned. Include at least one figure that
shows the distribution of AQI values over time.

## Feature engineering

Describe the engineered features used in your models. Explain why
time‑based features (hour, day of week, month, etc.) and derived
features (change rates, ratios, rolling means/stdevs) are valuable for
capturing temporal dynamics and non‑linear relationships.

Provide a table summarising the features:

| Feature | Description |
|--------|-------------|
| `hour` | Hour of the day (0–23). |
| `dayofweek` | Day of the week (0=Monday, …). |
| `month` | Month of the year (1–12). |
| `is_weekend` | 1 if the day is Saturday/Sunday, 0 otherwise. |
| `aqi_change` | First difference of `main_aqi`. |
| `pm_ratio` | Ratio of PM₂.₅ to PM₁₀. |
| `aqi_roll_mean_k` | Rolling mean of `main_aqi` over *k* hours. |
| `aqi_roll_std_k` | Rolling standard deviation of `main_aqi` over *k* hours. |

## Modelling

Detail the models you trained and their performance metrics. Discuss
the training–validation split, hyperparameters and any feature
selection or preprocessing steps. Compare the following models:

* Random Forest Regressor
* Ridge Regression
* MLPRegressor (scikit‑learn)
* Keras feed‑forward neural network

Present a table of evaluation metrics (RMSE, MAE and R²) for each
model on the hold‑out set. Identify the best model based on RMSE and
justify why it was selected. If any model performed poorly, speculate
on the reasons.

## Feature importance

Explain how you used SHAP to interpret model predictions. Include a
bar chart of average absolute SHAP values or a summary plot to show
which features most strongly influence the forecasted AQI. Discuss
whether these findings align with your domain knowledge from the EDA
section.

## Pipeline and deployment

Describe the end‑to‑end pipeline implemented in `pipeline.py` and
`scheduler.py`. Explain how raw data flows through feature
engineering, model training, registration and inference. Mention the
role of the feature store and model registry.

Discuss the CI/CD considerations and how you could deploy this
pipeline using Airflow, Prefect or GitHub Actions. Outline how the
provided Dockerfile encapsulates the dependencies for reproducibility
and ease of deployment.

## Results and discussion

Summarise the main achievements and limitations of your project. Did
the model achieve satisfactory accuracy? Are there specific periods
when the predictions are more reliable? Provide context on how these
forecasts can be used by citizens, policymakers or public health
agencies.

## Conclusion and future work

Reflect on what was accomplished and propose avenues for future
improvements, such as:

* Collecting longer historical series or additional explanatory
  variables (wind speed, temperature, traffic data).
* Exploring time‑series specific models (ARIMA, Prophet, LSTM) or
  probabilistic forecasting.
* Deploying the pipeline on a cloud serverless platform (AWS Lambda,
  Google Cloud Functions) and integrating push notifications for
  hazardous events.

End with any key takeaways on working with environmental data and
deploying machine‑learning solutions in a production setting.