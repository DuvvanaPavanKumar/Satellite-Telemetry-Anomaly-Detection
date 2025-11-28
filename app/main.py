from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import joblib

app = FastAPI()

class Telemetry(BaseModel):
    timestamp: str
    values: dict

# Load model
print("🔄 Loading model...")
try:
    artifact = joblib.load("models/model.pkl")
    MODEL = artifact["model"]
    SCALER = artifact["scaler"]
    FEATURES = artifact["features"]
    print("✅ Model loaded successfully!")
except Exception as e:
    print("❌ ERROR loading model:", e)

@app.get("/")
def root():
    return {"message": "API working"}

@app.post("/predict")
def predict(data: Telemetry):
    try:
        print("\n📌 Incoming:", data.values)

        df = pd.DataFrame([data.values])
        print("📌 DF received:", df)

        df = df[FEATURES]
        print("📌 DF ordered:", df)

        X = SCALER.transform(df)

        pred = MODEL.predict(X)[0]
        score = MODEL.decision_function(X)[0]

        return {
            "anomaly": bool(pred == -1),   # <-- FIX 1
            "score": float(score)          # <-- FIX 2
        }

    except Exception as e:
        print("❌ BACKEND ERROR:", e)
        return {"error": str(e)}