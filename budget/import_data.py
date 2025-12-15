import csv
from typing import List

from budget import RawTransaction
from budget.common import EXPECTED_RAW_FIELDS


def load_data(csv_filename: str) -> List[RawTransaction]:
    """
    Reads a raw or processed data file. 
    The data file must have at least all of common.EXPECTED_RAW_FIELDS

    """
    rows: List[RawTransaction] = []
    with open(csv_filename, newline='', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        
        if not reader.fieldnames:
            raise ValueError("CSV file has no header")
            
        missing = [f for f in EXPECTED_RAW_FIELDS if f not in reader.fieldnames]
        if missing:
            raise ValueError(f"Missing fields: {', '.join(missing)}")

        print(f"Headers: {reader.fieldnames}")

        for row in reader:
            rt = RawTransaction(row)
            rows.append(rt)
    return rows
