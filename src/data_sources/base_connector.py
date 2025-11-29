from abc import ABC, abstractmethod
from pandas import DataFrame


class BaseDataSource(ABC):
    @abstractmethod
    def read(self, parse_dates: list = []) -> DataFrame:
        """Read data and return as a DataFrame."""
        pass
