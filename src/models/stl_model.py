import pandas as pd
import numpy as np
from statsmodels.tsa.seasonal import MSTL, DecomposeResult
from statsmodels.tsa.arima.model import ARIMA
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from shared.to_date import to_date, to_char
from datetime import datetime


def split_data(
    df: pd.DataFrame, split_date: datetime, split_col: str = "timestamp"
) -> tuple[pd.DataFrame, pd.DataFrame]:
    df_mask = df[split_col] < split_date
    # print(f"mask is: {df_mask.head()}", f"mask not is: {~df_mask.head()}", sep="\n")
    train_data = df[df_mask]
    test_data = df[~df_mask]
    return train_data.copy(deep=True), test_data.copy(deep=True)


def train_stl_v1(df: pd.DataFrame, split_date: datetime) -> DecomposeResult:
    train_data, test_data = split_data(df, split_date)
    train_data.set_index("DATE_H", inplace=True)
    train_data.sort_index(inplace=True)

    model = MSTL(train_data["CNT"], periods=(7, 30, 365))
    result = model.fit()

    return result


def predict_stl_v1(): ...


def train_stl_6g():
    # 1. Load and prepare data
    df = pd.read_csv(
        "../data/6g_far_ord_v2_prophet_formatted_v2.csv", parse_dates=["DATE_"]
    )

    # df = df.set_index("DATE_H").asfreq("H")
    # df["CNT"] = df["CNT"].interpolate()  # fill missing hours if any

    # 2. Multi-Seasonal STL decomposition
    mstl = MSTL(df["CNT"], periods=[24, 24 * 7, 24 * 30, 24 * 365])
    res = mstl.fit()

    # 3. Fit ARIMA on residuals
    arima_model = ARIMA(res.resid, order=(1, 0, 1))
    arima_result = arima_model.fit()

    # 4. In-sample fitted values
    fitted_resid = arima_result.fittedvalues
    fitted_values = res.trend + res.seasonal.sum(axis=1) + fitted_resid

    # 5. Compute anomaly bounds (e.g., ±3 std from residuals)
    residual_error = df["CNT"] - fitted_values
    threshold = 4 * residual_error.std()
    df["anomaly"] = 0
    df.loc[residual_error > threshold, "anomaly"] = 1  # upper anomaly
    df.loc[residual_error < -threshold, "anomaly"] = -1  # lower anomaly

    # fig = res.plot()
    # plt.show()

    # 6. Create interactive Plotly chart
    fig = go.Figure()

    # Observed values
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["CNT"],
            mode="lines",
            name="Observed",
            line=dict(color="blue"),
        )
    )

    # Fitted values
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=fitted_values,
            mode="lines",
            name="Fitted",
            line=dict(color="orange"),
        )
    )

    # Upper anomalies
    fig.add_trace(
        go.Scatter(
            x=df.index[df["anomaly"] == 1],
            y=df["CNT"][df["anomaly"] == 1],
            mode="markers",
            name="Upper Anomaly",
            marker=dict(color="red", size=8, symbol="circle"),
        )
    )

    # Lower anomalies
    fig.add_trace(
        go.Scatter(
            x=df.index[df["anomaly"] == -1],
            y=df["CNT"][df["anomaly"] == -1],
            mode="markers",
            name="Lower Anomaly",
            marker=dict(color="green", size=8, symbol="circle"),
        )
    )

    fig.update_layout(
        title="STL + ARIMA Anomaly Detection",
        xaxis_title="Date",
        yaxis_title="Count",
        template="plotly_white",
        hovermode="x unified",
    )

    fig.show()


