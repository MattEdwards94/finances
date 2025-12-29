import unittest.mock
import pytest
from textual.widgets import Label
from budget.screens import (
    OverwriteConfirmScreen,
    SaveChangesConfirmScreen,
    SaveOrLoadScreen,
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
    screen = SaveOrLoadScreen(mode="load")
    app = ScreenTestApp(screen)
    async with app.run_test() as pilot:
        await pilot.click("#cancel")
        assert app.result is None

@pytest.mark.asyncio
async def test_load_screen_load():
    screen = SaveOrLoadScreen(mode="load")
    app = ScreenTestApp(screen)
    async with app.run_test() as pilot:
        await pilot.click("#filename")
        await pilot.press("t", "e", "s", "t", ".", "c", "s", "v")
        await pilot.click("#load")
        assert app.result == "test.csv"

@pytest.mark.asyncio
async def test_save_screen_cancel():
    screen = SaveOrLoadScreen(mode="save")
    app = ScreenTestApp(screen)
    async with app.run_test() as pilot:
        await pilot.click("#cancel")
        assert app.result is None

@pytest.mark.asyncio
async def test_save_screen_save_new_file():
    # Mock Path.exists to return False
    with unittest.mock.patch("pathlib.Path.exists", return_value=False):
        screen = SaveOrLoadScreen(mode="save")
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
        screen = SaveOrLoadScreen(mode="save")
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
        screen = SaveOrLoadScreen(mode="save")
        app = ScreenTestApp(screen)
        async with app.run_test() as pilot:
            await pilot.click("#filename")
            await pilot.press("e", "x", "i", "s", "t", "s", ".", "c", "s", "v")
            await pilot.click("#save")

            # Should now be on OverwriteConfirmScreen
            assert isinstance(app.screen, OverwriteConfirmScreen)

            # Click No to deny overwrite
            await pilot.click("#no")

            # Should be back on save screen
            assert isinstance(app.screen, SaveOrLoadScreen)
            assert app.screen.mode == "save"

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
    screen = SaveOrLoadScreen(mode="load")
    app = ScreenTestApp(screen)
    async with app.run_test() as pilot:
        await pilot.press("escape")
        assert app.result is None

@pytest.mark.asyncio
async def test_save_screen_escape():
    screen = SaveOrLoadScreen(mode="save")
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
