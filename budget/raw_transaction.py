import datetime
from decimal import InvalidOperation

from budget import common

def parse_date(date_str: str) -> datetime.date:
    try:
        return datetime.datetime.strptime(date_str, '%d/%m/%Y').date()
    except ValueError:
        try:
            return datetime.date.fromisoformat(date_str)
        except ValueError as exc:
            raise ValueError(f"Unable to parse date: {date_str}") from exc

class RawTransaction:
    def __init__(self, raw_data: dict):
        self._raw = raw_data
        self._date = None
        self._amount = None
        for field in common.EXPECTED_RAW_FIELDS:
            if field not in raw_data:
                raise ValueError(f"Missing expected field: {field}")

    def __str__(self) -> str:
        return (f"name={self.name():20s}, amount={self.amount():11,.2f}, "
                f"date={self.date():%d-%m-%Y}, id={self.id()}")

    def __eq__(self, other) -> bool:
        if not isinstance(other, RawTransaction):
            return NotImplemented
        return self._raw == other._raw

    def to_dict(self) -> dict:
        return self._raw.copy()

    def id(self) -> str:
        return self._raw["Transaction ID"].strip()

    def date(self) -> datetime.date:
        if self._date is None:
            self._date = parse_date(self._raw["Date"].strip())
        return self._date

    def time(self):
        return self._raw["Time"].strip()

    def type(self):
        return self._raw["Type"].strip()

    def name(self) -> str:
        return self._raw["Name"].strip()

    def emoji(self) -> str:
        return self._raw["Emoji"].strip()

    def category(self) -> str:
        return self._raw["Category"].strip()

    def amount(self) -> float:
        if self._amount is None:
            try:
                self._amount = float(self._raw["Amount"].strip())
            except (ValueError, InvalidOperation) as exc:
                raise ValueError(f"Invalid amount: {self._raw['Amount']}") from exc
        return self._amount

    def currency(self) -> str:
        return self._raw["Currency"].strip()

    def local_amount(self) -> float:
        try:
            return float(self._raw["Local Amount"].strip())
        except (ValueError, InvalidOperation) as exc:
            raise ValueError(f"Invalid local amount: {self._raw['Local Amount']}") from exc

    def local_currency(self) -> str:
        return self._raw["Local Currency"].strip()

    def notes(self) -> str:
        return self._raw["Notes and #tags"].strip()

    def address(self) -> str:
        return self._raw["Address"].strip()

    def receipt(self) -> str:
        return self._raw["Receipt"].strip()

    def description(self) -> str:
        return self._raw["Description"].strip()

    def category_split(self) -> str:
        return self._raw["Category split"].strip()

    def money_out(self) -> float:
        try:
            return float(self._raw["Money out"].strip())
        except (ValueError, InvalidOperation) as exc:
            raise ValueError(f"Invalid money out: {self._raw['Money out']}") from exc

    def money_in(self) -> float:
        try:
            return float(self._raw["Money in"].strip())
        except (ValueError, InvalidOperation) as exc:
            raise ValueError(f"Invalid money in: {self._raw['Money in']}") from exc
