from decimal import Decimal
import datetime
import pytest
from budget.raw_transaction import RawTransaction


def make_row(**overrides):
    row = {
        "Transaction ID": " tx123 ",
        "Date": "28/07/2025",
        "Time": "12:34:56",
        "Type": "card",
        "Name": "Coffee Shop",
        "Emoji": "☕",
        "Category": "eating_out",
        "Amount": "-3.50",
        "Currency": "GBP",
        "Local amount": "-3.50",
        "Local currency": "GBP",
        "Notes and #tags": "latte #coffee",
        "Address": "123 Main St",
        "Receipt": "",
        "Description": "Coffee",
        "Category split": "",
        "Money Out": "-3.50",
        "Money In": ""
    }
    row.update(overrides)
    return row


def test_happy_path():
    row = make_row()
    trx = RawTransaction(row)

    assert trx.id() == "tx123"
    assert trx.date() == datetime.date(year=2025, month=7, day=28)
    assert trx.amount() == -3.5
    assert trx._raw is row


def test_date_iso_format():
    row = make_row(Date="2025-07-28")
    trx = RawTransaction(row)
    assert trx.date() == datetime.date(2025, 7, 28)


def test_bad_date():
    row = make_row(Date="not a date")
    trx = RawTransaction(row)
    with pytest.raises(ValueError):
        trx.date()


def test_missing_field():
    row = make_row()
    del row["Transaction ID"]
    with pytest.raises(ValueError, match="Missing expected field: Transaction ID"):
        RawTransaction(row)
