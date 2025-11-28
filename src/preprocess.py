import pandas as pd
import os

def preprocess(input_csv="data/sample_telemetry.csv",
               output_csv="data/preprocessed.csv",
               window="60s"):

    df = pd.read_csv(input_csv, parse_dates=["timestamp"])
    df = df.sort_values("timestamp")

    df = df.set_index("timestamp")
    cols = df.columns

    for c in cols:
        df[f"{c}_roll_mean"] = df[c].rolling(window).mean()
        df[f"{c}_roll_std"] = df[c].rolling(window).std()
        df[f"{c}_delta"] = df[c].diff(1)

    df = df.dropna().reset_index()
    os.makedirs("data", exist_ok=True)
    df.to_csv(output_csv, index=False)

    print(f"✅ Preprocessed dataset saved to {output_csv}")

if __name__ == "__main__":
    preprocess()
