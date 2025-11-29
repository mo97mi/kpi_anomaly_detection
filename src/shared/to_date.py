from abc import ABC, abstractmethod
from datetime import datetime
import jdatetime
from dateutil import parser


# Mapping between user format and Python's strptime format
FORMAT_MAP = {
    "YYYY": "%Y",
    "YY": "%y",
    "MM": "%m",
    # "M": "%m",
    "DD": "%d",
    "HH24": "%H",
    "MI": "%M",
    "SS": "%S",
}


def format_converter(user_format: str) -> str:
    """Parse date string using user-provided format like 'yyyy-mm-dd hh24:mi:ss'."""

    py_format = user_format.upper()

    # Replace user tokens with Python directives
    for k, v in FORMAT_MAP.items():
        py_format = py_format.replace(k, v)

    # Parse the string
    return py_format


class BaseConverter(ABC):
    @abstractmethod
    def to_date(self, str_date: str, str_format: str):
        print(f"original_format format: {str_format}")
        str_format = format_converter(str_format)
        print(f"converted format: {str_format}")
        return datetime.strptime(str_date, str_format)

    @abstractmethod
    def to_char(self, date: datetime, str_format: str) -> str:
        str_format = format_converter(str_format)
        print(str_format)
        return date.strftime(str_format)


class PersianConverter(BaseConverter):
    def to_date(self, str_date: str, str_format: str):
        str_format = format_converter(str_format)
        date = jdatetime.datetime.strptime(str_date, str_format).togregorian()
        return date

    def to_char(self, date: datetime, str_format: str) -> str:
        str_format = format_converter(str_format)
        str_date = jdatetime.datetime.fromgregorian(datetime=date)

        return jdatetime.datetime.strftime(str_date, str_format)


class GregorianConverter(BaseConverter):
    def to_date(self, str_date: str, str_format: str):
        print(f"original_format format: {str_format}")
        str_format = format_converter(str_format)
        print(f"converted format: {str_format}")
        return datetime.strptime(str_date, str_format)

    def to_char(self, date: datetime, str_format: str) -> str:
        str_format = format_converter(str_format)
        print(str_format)
        return date.strftime(str_format)


def get_converter(calendar: str) -> BaseConverter:
    calendar = calendar.lower()

    if calendar == "persian":
        return PersianConverter()
    elif calendar == "gregorian":
        return GregorianConverter()
    else:
        raise ValueError("calendar {calendar} is not supported")


def to_date(date: str, str_format: str, calendar: str = "gregorian"):
    converter = get_converter(calendar)
    return converter.to_date(date, str_format)


def to_char(date: datetime, str_format: str, calendar: str = "gregorian"):
    converter = get_converter(calendar)
    return converter.to_char(date, str_format)


def main():
    # date = PersianConverter().to_date("1404/05/25", format="%Y/%m/%d")
    # print(date)
    # print(f"type is: {type(date)}")
    # print(format_converter("1376/01/18 14:35:59"))
    # print(type(format_converter("1376/01/18 14:35:59")))
    # print(format_converter("16-08-2025 2:35 PM"))
    # print(format_converter("April 7, 1997"))
    # print(format_converter("yyyy/mm/dd"))

    # Examples
    # print(parse_date("25-08", "xy-mm"))  # 2025-08-01 00:00:00
    # print(parse_date("2025-08-16 14:35:59", "yyyy-mm-dd hh24:mi:ss"))
    # print(GregorianConverter().to_date("1404/5/25", "yyyy/m/dd"))
    # print(GregorianConverter().to_char(datetime.now(), "yyyy-mm-dd"))
    print(to_date("1404-05-25 16:39:39", "yyyy-mm-dd hh24:mi:ss", "persian"))
    print(to_char(datetime.now(), "yyyy-mm-dd hh24:mi:ss", "persian"))


if __name__ == "__main__":
    main()
