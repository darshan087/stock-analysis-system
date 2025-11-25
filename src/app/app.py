"""Flask application factory"""

from flask import Flask
from src.config.settings import get_config
from src.app.routes import api


def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    # Load configuration
    config = get_config()
    app.config.from_object(config)
    
    # Register blueprints
    app.register_blueprint(api)
    
    @app.route("/", methods=["GET"])
    def index():
        return {
            "name": "Stock Analysis ML API",
            "version": "0.1.0",
            "endpoints": {
                "health": "/api/health",
                "stats": "/api/stats",
                "predict": "/api/predict"
            }
        }
    
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)
