import csv
from dataclasses import dataclass
from typing import Optional, List
from budget.raw_transaction import RawTransaction
from budget import common

class Transaction:
    fields_to_persist = [
        "excluded",
        "category",
        "status",
    ]

    def __init__(self, raw_transaction: RawTransaction, processed_columns: dict = {}):
        self.raw = raw_transaction

        # Processed fields
        self._excluded: bool = False
        self._category: str = ""
        self._status: str = ""

        if "excluded" in processed_columns:
            self._excluded = bool(processed_columns["excluded"])
        if "category" in processed_columns:
            self._category = processed_columns["category"]
        if "status" in processed_columns:
            self._status = processed_columns["status"]

    def __eq__(self, other):
        if not isinstance(other, Transaction):
            return NotImplemented
        return self.raw == other.raw and all(
            getattr(self, field)() == getattr(other, field)()
            for field in self.fields_to_persist
        )

    def to_prefixed_dict(self) -> dict:
        """
        Exports the transaction to a dictionary suitable for CSV writing.
        Processed fields are prefixed with 'bt_'.
        """
        data = self.raw._raw.copy()

        for field in self.fields_to_persist:
            # add the data to the dict with prefix
            data[f"bt_{field}"] = getattr(self, field)()

        return data

    def category(self):
        return self._category

    def status(self):
        return self._status

    def excluded(self):
        return self._excluded

    def set_category(self, category: str):
        self._category = category

    def set_status(self, status: str):
        self._status = status

    def set_excluded(self, excluded: bool):
        self._excluded = excluded

    def id(self):
        return self.raw.id()

    def date(self):
        return self.raw.date()

    def type(self):
        return self.raw.type()

    def name(self):
        return self.raw.name()

    def amount(self):
        return self.raw.amount()

    def notes(self):
        return self.raw.notes()

def save_transactions(filename: str, transactions: List[Transaction]):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        # Combine raw fields and processed fields
        processed_fields = [f"bt_{f}" for f in Transaction.fields_to_persist]
        fieldnames = common.EXPECTED_RAW_FIELDS + processed_fields
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for trx in transactions:
            writer.writerow(trx.to_prefixed_dict())


