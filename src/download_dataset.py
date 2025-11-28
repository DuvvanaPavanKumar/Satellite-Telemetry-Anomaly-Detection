import pandas as pd
import numpy as np
import os

def generate_satellite_telemetry(out_path="data/sample_telemetry.csv"):
    os.makedirs("data", exist_ok=True)

    print("⏳ Generating dataset...")

    rng = pd.date_range("2025-01-01", periods=20000, freq="S")

    df = pd.DataFrame({
        "timestamp": rng,
        "battery_temp": 30 + 2*np.sin(np.arange(len(rng))/300) + np.random.normal(0,0.3,len(rng)),
        "solar_power": 7 + 0.5*np.sin(np.arange(len(rng))/200) + np.random.normal(0,0.1,len(rng)),
        "gyro_x": np.random.normal(0,0.05,len(rng)),
        "fuel_pressure": 150 + np.random.normal(0,0.4,len(rng)),
    })

    anomaly_idx = np.random.choice(len(df), size=20, replace=False)
    df.loc[anomaly_idx, "battery_temp"] += np.random.uniform(20, 60, size=len(anomaly_idx))
    df.loc[anomaly_idx, "solar_power"] -= np.random.uniform(2, 6, size=len(anomaly_idx))
    df.loc[anomaly_idx, "gyro_x"] += np.random.uniform(3, 8, size=len(anomaly_idx))

    df.to_csv(out_path, index=False)
    print(f"✅ Dataset saved to {out_path}")


if __name__ == "__main__":
    generate_satellite_telemetry()
