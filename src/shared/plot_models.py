import plotly.graph_objects as go
import pandas as pd


def plot_forecast(
    df: pd.DataFrame,
    timestamp_col: str = "ds",
    value_col: str = "y",
    pred_col: str = "yhat",
    anomaly_col: str = "anomaly",
    upper_col: str = "yhat_upper",
    lower_col: str = "yhat_lower",
    title: str = "Forecast vs Actual",
):
    """
    Plot actual values, predicted values, anomalies, and forecast intervals interactively.

    Parameters
    ----------
    df : pd.DataFrame
        Data containing actual, predicted, anomaly flags, and bounds.
    timestamp_col : str
        Name of timestamp column.
    value_col : str
        Name of actual values column.
    pred_col : str
        Name of predicted values column.
    anomaly_col : str
        Name of anomaly flag column ([0,1] or [-1,0,1]).
    upper_col : str
        Name of upper bound column.
    lower_col : str
        Name of lower bound column.
    title : str, optional
        Plot title.
    """
    df.sort_values(by=timestamp_col, inplace=True)
    fig = go.Figure()

    # Actual values
    fig.add_trace(
        go.Scatter(
            x=df[timestamp_col],
            y=df[value_col],
            mode="lines",
            name="Actual",
            line=dict(color="blue"),
        )
    )

    # Predicted values
    fig.add_trace(
        go.Scatter(
            x=df[timestamp_col],
            y=df[pred_col],
            mode="lines",
            name="Predicted",
            line=dict(color="green", dash="dash"),
        )
    )

    # Confidence interval (grey band)
    fig.add_trace(
        go.Scatter(
            x=pd.concat([df[timestamp_col], df[timestamp_col][::-1]]),
            y=pd.concat([df[upper_col], df[lower_col][::-1]]),
            fill="toself",
            fillcolor="rgba(128,128,128,0.2)",
            line=dict(color="rgba(255,255,255,0)"),
            hoverinfo="skip",
            name="Confidence Interval",
        )
    )

    # Anomalies (red dots)
    anomaly_mask = df[anomaly_col].isin([1, -1])  # works for [0,1] or [-1,0,1]
    fig.add_trace(
        go.Scatter(
            x=df.loc[anomaly_mask, timestamp_col],
            y=df.loc[anomaly_mask, value_col],
            mode="markers",
            marker=dict(color="red", size=8, symbol="circle"),
            name="Anomaly",
        )
    )

    # Layout
    fig.update_layout(
        title=title,
        xaxis_title="Time",
        yaxis_title="Value",
        template="plotly_white",
        hovermode="x unified",
        legend=dict(x=0, y=1, bgcolor="rgba(255,255,255,0)"),
    )

    fig.show()
