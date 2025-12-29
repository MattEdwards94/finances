import pytest
from budget.main import BudgetApp
from budget.screens import SaveChangesConfirmScreen, SaveOrLoadScreen

@pytest.mark.asyncio
async def test_exit_with_changes_prompt():
    app = BudgetApp()
    app.unsaved_changes = True

    async with app.run_test() as pilot:
        # Trigger quit
        await app.action_quit()
        await pilot.pause()

        # Should show SaveChangesConfirmScreen
        assert isinstance(app.screen, SaveChangesConfirmScreen)
        # Check message
        assert "Save changes before exiting?" in str(
            app.screen.query_one("#question").render()
        )

        # Click Cancel
        await pilot.click("#cancel")
        await pilot.pause()

        # Should be back to main screen (not SaveChangesConfirmScreen)
        assert not isinstance(app.screen, SaveChangesConfirmScreen)
        # App should still be running

@pytest.mark.asyncio
async def test_exit_with_changes_save():
    app = BudgetApp()
    app.unsaved_changes = True

    async with app.run_test() as pilot:
        await app.action_quit()
        await pilot.pause()

        assert isinstance(app.screen, SaveChangesConfirmScreen)
        await pilot.click("#yes")
        await pilot.pause()

        # Should show SaveScreen
        assert isinstance(app.screen, SaveOrLoadScreen)
        assert app.screen.mode == "save"
