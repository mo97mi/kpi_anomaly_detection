from models.get_model import get_model
from data_sources.get_connector import get_connector
from shared.split_data import split_data
from shared.to_date import to_date
import pandas as pd
from shared.plot_models import plot_forecast

kpi_name = "voice_400_min"


def predict_kpi(
    kpi_name: str,
    input_data: pd.DataFrame,
    plot_flag: bool = False,
):
    model = get_model(kpi_name)
    model.load()
    forecast = model.predict(input_data)

    if plot_flag:
        plot_forecast(forecast, title=kpi_name)


def main():
    conn = get_connector(kpi_name)
    data = conn.read(parse_dates=["DATE_H"])
    _, test = split_data(
        data, split_col="DATE_H", split_date=to_date("14040601", "yyyymmdd", "persian")
    )
    predict_kpi(kpi_name, test, True)


if __name__ == "__main__":
    main()
