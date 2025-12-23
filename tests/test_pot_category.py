import pytest
from budget.transaction import Transaction
from budget.raw_transaction import RawTransaction
from budget.main import BudgetApp
from budget.widgets import TransactionTable
from budget.screens import PotCategoryScreen
from tests import utils

def create_dummy_transaction(trx_id="1", category="", pot_category=""):
    raw_data = utils.mock_raw_trx_data(**{"Transaction ID": trx_id})
    rt = RawTransaction(raw_data)
    processed = {}
    if category:
        processed["category"] = category
    if pot_category:
        processed["pot_category"] = pot_category
    return Transaction(rt, processed)

def test_transaction_persistence():
    trx = create_dummy_transaction(category="Pot", pot_category="Bills")
    assert trx.category() == "Pot"
    assert trx.pot_category() == "Bills"

    data = trx.to_prefixed_dict()
    assert data["bt_category"] == "Pot"
    assert data["bt_pot_category"] == "Bills"

def test_transaction_setters():
    trx = create_dummy_transaction()
    trx.set_category("Pot")
    trx.set_pot_category("Holidays")
    assert trx.category() == "Pot"
    assert trx.pot_category() == "Holidays"

@pytest.mark.asyncio
async def test_app_set_pot_category_flow():
    app = BudgetApp()
    trx = create_dummy_transaction()
    app.transactions = [trx]
    app.displayed_transactions = [trx]

    async with app.run_test() as pilot:
        # Select the row
        table = app.query_one(TransactionTable)
        table.load_data([trx])
        table.cursor_coordinate = (0, 0)

        # Set category to Pot
        app.action_set_category("Pot")
        await pilot.pause()

        # Should be on PotCategoryScreen
        assert isinstance(app.screen, PotCategoryScreen)

        # Type "Bi" to filter for "Bills"
        await pilot.press("B", "i")
        await pilot.pause()

        # Press Enter to select
        await pilot.press("enter")
        await pilot.pause()

        # Should be back to main screen
        assert not isinstance(app.screen, PotCategoryScreen)
        assert trx.category() == "Pot"
        assert trx.pot_category() == "Bills"

        # Change category away from Pot
        app.action_set_category("Groceries")
        assert trx.category() == "Groceries"
        assert trx.pot_category() == "" # Should be cleared

@pytest.mark.asyncio
async def test_app_set_pot_category_cancel():
    app = BudgetApp()
    trx = create_dummy_transaction()
    app.transactions = [trx]
    app.displayed_transactions = [trx]

    async with app.run_test() as pilot:
        table = app.query_one(TransactionTable)
        table.load_data([trx])
        table.cursor_coordinate = (0, 0)

        app.action_set_category("Pot")
        await pilot.pause()

        assert isinstance(app.screen, PotCategoryScreen)

        # Cancel (press escape)
        await pilot.press("escape")
        await pilot.pause()

        assert not isinstance(app.screen, PotCategoryScreen)
        assert trx.category() == "Pot"
        assert trx.pot_category() == "" # Not set

@pytest.mark.asyncio
async def test_app_set_pot_category_list_selection():
    app = BudgetApp()
    trx = create_dummy_transaction()
    app.transactions = [trx]
    app.displayed_transactions = [trx]

    async with app.run_test() as pilot:
        table = app.query_one(TransactionTable)
        table.load_data([trx])
        table.cursor_coordinate = (0, 0)

        app.action_set_category("Pot")
        await pilot.pause()

        assert isinstance(app.screen, PotCategoryScreen)

        # Select using list (down, down, enter)
        # Filter is empty, so all options are shown.
        # Sorted order: Bills, Car maintenance, ...
        # "Bills" is first, "Car maintenance" is second.

        # Input has focus. Pressing down should move selection in list.
        await pilot.press("down") # Move to second item (index 1)
        await pilot.press("enter")
        await pilot.pause()

        assert not isinstance(app.screen, PotCategoryScreen)
        assert trx.category() == "Pot"
        assert trx.pot_category() == "Car maintenance"
