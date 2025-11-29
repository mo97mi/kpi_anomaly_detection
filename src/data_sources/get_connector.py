from data_sources.base_connector import BaseDataSource
from data_sources.csv_connector import CSVDataSource
from shared.config_loader import get_config
from shared.path_manager import PathManager


def get_connector(kpi_name) -> BaseDataSource:
    path_mgr = PathManager()
    config = get_config(kpi_name)

    data_type = config["data"]["data_type"]
    data_source = path_mgr.data_file(config["data"]["data_source"])

    if data_type == "csv":
        csv_conn = CSVDataSource(data_source)
        return csv_conn
    elif data_type == "oracle":
        return CSVDataSource("asghar")
    else:
        return CSVDataSource("asghar")


def main():
    print(get_connector("kpi_a").read().head())


if __name__ == "__main__":
    main()
