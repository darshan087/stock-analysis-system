import argparse
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lag
from pyspark.sql.window import Window
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import RandomForestRegressor
from pyspark.ml import Pipeline
from pyspark.ml.evaluation import RegressionEvaluator

def create_spark():
    return SparkSession.builder \
        .appName("StockForecast") \
        .master("local[*]") \
        .config("spark.driver.memory", "4g") \
        .getOrCreate()

def prepare_data(spark, csv_path, lags=5):
    df = spark.read.csv(csv_path, header=True, inferSchema=True).orderBy("Date")
    w = Window.orderBy("Date")

    for i in range(1, lags + 1):
        df = df.withColumn(f"lag_{i}", lag(col("Close"), i).over(w))

    df = df.na.drop()
    return df

def train(csv_path, model_dir, lags=5):
    spark = create_spark()

    df = prepare_data(spark, csv_path, lags)

    feature_cols = [f"lag_{i}" for i in range(1, lags+1)]
    assembler = VectorAssembler(inputCols=feature_cols, outputCol="features")
    rf = RandomForestRegressor(featuresCol="features", labelCol="Close")

    pipeline = Pipeline(stages=[assembler, rf])

    total = df.count()
    train_df = df.limit(int(total * 0.8))
    test_df = df.subtract(train_df)

    model = pipeline.fit(train_df)
    preds = model.transform(test_df)

    evaluator = RegressionEvaluator(labelCol="Close", predictionCol="prediction", metricName="rmse")
    rmse = evaluator.evaluate(preds)

    print(f"[train] RMSE = {rmse}")

    os.makedirs(model_dir, exist_ok=True)
    model.write().overwrite().save(model_dir)

    print(f"[train] Model saved to: {model_dir}")
    spark.stop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True)
    parser.add_argument("--model_dir", default="src/models/spark_rf_model")
    parser.add_argument("--lags", type=int, default=5)
    args = parser.parse_args()

    train(args.csv, args.model_dir, args.lags)
