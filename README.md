# Stock Prediction & Analysis System

[![GitHub](https://img.shields.io/badge/GitHub-darshan087%2Fstock--analysis--system-blue)](https://github.com/darshan087/stock-analysis-system)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-green)](https://flask.palletsprojects.com/)
[![PySpark](https://img.shields.io/badge/PySpark-3.5.0-orange)](https://spark.apache.org/docs/latest/api/python/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A comprehensive Flask-based machine learning application leveraging PySpark for scalable stock price prediction and market analysis. This system provides distributed data processing, advanced ML pipelines, and RESTful APIs for real-time stock predictions.

## 🎯 Features

- **Real-time Stock Price Prediction** - ML-powered predictions using historical data
- **Distributed Data Processing** - PySpark integration for handling large datasets
- **ML Pipeline Architecture** - Feature scaling, normalization, and regression models
- **RESTful API** - Easy-to-use endpoints for integration
- **Configuration Management** - Environment-based settings (dev/prod/test)
- **Comprehensive Testing** - Unit tests with pytest and coverage reporting
- **Production Ready** - Gunicorn WSGI server support
- **Modular Design** - Clean separation of concerns for easy maintenance

## 📋 Requirements

All dependencies are specified in `requirements.txt`:

```
Flask==3.0.0
Flask-RESTful==0.3.10
pyspark==3.5.0
pandas==2.1.3
numpy==1.26.2
scikit-learn==1.3.2
python-dotenv==1.0.0
gunicorn==21.2.0
pytest==7.4.3
pytest-cov==4.1.0
```

### System Requirements
- **Python:** 3.8 or higher
- **Java:** Required for PySpark (JDK 8 or 11)
- **Memory:** Minimum 4GB RAM (8GB+ recommended)
- **OS:** Windows, macOS, or Linux

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/darshan087/stock-analysis-system.git
cd stock-analysis-system
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```

Edit `.env` and set your configuration:
```env
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
```

### 5. Run the Application
```bash
# Development Server (with auto-reload)
python src/app/app.py

# Or using Flask CLI
python -m flask --app src.app.app run --debug
```

The API will be available at `http://localhost:5000`

## 📁 Project Structure

```
stock-analysis-system/
│
├── src/                              # Source code
│   ├── app/
│   │   ├── __init__.py
│   │   ├── app.py                   # Flask application factory
│   │   └── routes.py                # API endpoints and blueprints
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── predictor.py             # ML prediction models
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── spark_utils.py           # PySpark session management
│   │   └── data_processing.py       # Data utilities and transformations
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py              # Configuration management
│   │
│   └── __init__.py
│
├── tests/
│   ├── __init__.py
│   └── test_app.py                  # Unit tests
│
├── notebooks/                        # Jupyter notebooks for exploration
│
├── data/                             # Data directory
│   ├── raw/                         # Raw stock data
│   └── processed/                   # Processed data
│
├── .github/
│   └── copilot-instructions.md      # Development guidelines
│
├── .env.example                      # Environment variables template
├── .gitignore                        # Git ignore rules
├── requirements.txt                  # Python dependencies
├── README.md                         # This file
└── LICENSE                           # MIT License
```

## 🔌 API Endpoints

### Health Check
Get the API status and available endpoints.

```http
GET /
GET /api/health
```

**Response:**
```json
{
  "status": "healthy"
}
```

### Statistics
Retrieve basic statistics about a dataset.

```http
GET /api/stats?filepath=<path>
```

**Parameters:**
- `filepath` (required): Path to CSV file

**Response:**
```json
{
  "row_count": 1000,
  "column_count": 5,
  "columns": ["date", "open", "high", "low", "close"]
}
```

### Prediction
Make stock price predictions based on features.

```http
POST /api/predict
Content-Type: application/json

{
  "features": [100.5, 102.3, 99.8, 105.2]
}
```

**Response:**
```json
{
  "prediction": 103.45,
  "confidence": 0.87
}
```

## 🧪 Testing

### Run All Tests
```bash
pytest tests/
```

### Run with Coverage Report
```bash
pytest tests/ --cov=src --cov-report=html
```

### Run Specific Test
```bash
pytest tests/test_app.py::test_health_check -v
```

## 🛠️ Development

### Adding a New Model

1. Create a new model class in `src/models/`:
```python
from src.models.predictor import StockPredictor

class AdvancedPredictor(StockPredictor):
    def build_pipeline(self, feature_cols, label_col="price"):
        # Custom implementation
        pass
```

2. Add endpoints in `src/app/routes.py`:
```python
@api.route("/predict-advanced", methods=["POST"])
def predict_advanced():
    # Implementation
    pass
```

3. Write tests in `tests/test_app.py`:
```python
def test_predict_advanced(client):
    response = client.post("/api/predict-advanced", json={"features": [...]})
    assert response.status_code == 200
```

### Adding a New Route

1. Update `src/app/routes.py`:
```python
@api.route("/new-endpoint", methods=["GET"])
def new_endpoint():
    return jsonify({"message": "Success"}), 200
```

2. Add corresponding test:
```python
def test_new_endpoint(client):
    response = client.get("/api/new-endpoint")
    assert response.status_code == 200
```

## 🔧 Configuration

### Environment Variables

Create `.env` file based on `.env.example`:

```env
# Flask Environment: development, production, or testing
FLASK_ENV=development

# Secret key for session management (use strong key in production)
SECRET_KEY=your-very-secure-secret-key-here
```

### Configuration Classes

Modify `src/config/settings.py` to adjust application settings:

```python
class DevelopmentConfig(Config):
    DEBUG = True
    FLASK_ENV = "development"

class ProductionConfig(Config):
    DEBUG = False
    FLASK_ENV = "production"
```

## 🚢 Deployment

### Using Gunicorn (Production)

```bash
# Install production dependencies (already in requirements.txt)
pip install -r requirements.txt

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 'src.app.app:create_app()'

# With environment variables
FLASK_ENV=production gunicorn -w 4 -b 0.0.0.0:5000 'src.app.app:create_app()'
```

### Docker Deployment

Create a `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "src.app.app:create_app()"]
```

Build and run:
```bash
docker build -t stock-analysis .
docker run -p 5000:5000 stock-analysis
```

## 📊 ML Model Details

### Linear Regression Pipeline

The default model includes:
- **Feature Assembly**: Combines input features into vectors
- **Standardization**: Scales features to mean=0, std=1
- **Linear Regression**: Predicts stock prices

**Hyperparameters:**
- Max iterations: 100
- Regularization parameter: 0.01

### Extending the Model

Modify `src/models/predictor.py` to add more sophisticated models:
- Gradient Boosting
- Random Forest
- Neural Networks
- LSTM for time-series

## 🐛 Troubleshooting

### PySpark Issues
- Ensure Java is installed: `java -version`
- Check PySpark installation: `python -c "import pyspark; print(pyspark.__version__)"`

### Import Errors
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### Port Already in Use
```bash
# Change port in app.py or use:
python -m flask --app src.app.app run --port 5001
```

## 📈 Performance Optimization

### PySpark Configuration

Adjust `src/utils/spark_utils.py` for better performance:
```python
spark = SparkSession.builder \
    .appName("stock-analysis") \
    .config("spark.executor.memory", "4g") \
    .config("spark.executor.cores", "4") \
    .getOrCreate()
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Darshan** - [GitHub Profile](https://github.com/darshan087)

## 📞 Support

For issues, questions, or suggestions:
- Open an [Issue](https://github.com/darshan087/stock-analysis-system/issues)
- Start a [Discussion](https://github.com/darshan087/stock-analysis-system/discussions)

## 🙏 Acknowledgments

- [Flask Documentation](https://flask.palletsprojects.com/)
- [PySpark Documentation](https://spark.apache.org/docs/latest/api/python/)
- [scikit-learn](https://scikit-learn.org/)

---

**Last Updated:** November 2025  
**Status:** Active Development
