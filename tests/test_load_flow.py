import unittest.mock
import pytest
from budget.main import BudgetApp
from budget.transaction import Transaction
from budget.raw_transaction import RawTransaction
from budget.screens import SaveChangesConfirmScreen, LoadScreen, SaveScreen
from tests import utils

@pytest.mark.asyncio
async def test_load_flow_existing_data_cancel_clear():
    # Setup app with data
    mock_trxs = [Transaction(RawTransaction(utils.mock_raw_trx_data()))]
    with unittest.mock.patch("budget.main.load_data", return_value=mock_trxs):
        app = BudgetApp()
        async with app.run_test() as pilot:
            app.load_transactions("dummy.csv")
            assert len(app.transactions) == 1

            # Trigger load
            app.action_load_file()
            await pilot.pause()

            # Should see SaveChangesConfirmScreen
            assert isinstance(app.screen, SaveChangesConfirmScreen)

            # Click Cancel
            await pilot.click("#cancel")
            await pilot.pause()

            # Should be back to main screen, data preserved
            assert not isinstance(app.screen, SaveChangesConfirmScreen)
            assert len(app.transactions) == 1

@pytest.mark.asyncio
async def test_load_flow_existing_data_no_save_then_load():
    # Setup app with data
    mock_trxs = [Transaction(RawTransaction(utils.mock_raw_trx_data()))]
    with unittest.mock.patch("budget.main.load_data", return_value=mock_trxs):
        app = BudgetApp()
        async with app.run_test() as pilot:
            app.load_transactions("dummy.csv")

            app.action_load_file()
            await pilot.pause()

            # Click No (don't save)
            await pilot.click("#no")
            await pilot.pause()

            # Should now be on LoadScreen
            assert isinstance(app.screen, LoadScreen)

            # Data should be cleared
            assert not app.transactions

            # Proceed to load new file
            await pilot.click("#filename")
            await pilot.press("n", "e", "w", ".", "c", "s", "v")
            await pilot.click("#load")
            await pilot.pause()

            # Should have loaded (mock returns same data, but count is 1)
            assert len(app.transactions) == 1
            # Verify notification or just success

@pytest.mark.asyncio
async def test_load_flow_existing_data_save_then_load():
    mock_trxs = [Transaction(RawTransaction(utils.mock_raw_trx_data()))]
    with unittest.mock.patch("budget.main.load_data", return_value=mock_trxs):
        with unittest.mock.patch("budget.main.save_transactions") as mock_save:
            with unittest.mock.patch("pathlib.Path.exists", return_value=False):
                app = BudgetApp()
                async with app.run_test() as pilot:
                    app.load_transactions("dummy.csv")

                    app.action_load_file()
                    await pilot.pause()

                    # Click Yes (save)
                    await pilot.click("#yes")
                    await pilot.pause()

                    # Should be on SaveScreen
                    assert isinstance(app.screen, SaveScreen)

                    # Save file
                    await pilot.click("#filename")
                    await pilot.press("s", "a", "v", "e", ".", "c", "s", "v")
                    await pilot.click("#save")
                    await pilot.pause()

                    mock_save.assert_called_once()

                    # Should now be on LoadScreen
                    assert isinstance(app.screen, LoadScreen)

                    # Load new file
                    await pilot.click("#filename")
                    await pilot.press("n", "e", "w", ".", "c", "s", "v")
                    await pilot.click("#load")
                    await pilot.pause()

                    assert len(app.transactions) == 1
