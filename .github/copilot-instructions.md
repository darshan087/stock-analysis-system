# Stock Analysis ML Project - Copilot Instructions

This is a Flask ML PySpark project for stock analysis and prediction.

## Project Overview
- **Type**: Flask ML Application with PySpark
- **Framework**: Flask, PySpark, scikit-learn
- **Language**: Python 3.8+
- **Structure**: Modular architecture with separate concerns (models, utils, routes, config)

## Key Components
- Flask REST API with health check, stats, and prediction endpoints
- PySpark for distributed data processing
- ML pipeline with feature scaling and linear regression
- Comprehensive configuration management
- Unit tests with pytest

## Quick Start
1. Create virtual environment: `python -m venv venv && venv\Scripts\activate`
2. Install dependencies: `pip install -r requirements.txt`
3. Configure environment: `copy .env.example .env`
4. Run development server: `python src/app/app.py`
5. Run tests: `pytest tests/`

## Project Layout
- `src/app/` - Flask application and routes
- `src/models/` - ML models and prediction logic
- `src/utils/` - Utility functions (PySpark, data processing)
- `src/config/` - Configuration settings
- `tests/` - Unit tests
- `notebooks/` - Jupyter notebooks for exploration
- `data/` - Data storage directory

## Common Tasks
- **Add new model**: Create class in `src/models/`, add endpoint in `src/app/routes.py`
- **Add new route**: Update `src/app/routes.py` and add test in `tests/test_app.py`
- **Process data**: Use utilities in `src/utils/spark_utils.py` and `src/utils/data_processing.py`

## Configuration
- Development/production configuration in `src/config/settings.py`
- Environment variables in `.env` file
- Flask app factory pattern in `src/app/app.py`

See README.md for full documentation.
