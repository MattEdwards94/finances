import datetime

from budget import common

def parse_date(date_str: str) -> datetime.date:
    try:
        return datetime.datetime.strptime(date_str, '%d/%m/%Y').date()
    except Exception:
        try:
            return datetime.date.fromisoformat(date_str)
        except Exception:
            raise ValueError(f"Unable to parse date: {date_str}")

class RawTransaction:
    def __init__(self, raw_data: dict):
        self._raw = raw_data
        self._date = None
        self._amount = None
        for field in common.EXPECTED_RAW_FIELDS:
            if field not in raw_data:
                raise ValueError(f"Missing expected field: {field}")

    def __str__(self) -> str:
        return f"name={self.name():20s}, amount={self.amount():11,.2f}, date={self.date():%d-%m-%Y}, id={self.id()}"

    @property
    def name(self) -> str:
        return self._raw["Name"].strip()

    @property
    def id(self) -> str:
        return self._raw["Transaction ID"].strip()

    @property
    def date(self) -> datetime.date:
        if self._date is None:
            self._date = parse_date(self._raw["Date"].strip())
        return self._date

    @property
    def amount(self) -> float:
        if self._amount is None:
            try:
                self._amount = float(self._raw["Amount"].strip())
            except (ValueError, InvalidOperation):
                raise ValueError(f"Invalid amount: {self._raw['Amount']}")
        return self._amount

