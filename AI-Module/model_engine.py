"""
AgriGuard AI Engine
Powered by Clevatec
Developed by Olakunle Sunday Olalekan
"""

from flask import Flask, request, jsonify
from flask_cors import CORS    
import numpy as np
import joblib
import json
import os

app = Flask(__name__)
CORS(app)   

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load(pkl, meta):
    m = joblib.load(os.path.join(BASE_DIR, pkl))
    with open(os.path.join(BASE_DIR, meta)) as f:
        md = json.load(f)
    return m, md

disease_model,    disease_meta    = load("crop_model.pkl",        "model_metadata.json")
yield_model,      yield_meta      = load("yield_model.pkl",        "yield_metadata.json")
fertilizer_model, fertilizer_meta = load("fertilizer_model.pkl",  "fertilizer_metadata.json")

DISEASE_CLASSES  = disease_meta["classes"]
FERT_CLASSES     = fertilizer_meta["classes"]
CROP_TYPES       = fertilizer_meta["crop_types"]

URGENCY_MAP = {
    "Healthy": "None", "Fungal Blight": "High",
    "Bacterial Wilt": "Critical", "Viral Mosaic": "Medium"
}

FERT_DOSAGE = {
    "NPK":          "Apply 200-300 kg/ha of NPK (15:15:15) at planting.",
    "Urea":         "Apply 100-150 kg/ha of Urea; split into 2 applications.",
    "DAP":          "Apply 100 kg/ha of DAP at planting for phosphorus boost.",
    "Potash":       "Apply 60-90 kg/ha of MOP (Muriate of Potash).",
    "Organic/Lime": "Apply 2-4 tonnes/ha of lime to correct acidity, then add organic compost."
}

@app.route('/')
def home():
    return jsonify({
        "engine": "AgriGuard AI", "powered_by": "Clevatec",
        "endpoints": ["/predict_disease", "/predict_yield", "/recommend_fertilizer", "/model_info"]
    })

@app.route('/predict_disease', methods=['POST'])
def predict_disease():
    data = request.get_json()
    try:
        features = np.array([[
            float(data['temp']), float(data['humidity']),
            float(data.get('soil_ph', 6.5)), float(data.get('rainfall', 100)),
            float(data.get('wind_speed', 10)), float(data.get('leaf_wetness', 8))
        ]])
        pred_class = int(disease_model.predict(features)[0])
        pred_proba = disease_model.predict_proba(features)[0]
        disease    = DISEASE_CLASSES[str(pred_class)]
        return jsonify({
            "disease": disease, "confidence": round(float(pred_proba[pred_class]), 2),
            "urgency": URGENCY_MAP.get(disease, "Normal"),
            "probabilities": {DISEASE_CLASSES[str(i)]: round(float(p), 2) for i, p in enumerate(pred_proba)}
        }), 200
    except KeyError as e:
        return jsonify({"error": f"Missing field: {e}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/predict_yield', methods=['POST'])
def predict_yield():
    data = request.get_json()
    try:
        features = np.array([[
            float(data['temp']), float(data['humidity']),
            float(data.get('soil_ph', 6.5)), float(data['rainfall']),
            float(data['fertilizer_kg']), float(data.get('sunlight_hrs', 8))
        ]])
        predicted = round(float(np.clip(yield_model.predict(features)[0], 500, 12000)), 1)
        rating = "Excellent" if predicted >= 8000 else "Good" if predicted >= 5000 else "Fair" if predicted >= 3000 else "Poor"
        advice = ("Conditions are optimal." if rating == "Excellent"
                  else "Consider increasing fertilizer or improving irrigation." if rating in ("Fair","Poor")
                  else "Yields are good. Monitor for disease.")
        return jsonify({"yield_kg_per_hectare": predicted, "rating": rating, "advice": advice}), 200
    except KeyError as e:
        return jsonify({"error": f"Missing field: {e}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/recommend_fertilizer', methods=['POST'])
def recommend_fertilizer():
    data = request.get_json()
    try:
        crop_input = data.get('crop_type', 'Maize')
        if isinstance(crop_input, str):
            crop_map_inv = {v.lower(): k for k, v in CROP_TYPES.items()}
            crop_id = int(crop_map_inv.get(crop_input.lower(), 0))
        else:
            crop_id = int(crop_input)
        features = np.array([[
            float(data['soil_ph']), float(data['nitrogen']),
            float(data['phosphorus']), float(data['potassium']),
            crop_id, float(data.get('moisture', 40))
        ]])
        pred_class = int(fertilizer_model.predict(features)[0])
        pred_proba = fertilizer_model.predict_proba(features)[0]
        fert_name  = FERT_CLASSES[str(pred_class)]
        return jsonify({
            "recommended_fertilizer": fert_name,
            "confidence": round(float(pred_proba[pred_class]), 2),
            "dosage_guide": FERT_DOSAGE[fert_name],
            "crop": CROP_TYPES.get(str(crop_id), "Unknown"),
            "probabilities": {FERT_CLASSES[str(i)]: round(float(p), 2) for i, p in enumerate(pred_proba)}
        }), 200
    except KeyError as e:
        return jsonify({"error": f"Missing field: {e}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/model_info', methods=['GET'])
def model_info():
    return jsonify({"disease_model": disease_meta, "yield_model": yield_meta, "fertilizer_model": fertilizer_meta}), 200

if __name__ == '__main__':
    app.run(port=5001)