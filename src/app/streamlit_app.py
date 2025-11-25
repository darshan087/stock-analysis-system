import streamlit as st
import os
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.ml.pipeline import PipelineModel
from pyspark.sql.functions import col, lag
from pyspark.sql.window import Window
import plotly.graph_objs as go

DATA_DIR = "data"
MODEL_DIR = "src/models/spark_rf_model"

@st.cache_resource
def create_spark():
    return SparkSession.builder \
        .appName("StreamlitSpark") \
        .master("local[*]") \
        .getOrCreate()

def engineer_and_predict(spark, csv_file, model_path, lags=5):
    df = spark.read.csv(csv_file, header=True, inferSchema=True).orderBy("Date")
    w = Window.orderBy("Date")
    for i in range(1, lags + 1):
        df = df.withColumn(f"lag_{i}", lag(col("Close"), i).over(w))
    df = df.na.drop()

    model = PipelineModel.load(model_path)
    preds = model.transform(df).select("Date", "Close", "prediction").toPandas()
    preds["Date"] = pd.to_datetime(preds["Date"])
    return preds

st.title("📈 PySpark Stock Market Forecasting")

files = [f for f in os.listdir(DATA_DIR) if f.endswith(".csv")]

symbol = st.sidebar.selectbox("Choose Stock", files)
lags = st.sidebar.slider("Lag Count", 1, 10, 5)

if st.sidebar.button("Predict"):
    path = os.path.join(DATA_DIR, symbol)
    spark = create_spark()
    result = engineer_and_predict(spark, path, MODEL_DIR, lags)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=result["Date"], y=result["Close"], name="Actual"))
    fig.add_trace(go.Scatter(x=result["Date"], y=result["prediction"], name="Predicted"))

    st.plotly_chart(fig, use_container_width=True)

