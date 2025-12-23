import unittest.mock
import pytest
from textual.app import App
from budget.screens import OverwriteConfirmScreen, ClearDataConfirmScreen, LoadScreen, SaveScreen

class ScreenTestApp(App):
    def __init__(self, screen_to_test):
        super().__init__()
        self.screen_to_test = screen_to_test
        self.result = None

    def on_mount(self):
        def handle_result(result):
            self.result = result
            self.exit()
        self.push_screen(self.screen_to_test, handle_result)

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
async def test_clear_data_confirm_screen_yes():
    screen = ClearDataConfirmScreen()
    app = ScreenTestApp(screen)
    async with app.run_test() as pilot:
        await pilot.click("#yes")
        assert app.result == "yes"

@pytest.mark.asyncio
async def test_clear_data_confirm_screen_no():
    screen = ClearDataConfirmScreen()
    app = ScreenTestApp(screen)
    async with app.run_test() as pilot:
        await pilot.click("#no")
        assert app.result == "no"

@pytest.mark.asyncio
async def test_clear_data_confirm_screen_cancel():
    screen = ClearDataConfirmScreen()
    app = ScreenTestApp(screen)
    async with app.run_test() as pilot:
        await pilot.click("#cancel")
        assert app.result == "cancel"

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
            # We can check if the top screen is OverwriteConfirmScreen
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

            # Should be back on SaveScreen (or rather, SaveScreen is still top)
            # Note: OverwriteConfirmScreen is dismissed, so SaveScreen should be active
            assert isinstance(app.screen, SaveScreen)

            # Result should still be None (not dismissed)
            assert app.result is None
