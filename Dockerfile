# Use official Python image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY aqi_project /app/aqi_project
COPY requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Streamlit port
EXPOSE 8501

# Set environment variable for Python buffering
ENV PYTHONUNBUFFERED=1

# Default command: run the Streamlit dashboard
CMD ["streamlit", "run", "aqi_project/src/dashboard.py", "--server.port", "8501", "--server.address", "0.0.0.0"]