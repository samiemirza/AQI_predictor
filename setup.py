#!/usr/bin/env python3
"""
Setup script for the AQI prediction project.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

requirements = []
_req_path = "requirements.txt"
try:
    with open(_req_path, "r", encoding="utf-8") as fh:
        requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
except FileNotFoundError:
    # Fallback for build environments that do not include requirements.txt in sdist context
    # Keep runtime minimal for packaging
    requirements = [
        "pandas>=1.5.0",
        "numpy>=1.23.0",
        "scikit-learn>=1.3.0",
        "requests>=2.31.0",
        "joblib>=1.2.0",
        "python-dotenv>=1.0.0",
        "pyarrow>=10.0.0",
    ]

setup(
    name="aqi-predictor",
    version="1.0.0",
    author="AQI Prediction Team",
    description="Air Quality Index prediction system using machine learning",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "aqi-predictor=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.json", "*.pkl", "*.parquet"],
    },
) 