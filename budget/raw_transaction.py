from dataclasses import dataclass
import datetime
from decimal import Decimal, InvalidOperation
from typing import Optional

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
        expected_fields = [
            "Transaction ID",
            "Date",
            "Time",
            "Type",
            "Name",
            "Emoji",
            "Category",
            "Amount",
            "Currency",
            "Local amount",
            "Local currency",
            "Notes and #tags",
            "Address",
            "Receipt",
            "Description",
            "Category split",
            "Money Out",
            "Money In"
        ]
        for field in expected_fields:
            if field not in raw_data:
                raise ValueError(f"Missing expected field: {field}")

    def id(self) -> str:
        return self._raw["Transaction ID"].strip()

    def date(self) -> datetime.date:
        if self._date is None:
            self._date = parse_date(self._raw["Date"].strip())
        return self._date

    def amount(self) -> float:
        if self._amount is None:
            try:
                self._amount = float(self._raw["Amount"].strip())
            except (ValueError, InvalidOperation):
                raise ValueError(f"Invalid amount: {self._raw['Amount']}")
        return self._amount

