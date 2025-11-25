"""Feature engineering for stock forecasting"""

import pandas as pd
import numpy as np
from typing import Tuple


class TechnicalIndicators:
    """Calculate technical indicators for stock analysis"""
    
    @staticmethod
    def moving_average(df: pd.DataFrame, window: int = 20, column: str = 'close') -> pd.Series:
        """Simple Moving Average (SMA)
        
        Args:
            df: Stock DataFrame
            window: Number of periods
            column: Column to calculate MA on
            
        Returns:
            Moving average series
        """
        return df[column].rolling(window=window).mean()
    
    @staticmethod
    def exponential_moving_average(df: pd.DataFrame, window: int = 20, column: str = 'close') -> pd.Series:
        """Exponential Moving Average (EMA)
        
        Args:
            df: Stock DataFrame
            window: Number of periods
            column: Column to calculate EMA on
            
        Returns:
            EMA series
        """
        return df[column].ewm(span=window, adjust=False).mean()
    
    @staticmethod
    def rsi(df: pd.DataFrame, window: int = 14, column: str = 'close') -> pd.Series:
        """Relative Strength Index (RSI)
        
        Args:
            df: Stock DataFrame
            window: Number of periods
            column: Column to calculate RSI on
            
        Returns:
            RSI series (0-100)
        """
        delta = df[column].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9, column: str = 'close') -> Tuple[pd.Series, pd.Series, pd.Series]:
        """MACD (Moving Average Convergence Divergence)
        
        Args:
            df: Stock DataFrame
            fast: Fast EMA period
            slow: Slow EMA period
            signal: Signal line period
            column: Column to calculate MACD on
            
        Returns:
            Tuple of (MACD, Signal line, Histogram)
        """
        ema_fast = df[column].ewm(span=fast, adjust=False).mean()
        ema_slow = df[column].ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    @staticmethod
    def bollinger_bands(df: pd.DataFrame, window: int = 20, num_std: float = 2, column: str = 'close') -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Bollinger Bands
        
        Args:
            df: Stock DataFrame
            window: Period for moving average
            num_std: Number of standard deviations
            column: Column to calculate on
            
        Returns:
            Tuple of (Upper band, Middle band, Lower band)
        """
        middle = df[column].rolling(window=window).mean()
        std = df[column].rolling(window=window).std()
        upper = middle + (num_std * std)
        lower = middle - (num_std * std)
        
        return upper, middle, lower
    
    @staticmethod
    def atr(df: pd.DataFrame, window: int = 14) -> pd.Series:
        """Average True Range (ATR) - Volatility indicator
        
        Args:
            df: Stock DataFrame with high, low, close columns
            window: Period
            
        Returns:
            ATR series
        """
        high_low = df['high'] - df['low']
        high_close = abs(df['high'] - df['close'].shift())
        low_close = abs(df['low'] - df['close'].shift())
        
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.rolling(window=window).mean()
        
        return atr


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Engineer all technical features for forecasting
    
    Args:
        df: Stock DataFrame
        
    Returns:
        DataFrame with engineered features
    """
    df = df.copy()
    
    # Price changes and returns
    df['daily_return'] = df['close'].pct_change() * 100
    df['price_change'] = df['close'].diff()
    
    # Moving averages
    df['sma_5'] = TechnicalIndicators.moving_average(df, 5)
    df['sma_20'] = TechnicalIndicators.moving_average(df, 20)
    df['sma_50'] = TechnicalIndicators.moving_average(df, 50)
    df['ema_12'] = TechnicalIndicators.exponential_moving_average(df, 12)
    df['ema_26'] = TechnicalIndicators.exponential_moving_average(df, 26)
    
    # Momentum indicators
    df['rsi_14'] = TechnicalIndicators.rsi(df, 14)
    df['macd'], df['macd_signal'], df['macd_hist'] = TechnicalIndicators.macd(df)
    
    # Volatility indicators
    df['upper_bb'], df['middle_bb'], df['lower_bb'] = TechnicalIndicators.bollinger_bands(df)
    df['atr'] = TechnicalIndicators.atr(df)
    
    # Volume features
    df['volume_sma'] = df['volume'].rolling(window=20).mean()
    df['volume_ratio'] = df['volume'] / df['volume_sma']
    
    # High-Low range
    df['hl_range'] = (df['high'] - df['low']) / df['close']
    df['oc_range'] = abs(df['open'] - df['close']) / df['close']
    
    # Trend signals
    df['sma_signal'] = 0
    df.loc[df['close'] > df['sma_20'], 'sma_signal'] = 1
    df.loc[df['close'] < df['sma_20'], 'sma_signal'] = -1
    
    return df


def create_target_variable(df: pd.DataFrame, lookahead: int = 5) -> pd.DataFrame:
    """Create target variable for supervised learning
    
    Args:
        df: Stock DataFrame with features
        lookahead: Number of days ahead to predict
        
    Returns:
        DataFrame with target variable (1: up, 0: down)
    """
    df = df.copy()
    
    # Future return
    df['future_return'] = df['close'].shift(-lookahead).pct_change(lookahead) * 100
    
    # Target: 1 if price goes up, 0 if goes down
    df['target'] = (df['future_return'] > 0).astype(int)
    
    return df


def prepare_ml_data(df: pd.DataFrame, lookahead: int = 5, drop_na: bool = True) -> Tuple[pd.DataFrame, pd.Series]:
    """Prepare data for ML modeling
    
    Args:
        df: Raw stock DataFrame
        lookahead: Days ahead for prediction
        drop_na: Whether to drop NaN values
        
    Returns:
        Tuple of (Features DataFrame, Target Series)
    """
    # Engineer features
    df = engineer_features(df)
    
    # Create target
    df = create_target_variable(df, lookahead)
    
    # Select feature columns (exclude price columns, date, target)
    feature_cols = [col for col in df.columns 
                   if col not in ['date', 'open', 'high', 'low', 'close', 'adj close', 
                                  'volume', 'future_return', 'target']]
    
    X = df[feature_cols]
    y = df['target']
    
    if drop_na:
        mask = X.notna().all(axis=1) & y.notna()
        X = X[mask]
        y = y[mask]
    
    return X, y
