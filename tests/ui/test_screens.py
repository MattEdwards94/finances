import unittest.mock
import pytest
from textual.widgets import Label
from budget import Transaction, RawTransaction
from budget.screens import (
    OverwriteConfirmScreen,
    SaveChangesConfirmScreen,
    SaveOrLoadScreen,
    FilterScreen
)
from .. import utils

#
#   Save changes
#
@pytest.mark.asyncio
async def test_can_save_to_new_file():
    """
    Verifies that we can select a new file and it returns the name of this file to the 
    callback function for saving
    """
    screen = SaveOrLoadScreen(mode="save")
    app = utils.ScreenTestApp(screen)

    with unittest.mock.patch("pathlib.Path.exists", return_value=False):
        async with app.run_test() as pilot:
            await pilot.click("#filename")
            await pilot.press("n", "e", "w", ".", "c", "s", "v")
            await pilot.click("#save")

            assert app.result == "new.csv"

@pytest.mark.asyncio
async def test_save_file_cancel_returns_none():
    """
    Verifies that cancelling the save screen returns None
    """
    screen = SaveOrLoadScreen(mode="save")
    app = utils.ScreenTestApp(screen)
    async with app.run_test() as pilot:
        await pilot.click("#filename")
        await pilot.press("n", "e", "w", ".", "c", "s", "v")
        await pilot.click("#cancel")

        assert app.result is None

@pytest.mark.asyncio
async def test_save_file_escape_returns_none():
    """
    Verifies that cancelling the save screen returns None
    """
    screen = SaveOrLoadScreen(mode="save")
    app = utils.ScreenTestApp(screen)
    async with app.run_test() as pilot:
        await pilot.click("#filename")
        await pilot.press("n", "e", "w", ".", "c", "s", "v")
        await pilot.press("escape")

        assert app.result is None

@pytest.mark.asyncio
async def test_perform_overwrite_to_existing_file():
    """
    Verifies that when we select a file that already exists, we are prompted to overwrite.
    Verify that confirming the overwrite returns the filename to the callback function for saving
    """
    screen = SaveOrLoadScreen(mode="save")
    app = utils.ScreenTestApp(screen)
    with unittest.mock.patch("pathlib.Path.exists", return_value=True):
        async with app.run_test() as pilot:
            await pilot.click("#filename")
            await pilot.press("e", "x", "i", "s", "t", "s", ".", "c", "s", "v")
            await pilot.click("#save")

            # Should now be on OverwriteConfirmScreen
            assert isinstance(app.screen, OverwriteConfirmScreen)
            await pilot.click("#yes")

            # Should return the filename
            assert app.result == "exists.csv"

@pytest.mark.asyncio
async def test_reject_overwrite_to_existing_file():
    """
    Verifies that when we select a file that already exists, we are prompted to overwrite.
    Verify that denying the overwrite returns us to the save screen without dismissing it.
    Verify also that pressing escape returns us to the save screen.
    """
    screen = SaveOrLoadScreen(mode="save")
    app = utils.ScreenTestApp(screen)
    with unittest.mock.patch("pathlib.Path.exists", return_value=True):
        async with app.run_test() as pilot:
            await pilot.click("#filename")
            await pilot.press("e", "x", "i", "s", "t", "s", ".", "c", "s", "v")
            await pilot.click("#save")

            # Should now be on the overwrite confirm screen
            assert isinstance(app.screen, OverwriteConfirmScreen)
            await pilot.click("#no")

            # Should be back on save screen
            assert isinstance(app.screen, SaveOrLoadScreen)
            assert app.screen.mode == "save"
            assert app.result is None

            # Now repeat, but press escape
            await pilot.click("#save")

            # Should now be on the overwrite confirm screen
            assert isinstance(app.screen, OverwriteConfirmScreen)
            await pilot.press("escape")

            # Should be back on save screen
            assert isinstance(app.screen, SaveOrLoadScreen)
            assert app.screen.mode == "save"
            assert app.result is None

#
# Load screen empty data
#

@pytest.mark.asyncio
async def test_empty_data_load_file():
    """
    Verifies that when we load without existing data, we can select a file and it returns the
    name of the input file
    """
    # start app with no data
    async with utils.run_app_with_mock_data(transactions=None) as (app, pilot, _):
        await pilot.press("l")
        await pilot.pause()

        # Check we are on load screen
        assert isinstance(app.screen, SaveOrLoadScreen)
        assert app.screen.mode == "load"


        await pilot.click("#filename")
        # patch the BudgetApp's load_data to simulate file existence
        with unittest.mock.patch("budget.main.load_data") as mock_load:
            await pilot.press("e", "x", "i", "s", "t", "s", ".", "c", "s", "v")
            await pilot.click("#load")

            mock_load.assert_called_once_with("exists.csv")

