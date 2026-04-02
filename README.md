# 🌿 AgriGuard AI

> AI-powered crop disease detection, yield forecasting and fertilizer recommendation for smallholder farmers across Africa.

---

## What Is AgriGuard AI?

AgriGuard AI is a smart farming assistant that puts the knowledge of an agricultural expert in the hands of any farmer with a phone.

A farmer enters basic information about their farm — temperature, humidity, soil condition and crop type — and AgriGuard AI instantly answers three critical questions:

| Question | Endpoint |
|---|---|
| 🦠 Is my crop at risk of disease? | `POST /predict_disease` |
| 🌾 How much will I harvest this season? | `POST /predict_yield` |
| 💊 What fertilizer should I apply? | `POST /recommend_fertilizer` |

No agricultural degree needed. No expensive equipment. Just fast, accurate, actionable answers.

---

## The Problem It Solves

Every year across Africa, smallholder farmers lose 20–40% of their harvest to crop disease and poor soil management. Most cannot afford agronomists. Most live hours from the nearest agricultural office. AgriGuard AI bridges that gap — instantly, affordably, at scale.

---

## Project Structure

```
agriguard-ai/
├── frontend/
│   ├── app.html              # Industrial dashboard UI
│   ├── app.js                # Frontend logic & AI API calls
│   └── style.css             # Custom styles
├── backend/
│   ├── server.js             # Node.js entry point
│   ├── routes/               # API route definitions
│   ├── controllers/          # Business logic
│   └── middleware/           # JWT auth & error handling
├── ai-module/
│   ├── model_engine.py       # Flask API — 3 ML inference endpoints
│   ├── train_model.py        # Scikit-Learn model training scripts
│   ├── crop_model.pkl        # Trained disease classifier
│   ├── yield_model.pkl       # Trained yield regressor
│   ├── fertilizer_model.pkl  # Trained fertilizer classifier
│   └── *.json                # Model metadata files
├── database/
│   └── schema.sql            # PostgreSQL table definitions
└── README.md
```

---

## AI Models

| Model | Type | Task | Performance |
|---|---|---|---|
| Disease Detector | Random Forest Classifier | Detects Fungal Blight, Bacterial Wilt, Viral Mosaic | 98.8% accuracy |
| Yield Forecaster | Random Forest Regressor | Predicts harvest in kg/hectare | ±213 kg/ha MAE |
| Fertilizer Advisor | Random Forest Classifier | Recommends NPK, Urea, DAP, Potash or Organic/Lime | 100% accuracy |

---

## Getting Started

### Prerequisites
- Python 3.11+ 
- Node.js 18+
- PostgreSQL

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/agriguard-ai.git
cd agriguard-ai
```

### 2. Set up the AI Engine
```bash
cd ai-module
pip install flask flask-cors numpy scikit-learn joblib
python model_engine.py
```
Flask runs on `http://127.0.0.1:5001`

### 3. Open the Dashboard
Open `frontend/app.html` in your browser using Live Server (VS Code) or directly.

---

## API Reference

### POST `/predict_disease`
```json
{
  "temp": 28,
  "humidity": 85,
  "soil_ph": 6.2,
  "rainfall": 120,
  "wind_speed": 8,
  "leaf_wetness": 15
}
```
**Response:**
```json
{
  "disease": "Fungal Blight",
  "confidence": 0.97,
  "urgency": "High",
  "probabilities": { "Healthy": 0.01, "Fungal Blight": 0.97, ... }
}
```

---

### POST `/predict_yield`
```json
{
  "temp": 25,
  "humidity": 70,
  "soil_ph": 6.5,
  "rainfall": 150,
  "fertilizer_kg": 120,
  "sunlight_hrs": 9
}
```
**Response:**
```json
{
  "yield_kg_per_hectare": 5795.5,
  "rating": "Good",
  "advice": "Yields are good. Monitor for disease."
}
```

---

### POST `/recommend_fertilizer`
```json
{
  "crop_type": "Maize",
  "soil_ph": 5.2,
  "nitrogen": 20,
  "phosphorus": 30,
  "potassium": 50,
  "moisture": 40
}
```
**Response:**
```json
{
  "recommended_fertilizer": "Organic/Lime",
  "confidence": 1.0,
  "dosage_guide": "Apply 2-4 tonnes/ha of lime to correct acidity, then add organic compost.",
  "crop": "Maize"
}
```

---

## Roadmap

- [x] AI inference engine (Flask)
- [x] Disease prediction model
- [x] Yield forecasting model
- [x] Fertilizer recommendation model
- [x] Industrial dashboard UI
- [ ] Deploy to Render + Netlify
- [ ] WhatsApp bot integration
- [ ] USSD support for non-smartphone users
- [ ] Local language support (Igbo, Yoruba, Hausa)
- [ ] Crop photo disease detection (image upload)
- [ ] Farmer profile and history

---

## Tech Stack

| Layer | Technology |
|---|---|
| AI / ML | Python, Scikit-Learn, Flask |
| Frontend | HTML, Tailwind CSS, Chart.js |
| Backend | Node.js, Express |
| Database | PostgreSQL |
| Deployment | Render (API), Netlify (Frontend) |

---

## License

MIT License — free to use, modify and distribute.

---

## About

**Powered by Clevatec**
Developed by Olakunle Sunday Olalekan

> *"Every farmer deserves access to the same intelligence that large agribusinesses have. AgriGuard AI makes that possible."*
