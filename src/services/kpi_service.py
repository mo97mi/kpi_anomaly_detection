from shared.path_manager import PathManager
from logger.logger import get_logger

path_mgr = PathManager()
log = get_logger()


def kpi_exists(kpi_name: str):
    return path_mgr.dir_exists(f"kpis/{kpi_name}")


def run_detection(kpi_name: str, data):
    if kpi_exists(kpi_name):
        pass


if __name__ == "__main__":
    log.debug(kpi_exists("kpi_a"))
