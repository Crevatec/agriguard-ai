"""
AgriGuard AI - Crop Disease Model Trainer
Powered by Clevatec | Developed by Olakunle Sunday Olalekan

Trains a Random Forest classifier on synthetic but realistic
crop disease data and saves it as crop_model.pkl
"""

import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import json

np.random.seed(42)
N = 2000

# --- Feature generation ---
temp        = np.random.uniform(15, 40, N)        # °C
humidity    = np.random.uniform(30, 100, N)       # %
soil_ph     = np.random.uniform(4.5, 8.5, N)      # pH
rainfall    = np.random.uniform(0, 300, N)        # mm/month
wind_speed  = np.random.uniform(0, 30, N)         # km/h
leaf_wetness = np.random.uniform(0, 24, N)        # hours/day

# --- Label generation (rule-based to mimic agronomic reality) ---
# 0 = Healthy, 1 = Fungal Blight, 2 = Bacterial Wilt, 3 = Viral Mosaic

labels = []
for i in range(N):
    h = humidity[i]
    t = temp[i]
    lw = leaf_wetness[i]
    r = rainfall[i]
    ph = soil_ph[i]

    if h > 80 and lw > 12 and 20 <= t <= 32:
        disease = 1  # Fungal Blight  — warm, wet, humid
    elif t > 30 and r < 50 and ph < 5.5:
        disease = 2  # Bacterial Wilt — hot, dry, acidic soil
    elif wind_speed[i] > 20 and h < 55:
        disease = 3  # Viral Mosaic   — spread by wind/insects in dry conditions
    else:
        disease = 0  # Healthy
    labels.append(disease)

labels = np.array(labels)

X = np.column_stack([temp, humidity, soil_ph, rainfall, wind_speed, leaf_wetness])
y = labels

# --- Train / test split ---
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# --- Train model ---
model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
model.fit(X_train, y_train)

# --- Evaluate ---
y_pred = model.predict(X_test)
report = classification_report(y_test, y_pred,
    target_names=["Healthy", "Fungal Blight", "Bacterial Wilt", "Viral Mosaic"])
print("=== Model Evaluation ===")
print(report)

# --- Save model and metadata ---
joblib.dump(model, "/home/claude/crop_model.pkl")

metadata = {
    "model_type": "RandomForestClassifier",
    "features": ["temp", "humidity", "soil_ph", "rainfall", "wind_speed", "leaf_wetness"],
    "classes": {
        "0": "Healthy",
        "1": "Fungal Blight",
        "2": "Bacterial Wilt",
        "3": "Viral Mosaic"
    },
    "n_estimators": 100,
    "training_samples": N,
    "accuracy": float(model.score(X_test, y_test))
}

with open("/home/claude/model_metadata.json", "w") as f:
    json.dump(metadata, f, indent=2)

print(f"\n✅ Model saved: crop_model.pkl")
print(f"✅ Metadata saved: model_metadata.json")
print(f"✅ Test Accuracy: {metadata['accuracy']*100:.1f}%")