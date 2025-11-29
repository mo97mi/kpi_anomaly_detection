from sys import exception
from prophet import Prophet
from prophet.plot import plot_weekly
import pandas as pd
import matplotlib.pyplot as plt
import joblib
import shutil
from datetime import datetime
from models.base_model import BaseModel
from shared.path_manager import PathManager
from data_sources.get_connector import get_connector
from shared.split_data import split_data
from shared.to_date import to_date
from shared.plot_models import plot_forecast as mplot
from shared.fill_range import fill_range
from logger.logger import get_logger
import os
from logger.logger import get_logger


log = get_logger()


class ProphetModel(BaseModel):
    def __init__(self, kpi_name, **kwargs) -> None:
        self.model = Prophet(**kwargs)
        self._kpi_name: str = kpi_name

    def fit(
        self,
        input_data,
        date_col: str = "timestamp",
        value_col: str = "value",
    ):

        data = self._pre_process(input_data, date_col=date_col, value_col=value_col)
        log.info("data processed for training.")
        self.model.add_country_holidays("IR")
        log.info("country holidays added to the model")
        self.model.fit(data)
        log.warning("model fitted!")

    def predict_v1(
        self,
        input_data,
        date_col: str = "timestamp",
        value_col: str = "value",
    ) -> pd.DataFrame:
        data = self._pre_process(input_data, date_col=date_col, value_col=value_col)
        forecast = self.model.predict(data)
        data["yhat"] = forecast["yhat"].clip(lower=0)
        data["yhat_lower"] = forecast["yhat_lower"].clip(lower=0)
        data["yhat_upper"] = forecast["yhat_upper"].clip(lower=0)

        data["anomaly"] = 0
        data.loc[data["y"] > (data["yhat_upper"] * 1), "anomaly"] = (
            1  # Positive anomaly
        )
        data.loc[data["y"] < (data["yhat_lower"] / 1), "anomaly"] = (
            -1
        )  # Negative anomaly

        return data

    def predict(
        self,
        input_data: pd.DataFrame,
        date_col: str = "timestamp",
        value_col: str = "value",
    ) -> pd.DataFrame:
        data = self._pre_process(input_data, date_col=date_col, value_col=value_col)
        log.info("data processed for predicting.")

        forecast = self.model.predict(data)
        data["yhat"] = forecast["yhat"].clip(lower=0)
        data["yhat_lower"] = forecast["yhat_lower"].clip(lower=0)
        data["yhat_upper"] = forecast["yhat_upper"].clip(lower=0)
        data["residual"] = data["y"] - forecast["yhat"].clip(lower=0)

        data["hour"] = data["ds"].dt.hour
        data["date"] = data["ds"].dt.date

        N = 10
        anomalies = []

        for idx, row in data.iterrows():
            hour = row["hour"]
            date = row["date"]

            # Get same-hour values from past N days
            mask = (data["hour"] == hour) & (data["date"] < date)
            past_values: pd.Series = data["residual"].loc[mask].tail(N)

            if len(past_values) >= 3:  # need enough data
                mean = past_values.mean()
                std = past_values.std()

                z_score = (row["residual"] - mean) / std if std > 0 else 0
                anomalies.append(1 if abs(z_score) > 2.5 else 0)  # threshold
            else:
                anomalies.append(0)

        data["anomaly"] = anomalies
        log.info("prediction completed.")
        return data

    def _pre_process(
        self,
        data: pd.DataFrame,
        date_col: str,
        value_col: str,
    ) -> pd.DataFrame:
        data = fill_range(data)
        data[date_col] = pd.to_datetime(data[date_col], format="%Y-%m-%d %H:%M:%S")
        data.rename(columns={date_col: "ds", value_col: "y"}, inplace=True)
        data.sort_values(by="ds", inplace=True)
        data.reset_index(inplace=True, drop=True)
        return data

    def save(
        self,
    ) -> None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_name = f"model_{timestamp}.pkl"
        model_dir = PathManager().kpi_path(self._kpi_name) / "prophet" / model_name

        joblib.dump(self.model, model_dir)
        shutil.copy(model_dir, model_dir.parent / "model_latest.pkl")
        log.info(f"model saved in {model_dir}")

    def load(
        self,
    ):
        model_path = (
            PathManager().kpi_path(self._kpi_name) / "prophet" / "model_latest.pkl"
        )
        try:
            model = joblib.load(model_path)
            self.model = model
            log.info("model loaded successfully")

        except exception as e:
            log.exception("failed to load model!")

    def get_model(self):
        return self.model

    def tune_model(self):
        # Add custom daily (24-hour) seasonality
        self.model.add_seasonality(
            name="hourly_daily_pattern",
            period=1,
            fourier_order=10,
        )


def main():
    model = ProphetModel(weekly_seasonality=100, kpi_name="sim_activation")

    data_path = PathManager().data_file("sim_activation.csv")
    data = pd.read_csv(data_path, parse_dates=["DATE_H"])

    train, test = split_data(
        data, to_date("1404-03-20", "yyyy-mm-dd", "persian"), "DATE_H"
    )
    model.fit(train)


if __name__ == "__main__":
    main()
