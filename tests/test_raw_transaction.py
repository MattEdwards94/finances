import datetime
import pytest

from budget.raw_transaction import RawTransaction
from . import utils


def test_can_create_raw_transaction():
    row = utils.mock_raw_trx_data()

    trx = RawTransaction(row)

    assert trx.to_dict() == row

def test_date_iso_format():
    # Explicitly set the date so we can verify it
    row = utils.mock_raw_trx_data(Date="2025-07-28")

    trx = RawTransaction(row)

    assert trx.date() == datetime.date(2025, 7, 28)

def test_bad_date_raises():
    row = utils.mock_raw_trx_data(Date="not a date")

    trx = RawTransaction(row)

    with pytest.raises(ValueError):
        trx.date()

def test_missing_field_raises():
    row = utils.mock_raw_trx_data()
    del row["Time"]

    with pytest.raises(ValueError, match="Missing expected field: Time"):
        RawTransaction(row)

def test_equality_operator():
    row1 = utils.mock_raw_trx_data()
    row2 = utils.mock_raw_trx_data()

    trx1 = RawTransaction(row1)
    trx2 = RawTransaction(row2)

    assert trx1 == trx2

    row2["Name"] = "Different Name"
    trx3 = RawTransaction(row2)

    assert trx1 != trx3
