"""PySpark utilities and helpers"""

from pyspark.sql import SparkSession


def get_spark_session(app_name: str = "stock-analysis") -> SparkSession:
    """Create or get SparkSession
    
    Args:
        app_name: Application name for Spark
        
    Returns:
        SparkSession instance
    """
    spark = SparkSession.builder \
        .appName(app_name) \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
        .getOrCreate()
    
    return spark


def stop_spark_session(spark: SparkSession) -> None:
    """Stop SparkSession
    
    Args:
        spark: SparkSession instance to stop
    """
    if spark:
        spark.stop()
