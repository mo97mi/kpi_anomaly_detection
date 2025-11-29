from datetime import datetime
import jdatetime
from abc import ABC, abstractmethod


# ===== Interfaces =====
class CalendarConverter(ABC):
    """Interface for all calendar converters"""

    @abstractmethod
    def to_gregorian(self, date_obj: datetime) -> datetime:
        pass

    @abstractmethod
    def from_string(self, date_str: str, date_format: str) -> datetime:
        pass


# ===== Converters =====
class GregorianConverter(CalendarConverter):
    """Gregorian date converter implementation"""

    def to_gregorian(self, date_obj: datetime) -> datetime:
        return date_obj  # Already Gregorian

    def from_string(self, date_str: str, date_format: str) -> datetime:
        return datetime.strptime(date_str, date_format)


class JalaliConverter(CalendarConverter):
    """Jalali date converter implementation"""

    def to_gregorian(self, date_obj: datetime) -> datetime:
        # date_obj here should be a jdatetime.date or jdatetime.datetime
        g_date = date_obj.togregorian()
        return datetime(g_date.year, g_date.month, g_date.day)

    def from_string(self, date_str: str, date_format: str) -> datetime:
        j_date = jdatetime.datetime.strptime(date_str, date_format)
        g_date = j_date.togregorian()
        return datetime(g_date.year, g_date.month, g_date.day)


# ===== Factory =====
class CalendarFactory:
    """Factory to get appropriate calendar converter"""

    @staticmethod
    def get_converter(calendar_type: str) -> CalendarConverter:
        calendar_type = calendar_type.lower()
        if calendar_type in ["gregorian", "miladi"]:
            return GregorianConverter()
        elif calendar_type in ["jalali", "shamsi"]:
            return JalaliConverter()
        else:
            raise ValueError(f"Unknown calendar type: {calendar_type}")


# ===== Facade =====
class DateFacade:
    """Facade for converting and parsing dates"""

    @staticmethod
    def to_date(date_str: str, date_format: str, calendar_type: str) -> datetime:
        converter = CalendarFactory.get_converter(calendar_type)
        date_obj = converter.from_string(date_str, date_format)
        return converter.to_gregorian(date_obj)


# ===== Public API =====
def to_date(date_str: str, date_format: str, calendar_type: str) -> datetime:
    """
    Converts a date string from a specific calendar to Python datetime (Gregorian).
    :param date_str: Date string
    :param date_format: Format of the date string
    :param calendar_type: 'gregorian'/'miladi' or 'jalali'/'shamsi'
    :return: datetime object (Gregorian)
    """
    return DateFacade.to_date(date_str, date_format, calendar_type)


# ===== Example Usage =====
if __name__ == "__main__":
    # Jalali to Gregorian
    print(to_date("1403-05-23", "%Y-%m-%d", "shamsi"))
    # Gregorian to Gregorian
    print(to_date("2024-08-14", "%Y-%m-%d", "gregorian"))

    print("hello")
