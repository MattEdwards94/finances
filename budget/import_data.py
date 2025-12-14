import csv
from typing import List

from budget import RawTransaction


def load_raw_data(csv_filename: str) -> List[RawTransaction]:
    """
    Reads a raw Monzo data export from file
    """
    rows: List[RawTransaction] = []
    with open(csv_filename, newline='', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            rt = RawTransaction.from_csv_row(row)
            if rt:
                rows.append(rt)
    return rows
