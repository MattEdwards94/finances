import unittest.mock
import pytest
from textual.widgets import Label
from budget.screens import (
    OverwriteConfirmScreen,
    SaveChangesConfirmScreen,
    LoadScreen,
    SaveScreen,
    FilterScreen
)
from ..utils import ScreenTestApp

#
#   Save changes
#


@pytest.mark.asyncio
async def test_overwrite_confirm_screen_yes():
    screen = OverwriteConfirmScreen()
    app = ScreenTestApp(screen)
    async with app.run_test() as pilot:
        await pilot.click("#yes")
        assert app.result is True

@pytest.mark.asyncio
async def test_overwrite_confirm_screen_no():
    screen = OverwriteConfirmScreen()
    app = ScreenTestApp(screen)
    async with app.run_test() as pilot:
        await pilot.click("#no")
        assert app.result is False

@pytest.mark.asyncio
async def test_save_changes_confirm_screen_yes():
    screen = SaveChangesConfirmScreen()
    app = ScreenTestApp(screen)
    async with app.run_test() as pilot:
        await pilot.click("#yes")
        assert app.result == "yes"

@pytest.mark.asyncio
async def test_save_changes_confirm_screen_no():
    screen = SaveChangesConfirmScreen()
    app = ScreenTestApp(screen)
    async with app.run_test() as pilot:
        await pilot.click("#no")
        assert app.result == "no"

@pytest.mark.asyncio
async def test_save_changes_confirm_screen_cancel():
    screen = SaveChangesConfirmScreen()
    app = ScreenTestApp(screen)
    async with app.run_test() as pilot:
        await pilot.click("#cancel")
        assert app.result == "cancel"

@pytest.mark.asyncio
async def test_save_changes_confirm_screen_message():
    screen = SaveChangesConfirmScreen("Custom Message?")
    app = ScreenTestApp(screen)
    async with app.run_test() as pilot:
        # Use pilot.app.screen to get the active screen
        assert "Custom Message?" in str(pilot.app.screen.query_one("#question", Label).render())
        await pilot.click("#yes")
        assert app.result == "yes"

@pytest.mark.asyncio
async def test_load_screen_cancel():
    screen = LoadScreen()
    app = ScreenTestApp(screen)
    async with app.run_test() as pilot:
        await pilot.click("#cancel")
        assert app.result is None

@pytest.mark.asyncio
async def test_load_screen_load():
    screen = LoadScreen()
    app = ScreenTestApp(screen)
    async with app.run_test() as pilot:
        await pilot.click("#filename")
        await pilot.press("t", "e", "s", "t", ".", "c", "s", "v")
        await pilot.click("#load")
        assert app.result == "test.csv"

@pytest.mark.asyncio
async def test_save_screen_cancel():
    screen = SaveScreen()
    app = ScreenTestApp(screen)
    async with app.run_test() as pilot:
        await pilot.click("#cancel")
        assert app.result is None

@pytest.mark.asyncio
async def test_save_screen_save_new_file():
    # Mock Path.exists to return False
    with unittest.mock.patch("pathlib.Path.exists", return_value=False):
        screen = SaveScreen()
        app = ScreenTestApp(screen)
        async with app.run_test() as pilot:
            await pilot.click("#filename")
            await pilot.press("n", "e", "w", ".", "c", "s", "v")
            await pilot.click("#save")
            assert app.result == "new.csv"

@pytest.mark.asyncio
async def test_save_screen_overwrite_existing_file():
    # Mock Path.exists to return True
    with unittest.mock.patch("pathlib.Path.exists", return_value=True):
        screen = SaveScreen()
        app = ScreenTestApp(screen)
        async with app.run_test() as pilot:
            await pilot.click("#filename")
            await pilot.press("e", "x", "i", "s", "t", "s", ".", "c", "s", "v")
            await pilot.click("#save")

            # Should now be on OverwriteConfirmScreen
            assert isinstance(app.screen, OverwriteConfirmScreen)

            # Click Yes to confirm overwrite
            await pilot.click("#yes")

            # Should return the filename
            assert app.result == "exists.csv"

@pytest.mark.asyncio
async def test_save_screen_overwrite_deny():
    # Mock Path.exists to return True
    with unittest.mock.patch("pathlib.Path.exists", return_value=True):
        screen = SaveScreen()
        app = ScreenTestApp(screen)
        async with app.run_test() as pilot:
            await pilot.click("#filename")
            await pilot.press("e", "x", "i", "s", "t", "s", ".", "c", "s", "v")
            await pilot.click("#save")

            # Should now be on OverwriteConfirmScreen
            assert isinstance(app.screen, OverwriteConfirmScreen)

            # Click No to deny overwrite
            await pilot.click("#no")

            # Should be back on SaveScreen
            assert isinstance(app.screen, SaveScreen)

            # Result should still be None (not dismissed)
            assert app.result is None

# ESC key tests
@pytest.mark.asyncio
async def test_overwrite_confirm_screen_escape():
    screen = OverwriteConfirmScreen()
    app = ScreenTestApp(screen)
    async with app.run_test() as pilot:
        await pilot.press("escape")
        assert app.result is False

@pytest.mark.asyncio
async def test_save_changes_confirm_screen_escape():
    screen = SaveChangesConfirmScreen()
    app = ScreenTestApp(screen)
    async with app.run_test() as pilot:
        await pilot.press("escape")
        assert app.result == "cancel"

@pytest.mark.asyncio
async def test_load_screen_escape():
    screen = LoadScreen()
    app = ScreenTestApp(screen)
    async with app.run_test() as pilot:
        await pilot.press("escape")
        assert app.result is None

@pytest.mark.asyncio
async def test_save_screen_escape():
    screen = SaveScreen()
    app = ScreenTestApp(screen)
    async with app.run_test() as pilot:
        await pilot.press("escape")
        assert app.result is None

@pytest.mark.asyncio
async def test_filter_screen_escape():
    screen = FilterScreen(categories=["Groceries", "Entertainment"], selected={"All"})
    app = ScreenTestApp(screen)
    async with app.run_test() as pilot:
        await pilot.press("escape")
        assert app.result is None
