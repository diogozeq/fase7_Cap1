"""
ML Models Service - Manages ML model loading and inference
"""
from pathlib import Path
from typing import Dict, List, Any, Optional
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.cluster import KMeans
from statsmodels.tsa.arima.model import ARIMA
import structlog

logger = structlog.get_logger()


class MLModelsService:
    """Manages loading, inference and retraining of ML models"""
    
    def __init__(self, models_dir: Path = Path("./models")):
        """Initialize ML Models Service"""
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        self.loaded_models: Dict[str, Any] = {}
        logger.info("ml_models_service_initialized", models_dir=str(self.models_dir))
    
    def load_model(self, model_name: str) -> Any:
        """Load serialized model from disk"""
        if model_name in self.loaded_models:
            return self.loaded_models[model_name]
        
        model_path = self.models_dir / f"{model_name}.joblib"
        if not model_path.exists():
            logger.warning("model_not_found", model_name=model_name)
            return None
        
        try:
            model = joblib.load(model_path)
            self.loaded_models[model_name] = model
            logger.info("model_loaded", model_name=model_name)
            return model
        except Exception as e:
            logger.error("model_load_failed", model_name=model_name, error=str(e))
            return None
    
    def predict_risk(self, features: np.ndarray) -> Dict:
        """Predict emergency risk using RandomForest"""
        model = self.load_model("risk_classifier")
        
        if model is None:
            # Return default prediction if model not available
            return {
                "risk_level": "unknown",
                "probability": 0.0,
                "factors": {}
            }
        
        try:
            prediction = model.predict(features.reshape(1, -1))[0]
            probability = model.predict_proba(features.reshape(1, -1))[0]
            
            # Get feature importance
            feature_names = ["umidade", "ph", "temperatura"]
            importance = dict(zip(feature_names, model.feature_importances_))
            
            risk_levels = ["low", "medium", "high"]
            risk_level = risk_levels[prediction] if prediction < len(risk_levels) else "unknown"
            
            return {
                "risk_level": risk_level,
                "probability": float(max(probability)),
                "factors": importance
            }
        except Exception as e:
            logger.error("risk_prediction_failed", error=str(e))
            return {"risk_level": "error", "probability": 0.0, "factors": {}}
    
    def forecast_umidade(self, history: List[float], steps: int = 7) -> Dict:
        """Forecast umidade using ARIMA"""
        try:
            # Convert to float to handle Decimal types from Oracle
            history_clean = [float(x) for x in history if x is not None]

            if len(history_clean) < 3:
                logger.warning("forecast_insufficient_data", count=len(history_clean))
                return {"predictions": [], "confidence_intervals": [], "alerts": []}

            # Fit ARIMA model
            model = ARIMA(history_clean, order=(1, 1, 1))
            fitted_model = model.fit()

            # Make forecast
            forecast = fitted_model.forecast(steps=steps)
            conf_int = fitted_model.get_forecast(steps=steps).conf_int()

            # Check for critical alerts
            alerts = []
            for i, value in enumerate(forecast):
                if value < 15.0:
                    alerts.append(f"Dia {i+1}: Umidade crítica prevista ({value:.1f}%)")

            return {
                "predictions": forecast.tolist(),
                "confidence_intervals": conf_int.tolist(),
                "alerts": alerts
            }
        except Exception as e:
            logger.error("forecast_failed", error=str(e))
            return {"predictions": [], "confidence_intervals": [], "alerts": []}
    
    def cluster_data(self, data: pd.DataFrame, n_clusters: int = 3) -> Dict:
        """Perform K-Means clustering"""
        try:
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            clusters = kmeans.fit_predict(data)
            
            # Get cluster centers
            centers = kmeans.cluster_centers_
            
            return {
                "clusters": clusters.tolist(),
                "centers": centers.tolist(),
                "inertia": float(kmeans.inertia_)
            }
        except Exception as e:
            logger.error("clustering_failed", error=str(e))
            return {"clusters": [], "centers": [], "inertia": 0.0}
    
    def train_model(self, model_type: str, X: np.ndarray, y: np.ndarray) -> Dict:
        """Train or retrain model"""
        try:
            if model_type == "risk_classifier":
                model = RandomForestClassifier(n_estimators=100, random_state=42)
            elif model_type == "regression":
                model = RandomForestRegressor(n_estimators=100, random_state=42)
            else:
                return {"success": False, "error": "Unknown model type"}
            
            model.fit(X, y)
            
            # Save model
            model_path = self.models_dir / f"{model_type}.joblib"
            joblib.dump(model, model_path)
            
            # Store in cache
            self.loaded_models[model_type] = model
            
            logger.info("model_trained", model_type=model_type)
            return {"success": True, "model_path": str(model_path)}
        except Exception as e:
            logger.error("model_training_failed", error=str(e))
            return {"success": False, "error": str(e)}
    
    def get_model_metrics(self, model_name: str) -> Dict:
        """Get model performance metrics"""
        model = self.load_model(model_name)
        
        if model is None:
            return {"error": "Model not found"}
        
        # Return basic metrics
        return {
            "model_name": model_name,
            "type": type(model).__name__,
            "loaded": True
        }
