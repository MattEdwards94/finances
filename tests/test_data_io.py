import csv
from pathlib import Path
import pytest

import budget
from . import utils

def create_csv(tmp_path: Path, fields: list[str], rows: list[dict]) -> str:
    p = tmp_path / "test.csv"
    with open(p, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return str(p)

def test_can_load_raw_data(tmp_path):
    """
    Creates a CSV file with mock raw transaction data and tests loading it.
    """
    row_data = utils.mock_raw_trx_data()
    csv_file = create_csv(tmp_path, list(row_data.keys()), [row_data])

    transactions = budget.load_data(csv_file)

    assert len(transactions) == 1
    assert transactions[0] == budget.Transaction(budget.RawTransaction(row_data))

def test_load_data_missing_field_raises_exception(tmp_path):
    """
    We expect all fields in EXPECTED_RAW_FIELDS to be present.
    """
    row_data = utils.mock_raw_trx_data()
    del row_data["Transaction ID"]
    csv_file = create_csv(tmp_path, list(row_data), [row_data])

    with pytest.raises(ValueError, match="Missing fields: Transaction ID"):
        budget.load_data(csv_file)

def test_load_data_extra_fields_ok(tmp_path):
    """
    Additional fields are fine, as these can represent processed data.
    This should not be part of the raw transaction
    """
    row_data = utils.mock_raw_trx_data()
    row_data["Extra Field"] = "extra"
    csv_file = create_csv(tmp_path, list(row_data), [row_data])

    transactions = budget.load_data(csv_file)

    assert len(transactions) == 1
    exp_raw_trx = budget.RawTransaction(utils.mock_raw_trx_data())
    assert transactions[0] == budget.Transaction(exp_raw_trx)

def test_load_data_with_prefixes(tmp_path):
    """
    Creates a CSV file with mock raw transaction data and processed data with 'bt_' prefixes.
    Tests loading it.
    """
    row_data = utils.mock_raw_trx_data()
    row_data["bt_category"] = "Food"
    row_data["bt_status"] = "Reviewed"
    row_data["bt_excluded"] = "True"
    csv_file = create_csv(tmp_path, list(row_data.keys()), [row_data])

    transactions = budget.load_data(csv_file)

    assert len(transactions) == 1
    trx = transactions[0]
    assert trx.raw == budget.RawTransaction(utils.mock_raw_trx_data())
    assert trx.category() == "Food"
    assert trx.status() == "Reviewed"
    assert trx.excluded() is True

def test_save_to_csv():
    row_data = utils.mock_raw_trx_data()
    rt = budget.RawTransaction(row_data)
    trx = budget.Transaction(rt)
    trx.set_category("Some Category")
    trx.set_status("Some Status")
    trx.set_excluded(False)

    budget.save_transactions("test_output.csv", [trx])

    # read csv a load headers and data
    with open("test_output.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        assert headers is not None
        data_row = next(reader)

    for field in budget.EXPECTED_RAW_FIELDS:
        assert field in headers
    assert "bt_category" in headers
    assert "bt_status" in headers
    assert "bt_excluded" in headers

    for field in budget.EXPECTED_RAW_FIELDS:
        assert data_row[field] == row_data[field]
    assert data_row["bt_category"] == "Some Category"
    assert data_row["bt_status"] == "Some Status"
    assert data_row["bt_excluded"] == "False"

def test_round_trip(tmp_path):
    row_data = utils.mock_raw_trx_data()
    rt = budget.RawTransaction(row_data)
    trx = budget.Transaction(rt)
    trx.set_category("RoundTrip")
    trx.set_status("Done")
    trx.set_excluded(True)

    csv_file = tmp_path / "round_trip.csv"
    budget.save_transactions(csv_file, [trx])

    loaded_trxs = budget.load_data(csv_file)
    assert len(loaded_trxs) == 1
    loaded_trx = loaded_trxs[0]

    assert loaded_trx.category() == "RoundTrip"
    assert loaded_trx.status() == "Done"
    assert loaded_trx.excluded() is True
