import pytest
# pylint: disable=duplicate-code
from budget.transaction import Transaction
from budget.raw_transaction import RawTransaction
from budget.screens import SaveChangesConfirmScreen, SaveOrLoadScreen
from . import utils

@pytest.mark.asyncio
async def test_load_flow_existing_data_cancel_clear():
    # Setup app with data
    mock_trxs = [Transaction(RawTransaction(utils.mock_raw_trx_data()))]
    async with utils.run_app_with_mock_data(mock_trxs) as (app, pilot, _):
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
    async with utils.run_app_with_mock_data(mock_trxs) as (app, pilot, _):
        app.action_load_file()
        await pilot.pause()

        # Click No (don't save)
        await pilot.click("#no")
        await pilot.pause()

        # Should now be on load screen
        assert isinstance(app.screen, SaveOrLoadScreen)
        assert app.screen.mode == "load"

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
    async with utils.run_app_with_mock_data(
        mock_trxs, mock_save=True, mock_path_exists=False
    ) as (app, pilot, mock_save):
        app.action_load_file()
        await pilot.pause()

        await utils.perform_save_flow(pilot, "save.csv")

        mock_save.assert_called_once()

        # Should now be on load screen
        assert isinstance(app.screen, SaveOrLoadScreen)
        assert app.screen.mode == "load"

        # Load new file
        await pilot.click("#filename")
        await pilot.press("n", "e", "w", ".", "c", "s", "v")
        await pilot.click("#load")
        await pilot.pause()

        assert len(app.transactions) == 1
