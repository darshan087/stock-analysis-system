"""Flask API routes"""

from flask import Blueprint, jsonify, request
from src.utils.fetch_data import fetch_stock_data, validate_stock_data, get_latest_price
from src.models.feature_engineering import engineer_features, prepare_ml_data
from src.models.predictor import TimeSeriesForecaster, TrendAnalyzer, StockPredictor
from src.utils.visualization import StockVisualizer
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import traceback

api = Blueprint("api", __name__, url_prefix="/api")


@api.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()}), 200


@api.route("/stats", methods=["GET"])
def get_stats():
    """Get basic statistics about stock data
    
    Query parameters:
        - ticker: Stock ticker (e.g., AAPL, GOOGL)
        - period: Time period ('1y', '6mo', '3mo', '1mo')
    """
    try:
        ticker = request.args.get("ticker", "AAPL")
        period = request.args.get("period", "1y")
        
        df = fetch_stock_data(ticker, period=period)
        
        if not validate_stock_data(df):
            return jsonify({"error": "Invalid or incomplete data"}), 400
        
        stats = {
            "ticker": ticker,
            "period": period,
            "rows": len(df),
            "columns": df.columns.tolist(),
            "date_range": {
                "start": df['date'].min().strftime('%Y-%m-%d'),
                "end": df['date'].max().strftime('%Y-%m-%d')
            },
            "price_stats": {
                "current": float(df['close'].iloc[-1]),
                "min": float(df['close'].min()),
                "max": float(df['close'].max()),
                "avg": float(df['close'].mean()),
                "std": float(df['close'].std())
            },
            "volume_stats": {
                "avg_volume": float(df['volume'].mean()),
                "total_volume": float(df['volume'].sum())
            }
        }
        
        return jsonify(stats), 200
    
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


@api.route("/forecast", methods=["GET"])
def forecast():
    """Forecast stock price for next N days
    
    Query parameters:
        - ticker: Stock ticker symbol
        - days: Number of days to forecast (default 5)
        - method: Forecasting method ('exp_smooth' or 'linear_trend')
        - period: Historical period to use for forecast
    """
    try:
        ticker = request.args.get("ticker", "AAPL")
        days = int(request.args.get("days", 5))
        method = request.args.get("method", "exp_smooth")
        period = request.args.get("period", "1y")
        
        if days < 1 or days > 30:
            return jsonify({"error": "Days must be between 1 and 30"}), 400
        
        # Fetch data
        df = fetch_stock_data(ticker, period=period)
        
        if not validate_stock_data(df):
            return jsonify({"error": "Invalid data"}), 400
        
        # Generate forecast
        forecaster = TimeSeriesForecaster()
        forecast_values = forecaster.forecast_next_n_days(df['close'], n_days=days, method=method)
        
        # Get last date and generate forecast dates
        last_date = pd.Timestamp(df['date'].max())
        freq = 'D'  # Daily frequency
        forecast_dates = pd.date_range(start=last_date + timedelta(days=1), periods=days, freq=freq)
        
        forecast_data = [
            {
                "date": date.strftime('%Y-%m-%d'),
                "price": float(price)
            }
            for date, price in zip(forecast_dates, forecast_values)
        ]
        
        result = {
            "ticker": ticker,
            "method": method,
            "period_analyzed": period,
            "current_price": float(df['close'].iloc[-1]),
            "last_date": last_date.strftime('%Y-%m-%d'),
            "forecast": forecast_data,
            "avg_forecast": float(np.mean(forecast_values))
        }
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route("/trends", methods=["GET"])
def trends():
    """Analyze stock trends and signals
    
    Query parameters:
        - ticker: Stock ticker symbol
        - period: Historical period ('1y', '6mo', '3mo', '1mo')
    """
    try:
        ticker = request.args.get("ticker", "AAPL")
        period = request.args.get("period", "6mo")
        
        df = fetch_stock_data(ticker, period=period)
        
        if not validate_stock_data(df):
            return jsonify({"error": "Invalid data"}), 400
        
        # Engineer features
        df = engineer_features(df)
        
        # Analyze trends
        analyzer = TrendAnalyzer()
        trend = analyzer.calculate_trend(df)
        support_resistance = analyzer.identify_support_resistance(df)
        returns = df['close'].pct_change() * 100
        volatility = analyzer.calculate_volatility(returns)
        momentum = analyzer.momentum_score(df)
        
        # Get recent trend
        recent_trend = trend.iloc[-1]
        trend_label = "UPTREND" if recent_trend == 1 else "DOWNTREND" if recent_trend == -1 else "NEUTRAL"
        
        result = {
            "ticker": ticker,
            "current_price": float(df['close'].iloc[-1]),
            "trend": {
                "direction": trend_label,
                "signal": int(recent_trend)
            },
            "support_resistance": {
                "support": float(support_resistance['support']),
                "resistance": float(support_resistance['resistance']),
                "gap": float(support_resistance['gap'])
            },
            "volatility": float(volatility),
            "momentum": float(momentum),
            "indicators": {
                "rsi": float(df['rsi_14'].iloc[-1]) if 'rsi_14' in df.columns else None,
                "sma_20": float(df['sma_20'].iloc[-1]) if 'sma_20' in df.columns else None,
                "sma_50": float(df['sma_50'].iloc[-1]) if 'sma_50' in df.columns else None
            }
        }
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route("/predict", methods=["POST"])
def predict():
    """Make price predictions using ML model
    
    Expected JSON:
        {
            "ticker": "AAPL",
            "model_type": "linear",
            "period": "1y"
        }
    """
    try:
        data = request.get_json()
        ticker = data.get("ticker", "AAPL")
        model_type = data.get("model_type", "linear")
        period = data.get("period", "1y")
        
        # Fetch data
        df = fetch_stock_data(ticker, period=period)
        
        if not validate_stock_data(df):
            return jsonify({"error": "Invalid data"}), 400
        
        # Prepare ML data
        X, y = prepare_ml_data(df)
        
        # Train model
        predictor = StockPredictor()
        predictor.build_model(model_type=model_type)
        predictor.train(X, y)
        
        # Make predictions
        predictions = predictor.predict(X)
        
        result = {
            "ticker": ticker,
            "model_type": model_type,
            "accuracy": float(np.mean(predictions == y)),
            "predictions": predictions[-5:].tolist(),  # Last 5 predictions
            "model_performance": {
                "mean_prediction": float(np.mean(predictions)),
                "std_prediction": float(np.std(predictions))
            }
        }
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


@api.route("/historical", methods=["GET"])
def historical():
    """Get historical stock data
    
    Query parameters:
        - ticker: Stock ticker symbol
        - period: Period ('1y', '6mo', '3mo', '1mo')
        - limit: Number of rows to return (default all)
    """
    try:
        ticker = request.args.get("ticker", "AAPL")
        period = request.args.get("period", "1y")
        limit = request.args.get("limit", type=int)
        
        df = fetch_stock_data(ticker, period=period)
        
        if limit:
            df = df.tail(limit)
        
        records = df.to_dict('records')
        
        # Convert datetime objects to strings
        for record in records:
            if 'date' in record and hasattr(record['date'], 'isoformat'):
                record['date'] = record['date'].isoformat()
        
        return jsonify({
            "ticker": ticker,
            "period": period,
            "count": len(records),
            "data": records
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
