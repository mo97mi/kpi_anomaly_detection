from models.base_model import BaseModel
from models.prophet_model import ProphetModel
from shared.config_loader import get_config
from shared.path_manager import PathManager


def get_model(kpi_name, **kwargs) -> BaseModel:
    path_mgr = PathManager()
    config = get_config(kpi_name)

    model_type = config["model"]["model"]

    if model_type == "prophet":
        model = ProphetModel(kpi_name=kpi_name, **kwargs)
        return model
    elif model_type == "something":
        return ProphetModel(kpi_name=kpi_name, **kwargs)
    else:
        return ProphetModel(kpi_name=kpi_name, **kwargs)


def main():
    model = get_model("kpi_a")
    print(type(model))


if __name__ == "__main__":
    main()
