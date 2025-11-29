from abc import ABC, abstractmethod
from pandas import DataFrame


class BaseModel(ABC):
    """interface for models"""

    @abstractmethod
    def fit(
        self,
        input_data,
        date_col: str = "timestamp",
        value_col: str = "value",
    ):
        pass

    @abstractmethod
    def predict(
        self,
        input_data,
        date_col: str = "timestamp",
        value_col: str = "value",
    ) -> DataFrame:
        pass

    @abstractmethod
    def save(
        self,
    ):
        pass

    @abstractmethod
    def load(
        self,
    ):
        pass
