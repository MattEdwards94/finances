from budget.transaction import Transaction
from budget.raw_transaction import RawTransaction
from . import utils

def test_initialization_defaults():
    row = utils.mock_raw_trx_data()
    raw_trx = RawTransaction(row)

    trx = Transaction(raw_trx)

    assert trx.raw == raw_trx
    assert trx.category() == ""
    assert trx.pot_category() == ""
    assert trx.status() == ""
    assert trx.excluded() is False

def test_initialization_with_processed_data():
    row = utils.mock_raw_trx_data()
    raw_trx = RawTransaction(row)
    processed = {
        "category": "Groceries",
        "pot_category": "Food",
        "status": "Reviewed",
        "excluded": True
    }

    trx = Transaction(raw_trx, processed)

    assert trx.category() == "Groceries"
    assert trx.pot_category() == "Food"
    assert trx.status() == "Reviewed"
    assert trx.excluded() is True

def test_setters_update_state():
    row = utils.mock_raw_trx_data()
    trx = Transaction(RawTransaction(row))

    trx.set_category("Utilities")
    trx.set_pot_category("Bills")
    trx.set_status("Pending")
    trx.set_excluded(True)

    assert trx.category() == "Utilities"
    assert trx.pot_category() == "Bills"
    assert trx.status() == "Pending"
    assert trx.excluded() is True

def test_delegated_methods():
    row = utils.mock_raw_trx_data(Amount="-10.00", Name="Test Shop")
    trx = Transaction(RawTransaction(row))

    assert trx.amount() == -10.00
    assert trx.name() == "Test Shop"

def test_equality():
    row = utils.mock_raw_trx_data()
    trx1 = Transaction(RawTransaction(row))
    trx2 = Transaction(RawTransaction(row))

    # Initially equal
    assert trx1 == trx2

    # Change processed field
    trx1.set_category("New Cat")
    assert trx1 != trx2

    # Make them equal again
    trx2.set_category("New Cat")
    assert trx1 == trx2

def test_to_prefixed_dict():
    row = utils.mock_raw_trx_data()
    trx = Transaction(RawTransaction(row))
    trx.set_category("Food")
    trx.set_pot_category("Groceries")
    trx.set_excluded(True)

    data = trx.to_prefixed_dict()

    assert data["bt_category"] == "Food"
    assert data["bt_pot_category"] == "Groceries"
    assert data["bt_excluded"] is True
    assert data["bt_status"] == ""
    # Check a raw field exists
    assert data["Name"] == row["Name"]

def test_clear_processed_fields():
    row = utils.mock_raw_trx_data()
    trx = Transaction(RawTransaction(row))

    trx.set_category("Food")
    trx.set_pot_category("Groceries")
    trx.set_status("Done")
    trx.set_excluded(True)
    trx.set_link("123")

    trx.clear_processed_fields()

    assert trx.category() == ""
    assert trx.pot_category() == ""
    assert trx.status() == ""
    assert trx.excluded() is False
    assert trx.link() == ""
