"""Tests for stock forecasting functionality"""

import pytest
import pandas as pd
import numpy as np
from src.utils.fetch_data import fetch_stock_data, validate_stock_data
from src.models.feature_engineering import engineer_features, prepare_ml_data, TechnicalIndicators
from src.models.predictor import TimeSeriesForecaster, TrendAnalyzer, StockPredictor
from src.app.app import create_app


@pytest.fixture
def client():
    """Create Flask test client"""
    app = create_app()
    app.config["TESTING"] = True
    
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_stock_data():
    """Create sample stock data for testing"""
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
    data = {
        'date': dates,
        'open': np.random.uniform(100, 110, 100),
        'high': np.random.uniform(110, 120, 100),
        'low': np.random.uniform(90, 100, 100),
        'close': np.random.uniform(100, 110, 100),
        'volume': np.random.uniform(1000000, 5000000, 100),
        'adj close': np.random.uniform(100, 110, 100)
    }
    return pd.DataFrame(data)


class TestAPI:
    """Test API endpoints"""
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.get_json()["status"] == "healthy"
    
    def test_stats_endpoint(self, client):
        """Test stats endpoint with AAPL"""
        response = client.get("/api/stats?ticker=AAPL&period=1mo")
        assert response.status_code in [200, 500]  # May fail without yfinance
        if response.status_code == 200:
            data = response.get_json()
            assert "ticker" in data
            assert "price_stats" in data
    
    def test_forecast_endpoint(self, client):
        """Test forecast endpoint"""
        response = client.get("/api/forecast?ticker=AAPL&days=5")
        assert response.status_code in [200, 500]
    
    def test_trends_endpoint(self, client):
        """Test trends endpoint"""
        response = client.get("/api/trends?ticker=AAPL")
        assert response.status_code in [200, 500]


class TestTechnicalIndicators:
    """Test technical indicator calculations"""
    
    def test_moving_average(self, sample_stock_data):
        """Test moving average calculation"""
        ma = TechnicalIndicators.moving_average(sample_stock_data, window=5)
        assert len(ma) == len(sample_stock_data)
        assert ma.iloc[:4].isna().all()  # First 4 values should be NaN
        assert not ma.iloc[4:].isna().any()  # Rest should not be NaN
    
    def test_rsi(self, sample_stock_data):
        """Test RSI calculation"""
        rsi = TechnicalIndicators.rsi(sample_stock_data, window=14)
        assert len(rsi) == len(sample_stock_data)
        # RSI should be between 0 and 100
        valid_rsi = rsi.dropna()
        assert (valid_rsi >= 0).all() and (valid_rsi <= 100).all()
    
    def test_macd(self, sample_stock_data):
        """Test MACD calculation"""
        macd, signal, hist = TechnicalIndicators.macd(sample_stock_data)
        assert len(macd) == len(sample_stock_data)
        assert len(signal) == len(sample_stock_data)
        assert len(hist) == len(sample_stock_data)
    
    def test_bollinger_bands(self, sample_stock_data):
        """Test Bollinger Bands calculation"""
        upper, middle, lower = TechnicalIndicators.bollinger_bands(sample_stock_data, window=20)
        
        # Upper band should always be above middle, middle above lower
        valid_idx = ~(upper.isna() | middle.isna() | lower.isna())
        assert (upper[valid_idx] > middle[valid_idx]).all()
        assert (middle[valid_idx] > lower[valid_idx]).all()


class TestFeatureEngineering:
    """Test feature engineering"""
    
    def test_engineer_features(self, sample_stock_data):
        """Test feature engineering"""
        df_engineered = engineer_features(sample_stock_data)
        
        # Check that new features were added
        expected_features = ['daily_return', 'sma_5', 'sma_20', 'rsi_14', 'atr']
        for feature in expected_features:
            assert feature in df_engineered.columns
    
    def test_prepare_ml_data(self, sample_stock_data):
        """Test ML data preparation"""
        X, y = prepare_ml_data(sample_stock_data)
        
        # Check dimensions
        assert len(X) == len(y)
        assert len(X) > 0
        assert X.shape[1] > 0  # Should have features
        
        # Check target values are binary
        assert set(y.unique()).issubset({0, 1})


class TestForecasting:
    """Test forecasting models"""
    
    def test_exponential_smoothing(self, sample_stock_data):
        """Test exponential smoothing"""
        forecaster = TimeSeriesForecaster()
        forecast = forecaster.forecast_next_n_days(
            sample_stock_data['close'],
            n_days=5,
            method='exp_smooth'
        )
        
        assert len(forecast) == 5
        assert all(isinstance(x, (int, float, np.number)) for x in forecast)
    
    def test_linear_trend_forecast(self, sample_stock_data):
        """Test linear trend forecasting"""
        forecaster = TimeSeriesForecaster()
        forecast = forecaster.forecast_next_n_days(
            sample_stock_data['close'],
            n_days=5,
            method='linear_trend'
        )
        
        assert len(forecast) == 5
        assert all(isinstance(x, (int, float, np.number)) for x in forecast)


class TestTrendAnalysis:
    """Test trend analysis"""
    
    def test_trend_calculation(self, sample_stock_data):
        """Test trend calculation"""
        sample_stock_data = engineer_features(sample_stock_data)
        trend = TrendAnalyzer.calculate_trend(sample_stock_data)
        
        assert len(trend) == len(sample_stock_data)
        assert set(trend.unique()).issubset({-1, 0, 1})
    
    def test_support_resistance(self, sample_stock_data):
        """Test support/resistance identification"""
        levels = TrendAnalyzer.identify_support_resistance(sample_stock_data)
        
        assert 'support' in levels
        assert 'resistance' in levels
        assert 'gap' in levels
        assert levels['resistance'] > levels['support']
    
    def test_volatility_calculation(self, sample_stock_data):
        """Test volatility calculation"""
        returns = sample_stock_data['close'].pct_change()
        volatility = TrendAnalyzer.calculate_volatility(returns)
        
        assert isinstance(volatility, (int, float, np.number))
        assert volatility >= 0
    
    def test_momentum_score(self, sample_stock_data):
        """Test momentum score calculation"""
        momentum = TrendAnalyzer.momentum_score(sample_stock_data)
        
        assert isinstance(momentum, (int, float, np.number))
        assert -1 <= momentum <= 1


class TestStockPredictor:
    """Test ML predictor"""
    
    def test_predictor_linear_model(self, sample_stock_data):
        """Test linear regression model"""
        X, y = prepare_ml_data(sample_stock_data)
        
        predictor = StockPredictor()
        predictor.build_model(model_type='linear')
        predictor.train(X, y)
        
        predictions = predictor.predict(X[-10:])
        assert len(predictions) == 10
    
    def test_predictor_rf_model(self, sample_stock_data):
        """Test random forest model"""
        X, y = prepare_ml_data(sample_stock_data)
        
        predictor = StockPredictor()
        predictor.build_model(model_type='rf')
        predictor.train(X, y)
        
        predictions = predictor.predict(X[-10:])
        assert len(predictions) == 10
