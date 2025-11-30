from shared.path_manager import PathManager
from logger.logger import get_logger
from .exceptions import KPINotFoundError


class KPIService:
    def __init__(self) -> None:
        self._path_mgr = PathManager()
        self._log = get_logger()

    def run_train(self, kpi_name: str):
        if self.kpi_exists(kpi_name):
            return self._log.debug("train starts")
        else:
            raise KPINotFoundError(f"kpi {kpi_name} does not exists")

    def kpi_exists(self, kpi_name: str):
        return self._path_mgr.dir_exists(f"kpis/{kpi_name}")


if __name__ == "__main__":
    try:
        KPIService().run_train("kpi_c")
    except KPINotFoundError as e:
        KPIService()._log.debug(e.args)
