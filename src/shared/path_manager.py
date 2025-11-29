from pathlib import Path
from os.path import join


class PathManager:
    def __init__(self, env: str = "dev"):
        """
        Path Manager for handling environment-specific paths.

        :param env: Environment name (e.g., dev, prod, test)
        """
        self.env = env

        # Define base directories for environments
        self.base_dirs = {
            "dev": Path(__file__).resolve().parent.parent,  # Project root for dev
            "prod": Path("/opt/project"),  # Example prod path
            "test": Path("/tmp/project"),  # Example test path
        }

        self._base_dir = self.base_dirs.get(env, self.base_dirs["dev"])

    # ---- Core Directories ---- #
    @property
    def base_dir(self) -> Path:
        return self._base_dir

    @property
    def data_dir(self):
        return self.base_dir.parent / "data"

    @property
    def data_sources_dir(self):
        return self.base_dir / "data_sources"

    @property
    def shared_dir(self):
        return self.base_dir / "shared"

    @property
    def kpi_dir(self) -> Path:
        return self.base_dir / "kpis"

    @property
    def log_dir(self) -> Path:
        return self.base_dir / "logs"

    def kpi_path(self, kpi_name: str) -> Path:
        return self.kpi_dir / kpi_name

    def models_dir(self, model_name: str = ""):
        return self.base_dir / "models" / model_name

    # ---- File Getters ---- #
    def data_file(self, filename: str):
        return self.data_dir / filename

    def model_file(self, model_name: str, filename: str):
        return self.models_dir() / model_name / filename

    def kpi_config(
        self,
        kpi_name: str,
        config_name: str = "config.yaml",
    ):
        return self.kpi_path(kpi_name) / config_name

    # ---- Generic Getter ---- #
    def get(self, *subdirs):
        return self.base_dir.joinpath(*subdirs)


def main():
    path = PathManager()
    print(path.kpi_config("sim_acitvation"))


if __name__ == "__main__":
    main()
