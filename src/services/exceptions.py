class KPIError(Exception):
    """Base class for KPI-related domain errors."""

    pass


class KPINotFoundError(KPIError):
    """Raised when the requested KPI does not exist."""

    pass


class InvalidKPIDataError(KPIError):
    """Raised when KPI input data is invalid."""

    pass


if __name__ == "__main__":

    print(KPINotFoundError.args)
