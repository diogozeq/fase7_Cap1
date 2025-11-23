"""
Create mock models for testing without requiring full ML dependencies
"""
import json
from pathlib import Path
from datetime import datetime

models_dir = Path("./models")
models_dir.mkdir(exist_ok=True)

print("🚀 Criando modelos mock para testes...")

# Create metadata files for each model
models_metadata = {
    "risk_classifier": {
        "model_name": "risk_classifier",
        "model_type": "RandomForestClassifier",
        "trained_date": datetime.now().isoformat(),
        "version": "1.0",
        "accuracy": 0.92,
        "n_estimators": 100,
        "features": ["umidade", "ph", "temperatura"],
        "target": "risk_level (0=low, 1=medium, 2=high)",
        "status": "mock"
    },
    "linear_regression": {
        "model_name": "linear_regression",
        "model_type": "LinearRegression",
        "trained_date": datetime.now().isoformat(),
        "version": "1.0",
        "r2_score": 0.75,
        "mae": 3.2,
        "rmse": 4.1,
        "training_time_seconds": 0.05,
        "features": ["ph", "temperatura"],
        "target": "umidade",
        "status": "mock"
    },
    "ridge_regression": {
        "model_name": "ridge_regression",
        "model_type": "Ridge",
        "trained_date": datetime.now().isoformat(),
        "version": "1.0",
        "r2_score": 0.76,
        "mae": 3.1,
        "rmse": 4.0,
        "training_time_seconds": 0.04,
        "features": ["ph", "temperatura"],
        "target": "umidade",
        "status": "mock"
    },
    "lasso_regression": {
        "model_name": "lasso_regression",
        "model_type": "Lasso",
        "trained_date": datetime.now().isoformat(),
        "version": "1.0",
        "r2_score": 0.74,
        "mae": 3.3,
        "rmse": 4.2,
        "training_time_seconds": 0.06,
        "features": ["ph", "temperatura"],
        "target": "umidade",
        "status": "mock"
    },
    "random_forest_regression": {
        "model_name": "random_forest_regression",
        "model_type": "RandomForestRegressor",
        "trained_date": datetime.now().isoformat(),
        "version": "1.0",
        "r2_score": 0.89,
        "mae": 2.1,
        "rmse": 2.8,
        "training_time_seconds": 1.2,
        "features": ["ph", "temperatura"],
        "target": "umidade",
        "status": "mock"
    },
    "gradient_boosting_regression": {
        "model_name": "gradient_boosting_regression",
        "model_type": "GradientBoostingRegressor",
        "trained_date": datetime.now().isoformat(),
        "version": "1.0",
        "r2_score": 0.91,
        "mae": 1.9,
        "rmse": 2.5,
        "training_time_seconds": 2.3,
        "features": ["ph", "temperatura"],
        "target": "umidade",
        "status": "mock"
    }
}

# Save metadata for each model
for model_name, metadata in models_metadata.items():
    metadata_path = models_dir / f"{model_name}_metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"✅ Criado: {metadata_path}")

# Create comparison CSV
import csv
comparison_path = models_dir / "regression_comparison.csv"
with open(comparison_path, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "model_name", "model_type", "r2_score", "mae", "rmse", "training_time_seconds"
    ])
    writer.writeheader()
    for model_name, metadata in models_metadata.items():
        if "r2_score" in metadata:
            writer.writerow({
                "model_name": metadata["model_name"],
                "model_type": metadata["model_type"],
                "r2_score": metadata["r2_score"],
                "mae": metadata["mae"],
                "rmse": metadata["rmse"],
                "training_time_seconds": metadata["training_time_seconds"]
            })

print(f"✅ Criado: {comparison_path}")
print("\n✨ Modelos mock criados com sucesso!")
print(f"📁 Localização: {models_dir.absolute()}")
