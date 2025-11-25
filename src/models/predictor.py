"""ML prediction models"""

from pyspark.sql import DataFrame
from pyspark.ml import Pipeline
from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml.regression import LinearRegression


class StockPredictor:
    """Stock price prediction model"""
    
    def __init__(self):
        self.model = None
        self.pipeline = None
    
    def build_pipeline(self, feature_cols: list, label_col: str = "price"):
        """Build ML pipeline
        
        Args:
            feature_cols: List of feature column names
            label_col: Label column name
        """
        assembler = VectorAssembler(
            inputCols=feature_cols,
            outputCol="features"
        )
        
        scaler = StandardScaler(
            inputCol="features",
            outputCol="scaledFeatures"
        )
        
        lr = LinearRegression(
            featuresCol="scaledFeatures",
            labelCol=label_col,
            maxIter=100,
            regParam=0.01
        )
        
        self.pipeline = Pipeline(stages=[assembler, scaler, lr])
    
    def train(self, df: DataFrame) -> None:
        """Train the model
        
        Args:
            df: Training DataFrame
        """
        if self.pipeline is None:
            raise ValueError("Pipeline not built. Call build_pipeline first.")
        
        self.model = self.pipeline.fit(df)
    
    def predict(self, df: DataFrame) -> DataFrame:
        """Make predictions
        
        Args:
            df: Data for prediction
            
        Returns:
            DataFrame with predictions
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train first.")
        
        return self.model.transform(df)
