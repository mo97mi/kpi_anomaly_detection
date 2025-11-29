from shared.path_manager import PathManager
from shared.split_data import split_data
from shared.to_date import to_date
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from statsmodels.tsa.arima.model import ARIMA
from sklearn.ensemble import IsolationForest
import joblib


class HybridAnomalyDetector:
    def __init__(self, arima_order=(1, 0, 0), contamination=0.05, random_state=42):
        """Hybrid ARIMA + Isolation Forest anomaly detector."""
        self.arima_order = arima_order
        self.contamination = contamination
        self.random_state = random_state
        self.arima_model = None
        self.iforest_model = None

    def fit(self, df):
        """
        Fit ARIMA + Isolation Forest on training data.
        :param df: DataFrame with columns ['timestamp', 'value']
        """
        if not {"timestamp", "value"}.issubset(df.columns):
            raise ValueError("DataFrame must contain 'timestamp' and 'value' columns.")

        # Ensure timestamp is datetime and sorted
        df = df.copy()
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp").set_index("timestamp")

        # Train ARIMA on values
        arima = ARIMA(df["value"], order=self.arima_order)
        self.arima_model = arima.fit()

        # Compute residuals
        residuals = df["value"] - self.arima_model.fittedvalues

        # Train Isolation Forest on residuals
        self.iforest_model = IsolationForest(
            contamination=self.contamination, random_state=self.random_state
        )
        self.iforest_model.fit(residuals.values.reshape(-1, 1))

    def predict(self, timestamp=None, value=None, df=None) -> pd.DataFrame:
        """
        Predict anomaly status for:
          1. A single record (timestamp, value)
          2. A DataFrame with 'timestamp' and 'value' columns

        Returns:
          - dict (for single record)
          - DataFrame with expected, residual, anomaly (for batch)
        """
        if self.arima_model is None or self.iforest_model is None:
            raise ValueError(
                "Model not trained. Call fit() first or load a saved model."
            )

        # --- Case 1: single record ---
        if df is None:
            forecast = self.arima_model.predict(start=timestamp, end=timestamp)[0]
            residual = value - forecast
            is_anomaly = self.iforest_model.predict([[residual]])[0]
            is_anomaly = 1 if is_anomaly == -1 else 0

            return pd.DataFrame(
                {
                    "timestamp": timestamp,
                    "value": value,
                    "expected": forecast,
                    "residual": residual,
                    "anomaly": is_anomaly,
                }
            )

        # --- Case 2: batch dataframe ---
        else:
            if not {"timestamp", "value"}.issubset(df.columns):
                raise ValueError(
                    "DataFrame must contain 'timestamp' and 'value' columns."
                )

                """Predict anomalies for a given dataframe with timestamp, value"""
        # Copy and prepare
        df = df.copy()
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.set_index("timestamp")

        # Forecast for this df length
        start = 0
        end = len(df) - 1

        forecasts = self.arima_model.predict(start=start, end=end)

        # Align forecasts with df index
        forecasts.index = df.index

        # Residuals
        residuals = df["value"] - forecasts

        # Simple threshold rule
        mad = np.median(np.abs(residuals - np.median(residuals)))
        threshold = 3 * mad

        anomalies = (np.abs(residuals) > threshold).astype(int)

        # Return appended dataframe
        result = df.copy()
        result["forecast"] = forecasts
        result["residual"] = residuals
        result["anomaly"] = anomalies
        return result

    def save(self, path):
        """Save both models."""
        joblib.dump((self.arima_model, self.iforest_model), path)

    def load(self, path):
        """Load both models."""
        self.arima_model, self.iforest_model = joblib.load(path)

    def plot_results(
        self, df: pd.DataFrame, title: str = "Forecast vs Actual with Anomalies"
    ):
        """
        Plot actual values, forecasts, thresholds (as grey band), and anomalies with Plotly.

        Parameters
        ----------
        df : pd.DataFrame
            Dataframe must contain:
            - 'value' (actuals)
            - 'forecast' (predicted)
            - 'residual' (errors)
            - 'anomaly' (0/1 flag)
        title : str
            Title of the chart
        """
        fig = go.Figure()

        # Actual values
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["value"],
                mode="lines+markers",
                name="Actual",
                line=dict(color="blue"),
            )
        )

        # Forecast values
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["forecast"],
                mode="lines",
                name="Forecast",
                line=dict(color="green", dash="dash"),
            )
        )

        # Thresholds (MAD-based)
        mad = np.median(np.abs(df["residual"] - np.median(df["residual"])))
        threshold = 3 * mad if mad > 0 else 3 * df["residual"].std()

        upper = df["forecast"] + threshold
        lower = df["forecast"] - threshold

        # Grey shaded area for threshold band
        fig.add_trace(
            go.Scatter(
                x=list(df.index) + list(df.index[::-1]),
                y=list(upper) + list(lower[::-1]),
                fill="toself",
                fillcolor="rgba(128,128,128,0.2)",  # semi-transparent grey
                line=dict(color="rgba(255,255,255,0)"),  # no border line
                hoverinfo="skip",
                showlegend=True,
                name="Threshold Band",
            )
        )

        # Anomalies (red dots)
        anomalies = df[df["anomaly"] == 1]
        fig.add_trace(
            go.Scatter(
                x=anomalies.index,
                y=anomalies["value"],
                mode="markers",
                name="Anomalies",
                marker=dict(color="red", size=10, symbol="circle"),
            )
        )

        fig.update_layout(
            title=title,
            xaxis_title="Timestamp",
            yaxis_title="Value",
            template="plotly_white",
            legend=dict(x=0, y=1.1, orientation="h"),
        )

        fig.show()


def main():
    model = HybridAnomalyDetector()
    data = pd.read_csv(
        PathManager().data_file("sim_activation.csv"), parse_dates=["DATE_H"]
    )
    data.rename({"DATE_H": "timestamp", "CNT": "value"}, axis=1, inplace=True)
    train, test = split_data(data, to_date("1404-04-20", "yyyy-mm-dd", "persian"))
    # print(train.info())

    model.fit(train)
    result = model.predict(df=test)
    print(result.head())
    result.sort_index(inplace=True)
    model.plot_results(result)


if __name__ == "__main__":
    main()
