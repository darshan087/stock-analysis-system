"""Stock price visualization and plotting utilities"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from typing import Optional, Tuple
import io
import base64


class StockVisualizer:
    """Generate stock forecasting visualizations"""
    
    @staticmethod
    def plot_price_with_ma(
        df: pd.DataFrame,
        title: str = "Stock Price with Moving Averages",
        figsize: Tuple[int, int] = (14, 7)
    ) -> plt.Figure:
        """Plot stock price with moving averages
        
        Args:
            df: Stock DataFrame with columns: close, sma_20, sma_50
            title: Plot title
            figsize: Figure size
            
        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        ax.plot(df.index, df['close'], label='Close Price', linewidth=2, color='black')
        
        if 'sma_20' in df.columns:
            ax.plot(df.index, df['sma_20'], label='SMA 20', linewidth=1.5, alpha=0.7)
        
        if 'sma_50' in df.columns:
            ax.plot(df.index, df['sma_50'], label='SMA 50', linewidth=1.5, alpha=0.7)
        
        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Price ($)', fontsize=12)
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        
        fig.tight_layout()
        return fig
    
    @staticmethod
    def plot_forecast(
        historical: pd.DataFrame,
        forecast: np.ndarray,
        forecast_dates: Optional[pd.DatetimeIndex] = None,
        title: str = "Stock Price Forecast",
        figsize: Tuple[int, int] = (14, 7)
    ) -> plt.Figure:
        """Plot historical price and forecast
        
        Args:
            historical: Historical price DataFrame
            forecast: Forecast values array
            forecast_dates: Dates for forecast (if None, extends from last date)
            title: Plot title
            figsize: Figure size
            
        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        # Plot historical data
        ax.plot(historical.index, historical['close'], label='Historical Price', 
                linewidth=2, color='blue')
        
        # Generate forecast dates if not provided
        if forecast_dates is None:
            last_date = historical.index[-1]
            freq = pd.infer_freq(historical.index)
            forecast_dates = pd.date_range(start=last_date, periods=len(forecast) + 1, freq=freq)[1:]
        
        # Plot forecast
        forecast_values = np.concatenate([[historical['close'].iloc[-1]], forecast])
        ax.plot(forecast_dates, forecast_values[1:], label='Forecast', 
                linewidth=2, color='red', linestyle='--', marker='o', markersize=5)
        
        # Add confidence interval
        ax.fill_between(forecast_dates, 
                       forecast[:-1] * 0.95, 
                       forecast[:-1] * 1.05, 
                       alpha=0.2, color='red')
        
        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Price ($)', fontsize=12)
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        
        fig.tight_layout()
        return fig
    
    @staticmethod
    def plot_bollinger_bands(
        df: pd.DataFrame,
        title: str = "Bollinger Bands",
        figsize: Tuple[int, int] = (14, 7)
    ) -> plt.Figure:
        """Plot price with Bollinger Bands
        
        Args:
            df: Stock DataFrame with upper_bb, middle_bb, lower_bb columns
            title: Plot title
            figsize: Figure size
            
        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        ax.plot(df.index, df['close'], label='Close Price', linewidth=2, color='black')
        
        if all(col in df.columns for col in ['upper_bb', 'middle_bb', 'lower_bb']):
            ax.plot(df.index, df['middle_bb'], label='Middle Band (SMA)', 
                   linewidth=1.5, alpha=0.7, color='blue')
            ax.fill_between(df.index, df['upper_bb'], df['lower_bb'], 
                           alpha=0.2, color='blue', label='Bollinger Bands')
        
        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Price ($)', fontsize=12)
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        
        fig.tight_layout()
        return fig
    
    @staticmethod
    def plot_rsi(
        df: pd.DataFrame,
        title: str = "RSI (Relative Strength Index)",
        figsize: Tuple[int, int] = (14, 5)
    ) -> plt.Figure:
        """Plot RSI indicator
        
        Args:
            df: Stock DataFrame with rsi_14 column
            title: Plot title
            figsize: Figure size
            
        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        if 'rsi_14' in df.columns:
            ax.plot(df.index, df['rsi_14'], label='RSI(14)', linewidth=2, color='purple')
            ax.axhline(y=70, color='r', linestyle='--', alpha=0.5, label='Overbought (70)')
            ax.axhline(y=30, color='g', linestyle='--', alpha=0.5, label='Oversold (30)')
            ax.fill_between(df.index, 30, 70, alpha=0.1, color='gray')
        
        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('RSI', fontsize=12)
        ax.set_ylim([0, 100])
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        
        fig.tight_layout()
        return fig
    
    @staticmethod
    def plot_volume(
        df: pd.DataFrame,
        title: str = "Trading Volume",
        figsize: Tuple[int, int] = (14, 5)
    ) -> plt.Figure:
        """Plot trading volume
        
        Args:
            df: Stock DataFrame with volume column
            title: Plot title
            figsize: Figure size
            
        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        colors = ['green' if df['close'].iloc[i] >= df['close'].iloc[i-1] else 'red' 
                 for i in range(1, len(df))]
        colors = ['gray'] + colors
        
        ax.bar(df.index, df['volume'], color=colors, alpha=0.6)
        
        if 'volume_sma' in df.columns:
            ax.plot(df.index, df['volume_sma'], color='blue', linewidth=2, 
                   label='Volume SMA(20)')
        
        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Volume', fontsize=12)
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        
        fig.tight_layout()
        return fig
    
    @staticmethod
    def fig_to_base64(fig: plt.Figure) -> str:
        """Convert matplotlib figure to base64 string for embedding
        
        Args:
            fig: Matplotlib figure
            
        Returns:
            Base64 encoded string
        """
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode()
        plt.close(fig)
        return img_base64
    
    @staticmethod
    def create_dashboard(
        df: pd.DataFrame,
        ticker: str,
        forecast: Optional[np.ndarray] = None
    ) -> plt.Figure:
        """Create a 2x2 dashboard with multiple indicators
        
        Args:
            df: Stock DataFrame
            ticker: Stock ticker symbol
            forecast: Optional forecast array
            
        Returns:
            Matplotlib figure with subplots
        """
        fig = plt.figure(figsize=(16, 10))
        
        # Price with MA
        ax1 = plt.subplot(2, 2, 1)
        ax1.plot(df.index, df['close'], label='Close', linewidth=2)
        if 'sma_20' in df.columns:
            ax1.plot(df.index, df['sma_20'], label='SMA 20', alpha=0.7)
        ax1.set_title(f'{ticker} - Price & Moving Averages', fontsize=12, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # RSI
        ax2 = plt.subplot(2, 2, 2)
        if 'rsi_14' in df.columns:
            ax2.plot(df.index, df['rsi_14'], color='purple', linewidth=2)
            ax2.axhline(y=70, color='r', linestyle='--', alpha=0.5)
            ax2.axhline(y=30, color='g', linestyle='--', alpha=0.5)
            ax2.set_ylim([0, 100])
        ax2.set_title('RSI(14)', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        
        # Volume
        ax3 = plt.subplot(2, 2, 3)
        colors = ['green' if df['close'].iloc[i] >= df['close'].iloc[i-1] else 'red' 
                 for i in range(1, len(df))]
        ax3.bar(df.index, df['volume'], color=['gray'] + colors, alpha=0.6)
        ax3.set_title('Volume', fontsize=12, fontweight='bold')
        ax3.grid(True, alpha=0.3)
        
        # MACD or Forecast
        ax4 = plt.subplot(2, 2, 4)
        if forecast is not None:
            last_date = df.index[-1]
            forecast_dates = pd.date_range(start=last_date, periods=len(forecast)+1)[1:]
            ax4.plot(df.index[-30:], df['close'].iloc[-30:], label='Historical', linewidth=2)
            ax4.plot(forecast_dates, forecast, label='Forecast', linestyle='--', marker='o')
            ax4.set_title('Price Forecast (5-day)', fontsize=12, fontweight='bold')
            ax4.legend()
        elif 'macd' in df.columns:
            ax4.plot(df.index, df['macd'], label='MACD', linewidth=2)
            ax4.plot(df.index, df['macd_signal'], label='Signal', linewidth=1.5)
            ax4.bar(df.index, df['macd_hist'], label='Histogram', alpha=0.3)
            ax4.set_title('MACD', fontsize=12, fontweight='bold')
            ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        fig.suptitle(f'{ticker} - Trading Dashboard', fontsize=16, fontweight='bold')
        fig.tight_layout()
        
        return fig
