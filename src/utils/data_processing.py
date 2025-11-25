"""Data processing utilities"""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def load_csv(spark, filepath: str) -> DataFrame:
    """Load CSV file into Spark DataFrame
    
    Args:
        spark: SparkSession instance
        filepath: Path to CSV file
        
    Returns:
        Spark DataFrame
    """
    df = spark.read.csv(filepath, header=True, inferSchema=True)
    return df


def save_parquet(df: DataFrame, output_path: str) -> None:
    """Save DataFrame as Parquet
    
    Args:
        df: Spark DataFrame to save
        output_path: Output path for parquet file
    """
    df.write.mode("overwrite").parquet(output_path)


def get_basic_stats(df: DataFrame) -> dict:
    """Get basic statistics about DataFrame
    
    Args:
        df: Spark DataFrame
        
    Returns:
        Dictionary with basic statistics
    """
    return {
        "row_count": df.count(),
        "column_count": len(df.columns),
        "columns": df.columns
    }
