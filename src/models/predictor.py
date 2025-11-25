"""ML prediction models"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from typing import Dict, Tuple, Optional


class StockPredictor:
    """Stock price prediction model"""
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.feature_cols = None
    
    def build_model(self, model_type: str = "linear") -> None:
        """Build ML model
        
        Args:
            model_type: Type of model ('linear', 'rf')
        """
        if model_type == "linear":
            self.model = LinearRegression()
        elif model_type == "rf":
            self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        else:
            raise ValueError(f"Unknown model type: {model_type}")
    
    def train(self, X: pd.DataFrame, y: pd.Series) -> None:
        """Train the model
        
        Args:
            X: Features DataFrame
            y: Target Series
        """
        if self.model is None:
            self.build_model()
        
        # Scale features
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        # Store feature columns
        self.feature_cols = X.columns.tolist()
        
        # Train model
        self.model.fit(X_scaled, y)
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Make predictions
        
        Args:
            X: Features DataFrame
            
        Returns:
            Predictions array
        """
        if self.model is None or self.scaler is None:
            raise ValueError("Model not trained. Call train() first.")
        
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)
    
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Get prediction probabilities (for classification models)
        
        Args:
            X: Features DataFrame
            
        Returns:
            Probability predictions
        """
        if not hasattr(self.model, 'predict_proba'):
            raise ValueError("Model does not support probability predictions")
        
        X_scaled = self.scaler.transform(X)
        return self.model.predict_proba(X_scaled)


class TimeSeriesForecaster:
    """Time series forecasting for stock prices"""
    
    def __init__(self):
        self.trend = None
        self.seasonality = None
        self.residuals = None
    
    def simple_exponential_smoothing(self, series: pd.Series, alpha: float = 0.3) -> np.ndarray:
        """Simple Exponential Smoothing forecast
        
        Args:
            series: Time series data
            alpha: Smoothing parameter (0-1)
            
        Returns:
            Smoothed series
        """
        result = [series.iloc[0]]
        
        for n in range(1, len(series)):
            result.append(alpha * series.iloc[n] + (1 - alpha) * result[n-1])
        
        return np.array(result)
    
    def forecast_next_n_days(self, series: pd.Series, n_days: int = 5, method: str = "exp_smooth") -> np.ndarray:
        """Forecast next N days
        
        Args:
            series: Historical price series
            n_days: Number of days to forecast
            method: Forecasting method ('exp_smooth', 'linear_trend')
            
        Returns:
            Forecast array of length n_days
        """
        if method == "exp_smooth":
            smoothed = self.simple_exponential_smoothing(series)
            last_value = smoothed[-1]
            trend = smoothed[-1] - smoothed[-2]
            
            forecast = [last_value]
            for i in range(n_days - 1):
                forecast.append(forecast[-1] + trend * 0.95)  # Decay trend slightly
            
            return np.array(forecast)
        
        elif method == "linear_trend":
            x = np.arange(len(series)).reshape(-1, 1)
            y = series.values
            
            model = LinearRegression()
            model.fit(x, y)
            
            x_future = np.arange(len(series), len(series) + n_days).reshape(-1, 1)
            return model.predict(x_future)
        
        else:
            raise ValueError(f"Unknown forecasting method: {method}")


class TrendAnalyzer:
    """Analyze and classify stock trends"""
    
    @staticmethod
    def calculate_trend(df: pd.DataFrame, window: int = 20) -> pd.Series:
        """Calculate trend using moving average
        
        Args:
            df: Stock DataFrame
            window: MA window
            
        Returns:
            Trend series (1: uptrend, -1: downtrend, 0: neutral)
        """
        df = df.copy()
        sma = df['close'].rolling(window=window).mean()
        
        trend = pd.Series(0, index=df.index)
        trend[df['close'] > sma] = 1  # Uptrend
        trend[df['close'] < sma] = -1  # Downtrend
        
        return trend
    
    @staticmethod
    def identify_support_resistance(df: pd.DataFrame, window: int = 20) -> Dict[str, float]:
        """Identify support and resistance levels
        
        Args:
            df: Stock DataFrame
            window: Window for local extrema
            
        Returns:
            Dictionary with support and resistance levels
        """
        local_min = df['low'].rolling(window=window, center=True).min()
        local_max = df['high'].rolling(window=window, center=True).max()
        
        # Get recent support/resistance
        recent_support = df[local_min == df['low']]['low'].iloc[-5:].min()
        recent_resistance = df[local_max == df['high']]['high'].iloc[-5:].max()
        
        return {
            'support': recent_support,
            'resistance': recent_resistance,
            'gap': recent_resistance - recent_support
        }
    
    @staticmethod
    def calculate_volatility(returns: pd.Series, window: int = 20) -> float:
        """Calculate rolling volatility
        
        Args:
            returns: Daily returns series
            window: Rolling window
            
        Returns:
            Current volatility (annualized)
        """
        volatility = returns.rolling(window=window).std()
        return volatility.iloc[-1] * np.sqrt(252)  # Annualize
    
    @staticmethod
    def momentum_score(df: pd.DataFrame, window: int = 14) -> float:
        """Calculate momentum score (-1 to 1)
        
        Args:
            df: Stock DataFrame
            window: Window for calculation
            
        Returns:
            Momentum score
        """
        recent_change = (df['close'].iloc[-1] - df['close'].iloc[-window]) / df['close'].iloc[-window]
        
        # Normalize to -1 to 1
        momentum = np.tanh(recent_change * 10)
        
        return momentum
