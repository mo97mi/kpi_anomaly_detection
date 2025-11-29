import pandas as pd
from data_sources.base_connector import BaseDataSource


class CSVDataSource(BaseDataSource):
    def __init__(self, data_path) -> None:
        self.__data_path = data_path

    def read(self, parse_dates: list = []) -> pd.DataFrame:
        data = pd.read_csv(self.__data_path, parse_dates=parse_dates)
        return data

    def get_data_path(self):
        return self.__data_path


def main():
    csv_obj = CSVDataSource("../data/data_v1.csv")
    data = csv_obj.read()
    print(data.head())


if __name__ == "__main__":
    main()
