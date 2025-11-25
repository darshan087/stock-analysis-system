import argparse
import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
import joblib


def prepare_data_pd(csv_path, lags=5):
    df = pd.read_csv(csv_path, parse_dates=["Date"]) 
    df = df.sort_values("Date").reset_index(drop=True)

    for i in range(1, lags + 1):
        df[f"lag_{i}"] = df['Close'].shift(i)

    df = df.dropna().reset_index(drop=True)
    return df


def train(csv_path, model_dir, lags=5):
    df = prepare_data_pd(csv_path, lags)

    feature_cols = [f"lag_{i}" for i in range(1, lags + 1)]
    X = df[feature_cols]
    y = df['Close']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    rmse = mean_squared_error(y_test, preds, squared=False)

    print(f"[train_sklearn] RMSE = {rmse}")

    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, "rf_model.joblib")
    joblib.dump({'model': model, 'feature_cols': feature_cols}, model_path)

    print(f"[train_sklearn] Model saved to: {model_path}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--csv', required=True)
    parser.add_argument('--model_dir', default='src/models/sklearn_rf_model')
    parser.add_argument('--lags', type=int, default=5)
    args = parser.parse_args()

    train(args.csv, args.model_dir, args.lags)
