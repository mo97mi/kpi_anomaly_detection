import pandas as pd
from sklearn.ensemble import IsolationForest
from shared.plotting import plot_kpi_anomalies
from data_sources.get_connector import get_connector


import pandas as pd
from sklearn.ensemble import IsolationForest


def isolation_forest_anomaly_features(df: pd.DataFrame):
    """
    Isolation Forest anomaly detection with feature engineering.
    Features: raw CNT, lag values, rolling stats, time features.

    Parameters
    ----------
    df : pd.DataFrame
        Must have columns: DATE_H (datetime), CNT (numeric KPI).

    Returns
    -------
    pd.DataFrame
        With added columns:
        - features used for training
        - anomaly (-1 = anomaly, 1 = normal)
        - score (anomaly score)
    """
    df = df.copy()
    df["DATE_H"] = pd.to_datetime(df["DATE_H"])
    df = df.sort_values("DATE_H").reset_index(drop=True)

    # Calendar features
    df["hour"] = df["DATE_H"].dt.hour
    df["dow"] = df["DATE_H"].dt.dayofweek

    # Lag features
    df["lag1"] = df["CNT"].shift(1)
    df["lag24"] = df["CNT"].shift(24)

    # Rolling statistics
    df["roll_mean_24"] = df["CNT"].rolling(24).mean()
    df["roll_std_24"] = df["CNT"].rolling(24).std()

    # Drop first few rows with NaNs
    df = df.dropna().reset_index(drop=True)

    # Train/test split
    split_idx = len(df) // 2
    df.loc[:split_idx, "set"] = "train"
    df.loc[split_idx + 1 :, "set"] = "test"

    # Features for model
    feature_cols = [
        "CNT",
        "lag1",
        "lag24",
        "roll_mean_24",
        "roll_std_24",
        "hour",
        "dow",
    ]
    train_data = df.loc[df["set"] == "train", feature_cols]
    test_data = df.loc[df["set"] == "test", feature_cols]

    # Train Isolation Forest
    model = IsolationForest(contamination=0.05, random_state=42)
    model.fit(train_data)

    # Predict on test set
    df.loc[df["set"] == "test", "anomaly"] = model.predict(test_data)
    df.loc[df["set"] == "test", "score"] = model.decision_function(test_data)

    return df


def main():
    # Example
    conn = get_connector("kpi_a")
    df = conn.read()
    print(df.head())
    result = isolation_forest_anomaly_features(df)  # my_df must have DATE_H, CNT
    plot_kpi_anomalies(result)


if __name__ == "__main__":
    main()
