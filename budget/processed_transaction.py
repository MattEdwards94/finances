import csv
from dataclasses import dataclass
from typing import Optional
from .raw_transaction import RawTransaction


class ProcessedTransaction:
    def __init__(self, raw_transaction: RawTransaction):
        self.raw_trx = raw_transaction

    def write_to_csv(self, file_handle: csv.writer):
        pass



class ProcessedTransactions:
    def __init__(self, trxs: list[ProcessedTransaction]):
        self.trxs = trxs

    def to_csv(self, filename: str):
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['date', 'name', 'amount', 'category', 'notes']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for trx in self.trxs:
                writer.writerow({
                    'date': trx.raw_trx.date,
                    'name': trx.raw_trx.name,
                    'amount': trx.raw_trx.amount,
                    'category': getattr(trx, 'category', ''),
                    'notes': getattr(trx, 'notes', '')
                })


