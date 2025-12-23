import unittest.mock
import pytest
from textual.coordinate import Coordinate
from budget.main import BudgetApp
from budget.widgets import TransactionTable
from budget.transaction import Transaction
from budget.raw_transaction import RawTransaction
from tests import utils

@pytest.mark.asyncio
async def test_filter_toggle_logic():
    # Setup data: 1 categorized, 1 uncategorized
    t1 = Transaction(RawTransaction(utils.mock_raw_trx_data(Name="Cat")))
    t1.set_category("Food")
    t2 = Transaction(RawTransaction(utils.mock_raw_trx_data(Name="Uncat")))

    mock_trxs = [t1, t2]

    with unittest.mock.patch("budget.main.load_data", return_value=mock_trxs):
        app = BudgetApp()
        async with app.run_test() as pilot:
            app.load_transactions("dummy.csv")

            # Default: All (2 items)
            assert len(app.displayed_transactions) == 2
            assert app.query_one(TransactionTable).row_count == 2

            # Toggle -> Uncategorized
            app.action_toggle_filter_category()
            await pilot.pause()

            assert app.filter_category == "uncategorized"
            assert len(app.displayed_transactions) == 1
            assert app.displayed_transactions[0].name() == "Uncat"
            assert app.query_one(TransactionTable).row_count == 1

            # Toggle -> Categorized
            app.action_toggle_filter_category()
            await pilot.pause()

            assert app.filter_category == "categorized"
            assert len(app.displayed_transactions) == 1
            assert app.displayed_transactions[0].name() == "Cat"
            assert app.query_one(TransactionTable).row_count == 1

            # Toggle -> All
            app.action_toggle_filter_category()
            await pilot.pause()

            assert app.filter_category == "all"
            assert len(app.displayed_transactions) == 2

@pytest.mark.asyncio
async def test_set_category_while_filtered():
    # Setup: 2 uncategorized transactions
    t1 = Transaction(RawTransaction(utils.mock_raw_trx_data(Name="T1")))
    t2 = Transaction(RawTransaction(utils.mock_raw_trx_data(Name="T2")))

    mock_trxs = [t1, t2]

    with unittest.mock.patch("budget.main.load_data", return_value=mock_trxs):
        app = BudgetApp()
        async with app.run_test() as _:
            app.load_transactions("dummy.csv")

            # Filter to uncategorized
            app.action_toggle_filter_category()
            assert app.filter_category == "uncategorized"

            # Select second row (T2)
            table = app.query_one(TransactionTable)
            table.move_cursor(row=1)

            # Set category
            app.action_set_category("Food")

            # Verify T2 was updated
            assert t2.category() == "Food"
            assert t1.category() == ""

            # Verify table still shows it (until refresh)
            # T2 is at row 1
            assert table.get_cell_at(Coordinate(1, 5)) == "Food"

            # Toggle filter to refresh (Uncategorized -> Categorized)
            app.action_toggle_filter_category()
            assert app.filter_category == "categorized"

            # Should only show T2
            assert len(app.displayed_transactions) == 1
            assert app.displayed_transactions[0].name() == "T2"