@pytest.mark.asyncio
async def test_load_file_cancel_returns_none():
    """
    Verifies that cancelling the load screen returns None
    """
    screen = SaveOrLoadScreen(mode="load")
    app = utils.ScreenTestApp(screen)
    async with app.run_test() as pilot:
        await pilot.click("#cancel")

        assert app.result is None

@pytest.mark.asyncio
async def test_load_file_escape_returns_none():
    """
    Verifies that pressing escape on the load screen returns None
    """
    screen = SaveOrLoadScreen(mode="load")
    app = utils.ScreenTestApp(screen)
    async with app.run_test() as pilot:
        await pilot.press("escape")

        assert app.result is None

@pytest.mark.asyncio
async def test_load_file_no_filename_does_nothing():
    """
    Verifies that clicking load without a filename does nothing
    """
    screen = SaveOrLoadScreen(mode="load")
    app = utils.ScreenTestApp(screen)
    async with app.run_test() as pilot:
        await pilot.click("#load")

        assert app.result is None
        # Still on the same screen
        assert isinstance(app.screen, SaveOrLoadScreen)
        assert app.screen.mode == "load"

#
# Load screen with existing data
#

@pytest.mark.asyncio
async def test_load_file_with_existing_data_then_cancel_does_nothing():
    """
    Verifies that when we load with existing data, we are prompted to save changes first.
    Verify that if we cancel, we return to the main screen with data intact.
    """
    # start app with existing data
    mock_trxs = [Transaction(RawTransaction(utils.mock_raw_trx_data()))]
    async with utils.run_app_with_mock_data(transactions=mock_trxs) as (app, pilot, _):
        await pilot.press("l")
        await pilot.pause()

        # Check we are on the confirm save changes screen
        assert isinstance(app.screen, SaveChangesConfirmScreen)

        # Now click cancel and verify we are back to main screen with data intact
        await pilot.click("#cancel")
        assert not isinstance(app.screen, SaveChangesConfirmScreen)
        assert len(app.transactions) == 1  # Data should still be intact

@pytest.mark.asyncio
async def test_load_file_with_existing_data_save_then_load():
    """
    Verifies that when we load with existing data, we are prompted to save changes first.
    Verify that if we select Yes, we proceed to save screen, and after saving, we go to load screen.
    """
    # start app with existing data
    mock_trxs = [Transaction(RawTransaction(utils.mock_raw_trx_data()))]
    async with utils.run_app_with_mock_data(
        transactions=mock_trxs, mock_save=True, mock_path_exists=False
    ) as (app, pilot, mock_save):
        await pilot.press("l")
        await pilot.pause()

        # Check we are on the confirm save changes screen
        assert isinstance(app.screen, SaveChangesConfirmScreen)

        # Now click Yes to save
        await pilot.click("#yes")

        # Should now be on save screen
        assert isinstance(app.screen, SaveOrLoadScreen)
        assert app.screen.mode == "save"

        await pilot.click("#filename")
        await pilot.press("s", "a", "v", "e", ".", "c", "s", "v")
        await pilot.click("#save")

        mock_save.assert_called_once()

        # Should now be on load screen
        assert isinstance(app.screen, SaveOrLoadScreen)
        assert app.screen.mode == "load"

@pytest.mark.asyncio
async def test_load_file_with_existing_data_then_no_clears_data():
    """
    Verifies that when we load with existing data, we are prompted to save changes first.
    Verify that if we select No, the data is cleared and we proceed to load screen.
    """
    # start app with existing data
    mock_trxs = [Transaction(RawTransaction(utils.mock_raw_trx_data()))]
    async with utils.run_app_with_mock_data(transactions=mock_trxs) as (app, pilot, _):
        await pilot.press("l")
        await pilot.pause()

        # Check we are on the confirm save changes screen
        assert isinstance(app.screen, SaveChangesConfirmScreen)

        # Now click No and verify we are on load screen with data cleared
        await pilot.click("#no")
        assert isinstance(app.screen, SaveOrLoadScreen)
        assert app.screen.mode == "load"
        assert not app.transactions  # Data should be cleared

#
# Filter Screen
#

@pytest.mark.asyncio
async def test_filter_screen_escape():
    screen = FilterScreen(categories=["Groceries", "Entertainment"], selected={"All"})
    app = utils.ScreenTestApp(screen)
    async with app.run_test() as pilot:
        await pilot.press("escape")
        assert app.result is None

