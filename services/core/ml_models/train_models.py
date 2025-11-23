"""
Script to train and serialize ML models
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score, r2_score, mean_absolute_error, mean_squared_error
import joblib
from pathlib import Path
from datetime import datetime
import json

# Create models directory
models_dir = Path("./models")
models_dir.mkdir(exist_ok=True)

print("🚀 Iniciando treinamento de modelos ML...")

# Generate synthetic training data for risk classification
print("\n📊 Gerando dados sintéticos para treinamento...")
np.random.seed(42)
n_samples = 1000

# Features: umidade, ph, temperatura
umidade = np.random.uniform(5, 50, n_samples)
ph = np.random.uniform(4.0, 8.0, n_samples)
temperatura = np.random.uniform(15, 40, n_samples)

X = np.column_stack([umidade, ph, temperatura])

# Target: risk level (0=low, 1=medium, 2=high)
# High risk: umidade < 15 or pH < 4.5 or pH > 7.5
# Medium risk: umidade < 20 or pH < 5.0 or pH > 7.0
# Low risk: otherwise
y = np.zeros(n_samples, dtype=int)
for i in range(n_samples):
    if umidade[i] < 15 or ph[i] < 4.5 or ph[i] > 7.5:
        y[i] = 2  # high risk
    elif umidade[i] < 20 or ph[i] < 5.0 or ph[i] > 7.0:
        y[i] = 1  # medium risk
    else:
        y[i] = 0  # low risk

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 1. Train RandomForest Classifier for risk prediction
print("\n🌲 Treinando RandomForestClassifier para predição de risco...")
rf_classifier = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    random_state=42,
    n_jobs=-1
)
rf_classifier.fit(X_train, y_train)

# Evaluate
y_pred = rf_classifier.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"   ✅ Acurácia: {accuracy:.2%}")

# Save model with metadata
model_path = models_dir / "risk_classifier.joblib"
joblib.dump(rf_classifier, model_path)

metadata = {
    "model_name": "risk_classifier",
    "model_type": "RandomForestClassifier",
    "trained_date": datetime.now().isoformat(),
    "version": "1.0",
    "accuracy": float(accuracy),
    "n_estimators": 100,
    "features": ["umidade", "ph", "temperatura"],
    "target": "risk_level (0=low, 1=medium, 2=high)"
}

with open(models_dir / "risk_classifier_metadata.json", "w") as f:
    json.dump(metadata, f, indent=2)

print(f"   💾 Modelo salvo em: {model_path}")

# 2. Train regression models for comparison
print("\n📈 Treinando modelos de regressão...")

# Generate regression data (predict umidade based on other factors)
y_reg = umidade + np.random.normal(0, 2, n_samples)
X_reg = np.column_stack([ph, temperatura])
X_reg_train, X_reg_test, y_reg_train, y_reg_test = train_test_split(
    X_reg, y_reg, test_size=0.2, random_state=42
)

regression_models = {
    "linear_regression": LinearRegression(),
    "ridge_regression": Ridge(alpha=1.0),
    "lasso_regression": Lasso(alpha=1.0),
    "random_forest_regression": RandomForestRegressor(n_estimators=100, random_state=42),
    "gradient_boosting_regression": GradientBoostingRegressor(n_estimators=100, random_state=42)
}

regression_results = []

for name, model in regression_models.items():
    print(f"\n   🔧 Treinando {name}...")
    
    # Train
    start_time = datetime.now()
    model.fit(X_reg_train, y_reg_train)
    training_time = (datetime.now() - start_time).total_seconds()
    
    # Evaluate
    y_pred_reg = model.predict(X_reg_test)
    r2 = r2_score(y_reg_test, y_pred_reg)
    mae = mean_absolute_error(y_reg_test, y_pred_reg)
    rmse = np.sqrt(mean_squared_error(y_reg_test, y_pred_reg))
    
    print(f"      R²: {r2:.4f}")
    print(f"      MAE: {mae:.4f}")
    print(f"      RMSE: {rmse:.4f}")
    print(f"      Tempo: {training_time:.2f}s")
    
    # Save model
    model_path = models_dir / f"{name}.joblib"
    joblib.dump(model, model_path)
    
    # Save metadata
    metadata = {
        "model_name": name,
        "model_type": type(model).__name__,
        "trained_date": datetime.now().isoformat(),
        "version": "1.0",
        "r2_score": float(r2),
        "mae": float(mae),
        "rmse": float(rmse),
        "training_time_seconds": float(training_time),
        "features": ["ph", "temperatura"],
        "target": "umidade"
    }
    
    with open(models_dir / f"{name}_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    
    regression_results.append(metadata)
    print(f"      💾 Salvo em: {model_path}")

# Save comparison results
comparison_df = pd.DataFrame(regression_results)
comparison_df.to_csv(models_dir / "regression_comparison.csv", index=False)

print("\n" + "="*60)
print("✨ Treinamento concluído com sucesso!")
print("="*60)
print(f"\n📁 Modelos salvos em: {models_dir.absolute()}")
print(f"\n📊 Modelos treinados:")
print(f"   • risk_classifier (RandomForest)")
print(f"   • linear_regression")
print(f"   • ridge_regression")
print(f"   • lasso_regression")
print(f"   • random_forest_regression")
print(f"   • gradient_boosting_regression")
print(f"\n📈 Comparação de modelos salva em: regression_comparison.csv")
