from os.path import join
from sys import exception
from yaml import safe_load
from shared.path_manager import PathManager
from logger.logger import get_logger

log = get_logger()


def get_config(
    kpi_name: str,
):
    config_path = PathManager().kpi_config(kpi_name)
    try:
        with open(config_path) as file:

            try:
                config = safe_load(file)
                log.info(f"{kpi_name} config loaded successfully")
            except exception as e:
                log.exception(
                    f"some error occured when safe loading the {kpi_name} config"
                )
                raise e
            return config

    except exception as e:
        log.exception(f"some error occured while loading the {kpi_name} config.")


def main():
    print(f"config loader dir is: {get_config('kpi_a')}")


if __name__ == "__main__":
    main()
