import csv
from typing import List

from budget.transaction import Transaction
from budget.raw_transaction import RawTransaction
from budget.common import EXPECTED_RAW_FIELDS


def load_data(csv_filename: str) -> List[Transaction]:
    """
    Reads a raw or processed data file. 
    The data file must have at least all of common.EXPECTED_RAW_FIELDS
    """
    rows: List[Transaction] = []
    with open(csv_filename, newline='', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        
        if not reader.fieldnames:
            raise ValueError("CSV file has no header")
            
        missing = [f for f in EXPECTED_RAW_FIELDS if f not in reader.fieldnames]
        if missing:
            raise ValueError(f"Missing fields: {', '.join(missing)}")

        # Identify processed columns
        processed_columns = [f for f in reader.fieldnames if f not in EXPECTED_RAW_FIELDS]

        for row in reader:
            # Split raw and processed data
            raw_data = {k: row[k] for k in EXPECTED_RAW_FIELDS}
            processed_data = {k: row[k] for k in processed_columns}

            rt = RawTransaction(raw_data)
            trx = Transaction(rt, processed_data)


            rows.append(trx)
    return rows
