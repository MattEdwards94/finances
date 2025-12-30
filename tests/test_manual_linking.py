import pytest
from textual.coordinate import Coordinate
from budget.transaction import Transaction
from budget.raw_transaction import RawTransaction
from budget.widgets import TransactionTable
from . import utils

@pytest.mark.asyncio
async def test_mark_manual_link_success():
    t1 = Transaction(RawTransaction(utils.mock_raw_trx_data(Name="T1")))
    t1.set_category("Pot")

    mock_trxs = [t1]

    async with utils.run_app_with_mock_data(mock_trxs) as (app, pilot, _):
        # Select row
        table = app.query_one(TransactionTable)
        table.cursor_coordinate = Coordinate(0, 0)

        # Press 'm'
        await pilot.press("m")
        await pilot.pause()

        assert t1.link() == Transaction.MANUAL_LINK_ID

        # We need to check the rendered content of the link label
        # The label id is #det-link
        link_label = app.query_one("#det-link")
        assert str(link_label.render()) == "Manually Linked"

@pytest.mark.asyncio
async def test_mark_manual_link_non_pot_fails():
    t1 = Transaction(RawTransaction(utils.mock_raw_trx_data(Name="T1")))
    t1.set_category("Groceries") # Not Pot

    mock_trxs = [t1]

    async with utils.run_app_with_mock_data(mock_trxs) as (_, pilot, _):
        await pilot.press("m")
        await pilot.pause()

        # Should not be linked
        assert t1.link() == ""

        # Should have shown a notification (hard to test notification directly easily,
        # but we verified state didn't change)

@pytest.mark.asyncio
async def test_mark_manual_link_unlinks_existing():
    t1 = Transaction(RawTransaction(utils.mock_raw_trx_data(Name="T1", **{"Transaction ID": "1"})))
    t1.set_category("Pot")

    t2 = Transaction(RawTransaction(utils.mock_raw_trx_data(Name="T2", **{"Transaction ID": "2"})))
    t2.set_category("Pot")

    # Link them
    t1.set_link("2")
    t2.set_link("1")

    mock_trxs = [t1, t2]

    async with utils.run_app_with_mock_data(mock_trxs) as (app, pilot, _):
        # Select T1
        table = app.query_one(TransactionTable)
        table.cursor_coordinate = Coordinate(0, 0)

        await pilot.press("m")
        await pilot.pause()

        assert t1.link() == Transaction.MANUAL_LINK_ID
        assert t2.link() == "" # Should be unlinked

@pytest.mark.asyncio
async def test_unlinked_pot_filter_excludes_manual():
    t1 = Transaction(RawTransaction(utils.mock_raw_trx_data(Name="T1")))
    t1.set_category("Pot")
    t1.set_link(Transaction.MANUAL_LINK_ID)

    t2 = Transaction(RawTransaction(utils.mock_raw_trx_data(Name="T2")))
    t2.set_category("Pot")
    # t2 is unlinked

    mock_trxs = [t1, t2]

    async with utils.run_app_with_mock_data(mock_trxs) as (app, pilot, _):
        app.filter_categories = {"Unlinked Pot"}
        # pylint: disable=protected-access
        app._apply_filters()
        await pilot.pause()

        # Should only show T2
        assert len(app.displayed_transactions) == 1
        assert app.displayed_transactions[0].name() == "T2"
