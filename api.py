from fastapi import FastAPI
import joblib
import pandas as pd

app = FastAPI()

# Load model, scaler, features
model_data = joblib.load("models/model.pkl")
model = model_data["model"]
scaler = model_data["scaler"]
features = model_data["features"]

@app.get("/")
def home():
    return {"message": "API is running!"}

@app.post("/predict")
def predict(payload: dict):
    # UI sends: {"timestamp": "...", "values": {...}}
    sensor_values = payload.get("values", {})

    # Convert to DataFrame
    df = pd.DataFrame([sensor_values])

    # Scale only the 4 features
    X = scaler.transform(df[features])

    # Predict
    pred = model.predict(X)[0]         # -1 = anomaly, 1 = normal
    score = model.decision_function(X)[0]  # anomaly score

    return {
        "anomaly": True if pred == -1 else False,
        "score": float(score)
    }