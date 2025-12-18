import csv
from dataclasses import dataclass
from typing import Optional, List
from .raw_transaction import RawTransaction
from . import common

class Transaction:
    def __init__(self, raw_transaction: RawTransaction):
        self.raw = raw_transaction
        self.category: str = ""
        self.notes: str = ""
        # We can add more fields here as needed, e.g. pot_link_id

    def __str__(self):
        return f"{self.raw} | Cat: {self.category}"

def save_transactions(filename: str, transactions: List['Transaction']):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        # Combine raw fields and processed fields
        fieldnames = common.EXPECTED_RAW_FIELDS + ['category', 'notes']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for trx in transactions:
            # Start with the raw data
            row_data = trx.raw._raw.copy()
            # Add processed data
            row_data['category'] = trx.category
            row_data['notes'] = trx.notes
            writer.writerow(row_data)