def stl_arima_anomaly(df, split_date, arima_order=(1, 0, 1), threshold_sigma=4):
    """
    STL + ARIMA anomaly detection pipeline.

    Args:
        df (pd.DataFrame): must contain columns ["DATE_H", "CNT"].
        split_date (str or pd.Timestamp): date to split train/test.
        arima_order (tuple): ARIMA(p,d,q) order for residual modeling.
        threshold_sigma (float): threshold multiplier for anomaly detection.

    Returns:
        pred_data (pd.DataFrame): prediction horizon with anomalies labeled.
        fig (plotly.graph_objects.Figure): interactive anomaly plot.
    """

    # Ensure datetime
    df = df.copy()
    df["DATE_H"] = pd.to_datetime(df["DATE_H"])

    # Split train/pred
    train_data = df[df["DATE_H"] < pd.to_datetime(split_date)]
    pred_data = df[df["DATE_H"] >= pd.to_datetime(split_date)].copy()

    # 1. STL decomposition on training data
    mstl = MSTL(train_data["CNT"], periods=[24, 24 * 7, 24 * 30, 24 * 365])
    res = mstl.fit()

    # 2. Fit ARIMA on residuals
    arima_model = ARIMA(res.resid, order=arima_order)
    arima_result = arima_model.fit()

    # 3. Forecast residuals into pred horizon
    n_forecast = len(pred_data)
    resid_forecast = arima_result.forecast(steps=n_forecast)

    # 4. Extend trend + seasonal
    trend_future = np.repeat(res.trend.iloc[-1], n_forecast)  # constant trend
    seasonal_sum = res.seasonal.sum(axis=1).values
    seasonal_future = np.tile(
        seasonal_sum, int(np.ceil(n_forecast / len(seasonal_sum)))
    )[:n_forecast]

    # 5. Build predictions
    fitted_future = trend_future + seasonal_future + resid_forecast.values

    # 6. Compute anomaly bounds
    residual_error = pred_data["CNT"].values - fitted_future
    threshold = threshold_sigma * residual_error.std()

    pred_data["fitted"] = fitted_future
    pred_data["anomaly"] = 0
    pred_data.loc[residual_error > threshold, "anomaly"] = 1
    pred_data.loc[residual_error < -threshold, "anomaly"] = -1

    # 7. Plot results
    fig = go.Figure()

    # Observed
    fig.add_trace(
        go.Scatter(
            x=pred_data["DATE_H"],
            y=pred_data["CNT"],
            mode="lines",
            name="Observed",
            line=dict(color="blue"),
        )
    )

    # Fitted
    fig.add_trace(
        go.Scatter(
            x=pred_data["DATE_H"],
            y=pred_data["fitted"],
            mode="lines",
            name="Fitted",
            line=dict(color="orange"),
        )
    )

    # Upper anomalies
    fig.add_trace(
        go.Scatter(
            x=pred_data.loc[pred_data["anomaly"] == 1, "DATE_H"],
            y=pred_data.loc[pred_data["anomaly"] == 1, "CNT"],
            mode="markers",
            name="Upper Anomaly",
            marker=dict(color="red", size=8, symbol="circle"),
        )
    )

    # Lower anomalies
    fig.add_trace(
        go.Scatter(
            x=pred_data.loc[pred_data["anomaly"] == -1, "DATE_H"],
            y=pred_data.loc[pred_data["anomaly"] == -1, "CNT"],
            mode="markers",
            name="Lower Anomaly",
            marker=dict(color="green", size=8, symbol="circle"),
        )
    )

    fig.update_layout(
        title="STL + ARIMA Anomaly Detection",
        xaxis_title="Date",
        yaxis_title="Count",
        template="plotly_white",
        hovermode="x unified",
    )

    return pred_data, fig


def main():
    df = pd.read_csv("../data/sim_activation.csv", parse_dates=["DATE_H"])
    result = train_stl_v1(df, to_date("1404-04-20", "yyyy-mm-dd", "persian"))
    # split_data(df, to_date("1404-04-20", "yyyy-mm-dd", "persian"))
    result.plot()
    plt.show()


if __name__ == "__main__":
    main()
    # df = pd.read_csv("../data/sim_activation.csv", parse_dates=["DATE_H"])
    # stl_arima_anomaly(df, to_date("1404-04-20", "yyyy-mm-dd", "persian"))
