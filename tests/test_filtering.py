import pytest
from textual.coordinate import Coordinate
from budget.widgets import TransactionTable
from budget.transaction import Transaction
from budget.raw_transaction import RawTransaction
from . import utils

@pytest.mark.asyncio
async def test_filter_toggle_logic():
    # Setup data: 1 categorized, 1 uncategorized
    t1 = Transaction(RawTransaction(utils.mock_raw_trx_data(Name="Cat")))
    t1.set_category("Food")
    t2 = Transaction(RawTransaction(utils.mock_raw_trx_data(Name="Uncat")))

    mock_trxs = [t1, t2]

    async with utils.run_app_with_mock_data(mock_trxs) as (app, pilot, _):
        # Default: All (2 items)
        assert len(app.displayed_transactions) == 2
        assert app.query_one(TransactionTable).row_count == 2

        # Filter -> Uncategorized
        app.filter_categories = {"Uncategorized"}
        # pylint: disable=protected-access
        app._apply_filters()
        await pilot.pause()

        assert len(app.displayed_transactions) == 1
        assert app.displayed_transactions[0].name() == "Uncat"
        assert app.query_one(TransactionTable).row_count == 1

        # Filter -> Categorized
        app.filter_categories = {"Categorized"}
        app._apply_filters()
        await pilot.pause()

        assert len(app.displayed_transactions) == 1
        assert app.displayed_transactions[0].name() == "Cat"
        assert app.query_one(TransactionTable).row_count == 1

        # Filter -> All
        app.filter_categories = {"All"}
        app._apply_filters()
        await pilot.pause()

        assert len(app.displayed_transactions) == 2

@pytest.mark.asyncio
async def test_set_category_while_filtered():
    # Setup: 2 uncategorized transactions
    t1 = Transaction(RawTransaction(utils.mock_raw_trx_data(Name="T1")))
    t2 = Transaction(RawTransaction(utils.mock_raw_trx_data(Name="T2")))

    mock_trxs = [t1, t2]

    async with utils.run_app_with_mock_data(mock_trxs) as (app, _, _):
        # Filter to uncategorized
        app.filter_categories = {"Uncategorized"}
        # pylint: disable=protected-access
        app._apply_filters()

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
        app.filter_categories = {"Categorized"}
        app._apply_filters()

        # Should only show T2
        assert len(app.displayed_transactions) == 1
        assert app.displayed_transactions[0].name() == "T2"

@pytest.mark.asyncio
async def test_multi_filter_logic():
    # Setup data
    mock_trxs = utils.mock_transactions_for_filtering()

    async with utils.run_app_with_mock_data(mock_trxs) as (app, pilot, _):
        # Filter -> Groceries + Transport
        app.filter_categories = {"Groceries", "Transport"}
        # pylint: disable=protected-access
        app._apply_filters()
        await pilot.pause()

        assert len(app.displayed_transactions) == 2
        names = sorted([t.name() for t in app.displayed_transactions])
        assert names == ["T1", "T3"]

@pytest.mark.asyncio
async def test_case_insensitive_filtering():
    # Setup data with mixed case categories
    t1 = Transaction(RawTransaction(utils.mock_raw_trx_data(Name="T1")))
    t1.set_category("Groceries")
    t2 = Transaction(RawTransaction(utils.mock_raw_trx_data(Name="T2")))
    t2.set_category("groceries") # lowercase
    t3 = Transaction(RawTransaction(utils.mock_raw_trx_data(Name="T3")))
    t3.set_category("GROCERIES") # uppercase

    mock_trxs = [t1, t2, t3]

    async with utils.run_app_with_mock_data(mock_trxs) as (app, pilot, _):
        # Filter -> Groceries (mixed case in filter set shouldn't matter if we normalize)
        # But FilterScreen usually returns what is in the list.
        # Let's assume we select "Groceries" (from T1).
        app.filter_categories = {"Groceries"}
        # pylint: disable=protected-access
        app._apply_filters()
        await pilot.pause()

        # Should show all 3 because they are all groceries (case-insensitive)
        assert len(app.displayed_transactions) == 3
        names = sorted([t.name() for t in app.displayed_transactions])
        assert names == ["T1", "T2", "T3"]
