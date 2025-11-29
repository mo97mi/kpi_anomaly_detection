from models.get_model import get_model
from data_sources.get_connector import get_connector
from shared.split_data import split_data
from shared.to_date import to_date
import pandas as pd


kpi_name = "kpi_a"


def train_kpi(kpi_name: str, save_flag: bool = False) -> None:
    """train and save

    Args:
        kpi_name (str): _description_

    Returns:
        bool: _description_
    """
    try:
        data_conn = get_connector(
            kpi_name,
        )
        data = data_conn.read(parse_dates=["DATE_H"])
        train, _ = split_data(
            data, to_date("14040320", "yyyymmdd", "persian"), "DATE_H"
        )
    except:
        raise Exception("the connection is out of access!")
    else:

        model = get_model(kpi_name)
        model.fit(train)

        if save_flag:
            model.save()


def main():
    train_kpi(kpi_name, True)
    # print(data.head())


if __name__ == "__main__":
    main()
