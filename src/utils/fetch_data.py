"""Stock data fetching utilities"""

import yfinance as yf
import pandas as pd
import argparse
import os
from datetime import datetime, timedelta
from typing import Optional, List


def fetch_stock_data(
    ticker: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    period: str = "1y"
) -> pd.DataFrame:
    """Fetch historical stock data using yfinance
    
    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL', 'GOOGL')
        start_date: Start date in 'YYYY-MM-DD' format
        end_date: End date in 'YYYY-MM-DD' format
        period: Period if start_date/end_date not provided ('1y', '6mo', '3mo', '1mo', '1d')
        
    Returns:
        DataFrame with OHLCV data (Open, High, Low, Close, Volume, Adj Close)
    """
    try:
        if start_date and end_date:
            data = yf.download(ticker, start=start_date, end=end_date, progress=False)
        else:
            data = yf.download(ticker, period=period, progress=False)
        
        # Reset index to have date as column
        data.reset_index(inplace=True)
        data.rename(columns={'Date': 'date'}, inplace=True)
        
        # Convert to lowercase for consistency
        data.columns = [col.lower() for col in data.columns]
        
        return data
    
    except Exception as e:
        raise ValueError(f"Failed to fetch data for {ticker}: {str(e)}")


def fetch_multiple_stocks(
    tickers: List[str],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    period: str = "1y"
) -> dict:
    """Fetch data for multiple stocks
    
    Args:
        tickers: List of stock ticker symbols
        start_date: Start date in 'YYYY-MM-DD' format
        end_date: End date in 'YYYY-MM-DD' format
        period: Period if dates not provided
        
    Returns:
        Dictionary with ticker as key and DataFrame as value
    """
    data = {}
    
    for ticker in tickers:
        try:
            df = fetch_stock_data(ticker, start_date, end_date, period)
            data[ticker] = df
        except Exception as e:
            print(f"Warning: Could not fetch data for {ticker}: {str(e)}")
    
    return data


def validate_stock_data(df: pd.DataFrame) -> bool:
    """Validate stock data completeness and quality
    
    Args:
        df: Stock data DataFrame
        
    Returns:
        True if valid, False otherwise
    """
    required_columns = ['date', 'open', 'high', 'low', 'close', 'volume']
    
    # Check required columns
    if not all(col in df.columns for col in required_columns):
        return False
    
    # Check for missing values
    if df[required_columns].isnull().any().any():
        return False
    
    # Check that prices are positive
    price_cols = ['open', 'high', 'low', 'close']
    if (df[price_cols] <= 0).any().any():
        return False
    
    return True


def get_latest_price(ticker: str) -> Optional[float]:
    """Get latest closing price for a stock
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Latest closing price or None if fetch fails
    """
    try:
        data = yf.download(ticker, period="1d", progress=False)
        return float(data['Close'].iloc[-1])
    except Exception as e:
        print(f"Error fetching latest price for {ticker}: {str(e)}")
        return None


def fetch(symbol: str, start: str, end: str, out_dir: str):
    """Legacy CLI function for backwards compatibility"""
    os.makedirs(out_dir, exist_ok=True)
    print(f"[fetch_data] Downloading {symbol} from {start} to {end}")
    df = yf.download(symbol, start=start, end=end, progress=False)
    if df.empty:
        raise SystemExit(f"No data returned for {symbol}")

    df.reset_index(inplace=True)
    df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')

    out_path = os.path.join(out_dir, f"{symbol}.csv")
    df.to_csv(out_path, index=False)

    print(f"[fetch_data] Saved: {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--start", default="2015-01-01")
    parser.add_argument("--end", default=datetime.today().strftime("%Y-%m-%d"))
    parser.add_argument("--out_dir", default="data")
    args = parser.parse_args()

    fetch(args.symbol, args.start, args.end, args.out_dir)
