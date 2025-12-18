import csv
from dataclasses import dataclass
from typing import Optional, List
from raw_transaction import RawTransaction
from . import common

class Transaction:
    fields_to_persist = [
        "excluded",
    ]

    def __init__(self, raw_transaction: RawTransaction, processed_columns: dict = {}):
        self.raw = raw_transaction

        # Processed fields
        self.excluded: bool = False

        # Update with any provided processed columns
        for field, value in processed_columns.items():
            if field not in self.fields_to_persist:
                raise ValueError(f"Unknown processed field: {field}")
            setattr(self, field, value)

    def to_dict(self) -> dict:
        """
        Exports the transaction to a dictionary suitable for CSV writing, checking for
        any possbile field conflicts.
        """
        data = self.raw._raw.copy()

        for field in self.fields_to_persist:
            # check it doesn't conflict with raw data fields
            if field in common.EXPECTED_RAW_FIELDS:
                raise ValueError(f"Processed field '{field}' conflicts with raw data fields.")
            # add the data to the dict
            data[field] = getattr(self, field)

        return data

def save_transactions(filename: str, transactions: List[Transaction]):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        # Combine raw fields and processed fields
        fieldnames = common.EXPECTED_RAW_FIELDS + Transaction.fields_to_persist
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for trx in transactions:
            writer.writerow(trx.to_dict())


