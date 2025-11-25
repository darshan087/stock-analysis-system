#!/usr/bin/env python
"""
Stock Forecasting System - Application Runner

Run this script to start the Flask API server:
    python run.py

The API will be available at http://localhost:5000
"""

import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(__file__))

from src.app.app import create_app

if __name__ == "__main__":
    app = create_app()
    
    print("\n" + "="*60)
    print("Stock Market Price Forecasting System")
    print("="*60)
    print("\n[+] Flask App Started")
    print("[+] API available at http://localhost:5000")
    print("\nEndpoints:")
    print("  GET  /                    - Index")
    print("  GET  /api/health          - Health check")
    print("  GET  /api/stats           - Data statistics")
    print("  GET  /api/historical      - Historical prices")
    print("  GET  /api/forecast        - 5-day price forecast")
    print("  GET  /api/trends          - Trend analysis")
    print("  POST /api/predict         - ML predictions")
    print("\nPress CTRL+C to stop\n")
    print("="*60 + "\n")
    
    app.run(debug=True, host="0.0.0.0", port=5000)
