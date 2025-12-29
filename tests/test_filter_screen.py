import pytest
from textual.widgets import SelectionList
from budget.transaction import Transaction
from budget.raw_transaction import RawTransaction
from budget.screens import FilterScreen
from . import utils

@pytest.mark.asyncio
async def test_filter_screen_select_category():
    # Setup data
    mock_trxs = utils.mock_transactions_for_filtering()

    async with utils.run_app_with_mock_data(mock_trxs) as (app, pilot, _):
        # Trigger filter menu
        app.action_filter_menu()
        await pilot.pause()

        # Should be on FilterScreen
        assert isinstance(app.screen, FilterScreen)

        # Select "Groceries"
        selection_list = app.screen.query_one(SelectionList)

        # "All (Active)" should be selected initially (default)
        assert "All (Active)" in selection_list.selected

        selection_list.deselect("All (Active)")
        selection_list.select("Groceries")

        # Click OK
        await pilot.click("#ok")
        await pilot.pause()

        # Should be back on main screen
        assert not isinstance(app.screen, FilterScreen)

        # Filter should be applied
        assert "Groceries" in app.filter_categories
        assert len(app.filter_categories) == 1
        assert len(app.displayed_transactions) == 1
        assert app.displayed_transactions[0].name() == "T1"

@pytest.mark.asyncio
async def test_filter_screen_select_all():
    t1 = Transaction(RawTransaction(utils.mock_raw_trx_data(Name="T1")))
    t1.set_category("Groceries")

    mock_trxs = [t1]

    async with utils.run_app_with_mock_data(mock_trxs) as (app, pilot, _):
        # Set filter to something else first
        app.filter_categories = {"Groceries"}
        # pylint: disable=protected-access
        app._apply_filters()

        app.action_filter_menu()
        await pilot.pause()

        # Select "All (Active)"
        selection_list = app.screen.query_one(SelectionList)

        # "Groceries" should be selected initially
        assert "Groceries" in selection_list.selected

        selection_list.deselect("Groceries")
        selection_list.select("All (Active)")

        await pilot.click("#ok")
        await pilot.pause()

        assert "All (Active)" in app.filter_categories
        assert len(app.displayed_transactions) == 1
