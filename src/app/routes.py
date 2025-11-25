"""Flask API routes"""

from flask import Blueprint, jsonify, request
from src.utils.spark_utils import get_spark_session

api = Blueprint("api", __name__, url_prefix="/api")


@api.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200


@api.route("/stats", methods=["GET"])
def get_stats():
    """Get basic statistics
    
    Query parameters:
        - filepath: Path to data file
    """
    try:
        filepath = request.args.get("filepath")
        if not filepath:
            return jsonify({"error": "filepath parameter required"}), 400
        
        spark = get_spark_session()
        df = spark.read.csv(filepath, header=True, inferSchema=True)
        
        stats = {
            "row_count": df.count(),
            "column_count": len(df.columns),
            "columns": df.columns
        }
        
        return jsonify(stats), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route("/predict", methods=["POST"])
def predict():
    """Make predictions endpoint
    
    Expected JSON:
        {
            "features": [list of feature values]
        }
    """
    try:
        data = request.get_json()
        if not data or "features" not in data:
            return jsonify({"error": "features field required in JSON"}), 400
        
        # TODO: Implement actual prediction logic
        return jsonify({
            "prediction": 0.0,
            "confidence": 0.0
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
