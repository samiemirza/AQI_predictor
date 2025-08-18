# Use official Python image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy project files (copy entire repo so it works whether code is nested or at root)
COPY . /app
COPY requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Streamlit port
EXPOSE 8501

# Set environment variable for Python buffering
ENV PYTHONUNBUFFERED=1

# Default command: run the Streamlit dashboard
CMD ["streamlit", "run", "src/dashboard.py", "--server.port", "8501", "--server.address", "0.0.0.0"]