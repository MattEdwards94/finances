import unittest.mock
import pytest
from textual.coordinate import Coordinate
from budget.main import BudgetApp
from budget.widgets import TransactionTable, TransactionDetails
from budget.transaction import Transaction
from budget.raw_transaction import RawTransaction
from budget.screens import SaveScreen
from tests import utils

@pytest.mark.asyncio
async def test_app_initial_state():
    app = BudgetApp()
    async with app.run_test() as _:
        assert not app.transactions

        table = app.query_one(TransactionTable)
        assert table.row_count == 0

        details = app.query_one(TransactionDetails)
        assert str(details.query_one("#det-desc").render()) == "--"

@pytest.mark.asyncio
async def test_app_load_transactions():
    # Mock load_data to return some transactions
    mock_trxs = [
        Transaction(RawTransaction(utils.mock_raw_trx_data(Name="Trx 1"))),
        Transaction(RawTransaction(utils.mock_raw_trx_data(Name="Trx 2")))
    ]

    with unittest.mock.patch("budget.main.load_data", return_value=mock_trxs):
        app = BudgetApp()
        async with app.run_test() as _:
            # Trigger load
            app.load_transactions("dummy.csv")

            assert len(app.transactions) == 2

            table = app.query_one(TransactionTable)
            assert table.row_count == 2
            assert table.get_cell_at(Coordinate(0, 2)) == "Trx 1"

@pytest.mark.asyncio
async def test_app_selection_updates_sidebar():
    mock_trxs = [
        Transaction(RawTransaction(utils.mock_raw_trx_data(Name="Trx 1", Amount="-10.00"))),
        Transaction(RawTransaction(utils.mock_raw_trx_data(Name="Trx 2", Amount="-20.00")))
    ]

    with unittest.mock.patch("budget.main.load_data", return_value=mock_trxs):
        app = BudgetApp()
        async with app.run_test() as pilot:
            app.load_transactions("dummy.csv")

            # Initially first row selected (default behavior of DataTable usually,
            # but let's ensure we click it or move cursor)
            table = app.query_one(TransactionTable)
            table.move_cursor(row=0)

            # Wait for events to process
            await pilot.pause()

            details = app.query_one(TransactionDetails)
            assert str(details.query_one("#det-desc").render()) == "Trx 1"

            # Move to second row
            table.move_cursor(row=1)
            await pilot.pause()

            assert str(details.query_one("#det-desc").render()) == "Trx 2"
            assert str(details.query_one("#det-amt").render()) == "-20.0"

@pytest.mark.asyncio
async def test_app_set_category():
    mock_trxs = [
        Transaction(RawTransaction(utils.mock_raw_trx_data(Name="Trx 1")))
    ]

    with unittest.mock.patch("budget.main.load_data", return_value=mock_trxs):
        app = BudgetApp()
        async with app.run_test() as _:
            app.load_transactions("dummy.csv")

            # Select first row
            table = app.query_one(TransactionTable)
            table.move_cursor(row=0)

            # Trigger action
            app.action_set_category("Groceries")

            # Check transaction updated
            assert app.transactions[0].category() == "Groceries"

            # Check table updated (Category is column 5)
            assert table.get_cell_at(Coordinate(0, 5)) == "Groceries"

            # Check sidebar updated
            details = app.query_one(TransactionDetails)
            assert str(details.query_one("#det-category").render()) == "Groceries"

@pytest.mark.asyncio
async def test_app_clear_data_no_data():
    app = BudgetApp()
    async with app.run_test() as _:
        # Ensure no data
        assert not app.transactions

        # Trigger clear action
        app.action_clear_data()

        # Should verify notification or just that no screen was pushed
        # Since we can't easily check notifications in this test setup without mocking,
        # we check that no screen was pushed (screen stack size is 1 - the main app)
        assert len(app.screen_stack) == 1

@pytest.mark.asyncio
async def test_app_clear_data_cancel():
    mock_trxs = [Transaction(RawTransaction(utils.mock_raw_trx_data()))]
    with unittest.mock.patch("budget.main.load_data", return_value=mock_trxs):
        app = BudgetApp()
        async with app.run_test() as pilot:
            app.load_transactions("dummy.csv")

            app.action_clear_data()
            await pilot.pause()

            # Click Cancel
            await pilot.click("#cancel")
            await pilot.pause()

            # Data should still exist
            assert len(app.transactions) == 1

@pytest.mark.asyncio
async def test_app_clear_data_no_save():
    mock_trxs = [Transaction(RawTransaction(utils.mock_raw_trx_data()))]
    with unittest.mock.patch("budget.main.load_data", return_value=mock_trxs):
        app = BudgetApp()
        async with app.run_test() as pilot:
            app.load_transactions("dummy.csv")

            app.action_clear_data()
            await pilot.pause()

            # Click No (don't save)
            await pilot.click("#no")
            await pilot.pause()

            # Data should be cleared
            assert not app.transactions
            assert app.query_one(TransactionTable).row_count == 0

@pytest.mark.asyncio
async def test_app_clear_data_save_cancel():
    mock_trxs = [Transaction(RawTransaction(utils.mock_raw_trx_data()))]
    with unittest.mock.patch("budget.main.load_data", return_value=mock_trxs):
        app = BudgetApp()
        async with app.run_test() as pilot:
            app.load_transactions("dummy.csv")

            app.action_clear_data()
            await pilot.pause()

            # Click Yes (want to save)
            await pilot.click("#yes")
            await pilot.pause()

            # Should be on SaveScreen
            assert isinstance(app.screen, SaveScreen)

            # Cancel save
            await pilot.click("#cancel")
            await pilot.pause()

            # Data should still exist (clearing happens AFTER save)
            assert len(app.transactions) == 1

@pytest.mark.asyncio
async def test_app_clear_data_save_success():
    mock_trxs = [Transaction(RawTransaction(utils.mock_raw_trx_data()))]
    with unittest.mock.patch("budget.main.load_data", return_value=mock_trxs):
        # Mock save_transactions to avoid file I/O
        with unittest.mock.patch("budget.main.save_transactions") as mock_save:
            # Mock Path.exists to return False (new file)
            with unittest.mock.patch("pathlib.Path.exists", return_value=False):
                app = BudgetApp()
                async with app.run_test() as pilot:
                    app.load_transactions("dummy.csv")

                    app.action_clear_data()
                    await pilot.pause()

                    # Click Yes (want to save)
                    await pilot.click("#yes")
                    await pilot.pause()

                    # Enter filename and save
                    await pilot.click("#filename")
                    await pilot.press("s", "a", "v", "e", ".", "c", "s", "v")
                    await pilot.click("#save")
                    await pilot.pause()

                    # Verify save called
                    mock_save.assert_called_once()

                    # Data should be cleared
                    assert not app.transactions
                    assert app.query_one(TransactionTable).row_count == 0
