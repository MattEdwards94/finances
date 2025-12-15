import csv
import pytest
from budget.import_data import load_data
from budget.common import EXPECTED_RAW_FIELDS

def create_csv(tmp_path, fields, rows):
    p = tmp_path / "test.csv"
    with open(p, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return str(p)

def test_load_data_valid(tmp_path):
    fields = EXPECTED_RAW_FIELDS
    row_data = {f: "" for f in fields}
    row_data["Transaction ID"] = "tx1"
    row_data["Date"] = "28/07/2025"
    row_data["Amount"] = "10.00"
    
    csv_file = create_csv(tmp_path, fields, [row_data])
    
    transactions = load_data(csv_file)
    assert len(transactions) == 1
    assert transactions[0].id() == "tx1"

def test_load_data_missing_field(tmp_path):
    fields = [f for f in EXPECTED_RAW_FIELDS if f != "Transaction ID"]
    csv_file = create_csv(tmp_path, fields, [])
    
    with pytest.raises(ValueError, match="Missing fields: Transaction ID"):
        load_data(csv_file)

def test_load_data_extra_fields_ok(tmp_path):
    fields = EXPECTED_RAW_FIELDS + ["Extra"]
    row_data = {f: "" for f in EXPECTED_RAW_FIELDS}
    row_data["Transaction ID"] = "tx1"
    row_data["Date"] = "28/07/2025"
    row_data["Amount"] = "10.00"
    row_data["Extra"] = "stuff"
    
    csv_file = create_csv(tmp_path, fields, [row_data])
    
    transactions = load_data(csv_file)
    assert len(transactions) == 1
