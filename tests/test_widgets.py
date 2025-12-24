import pytest
from textual.app import App, ComposeResult
from textual.coordinate import Coordinate
from budget.widgets import TransactionDetails, TransactionTable
from budget.transaction import Transaction
from budget.raw_transaction import RawTransaction
from . import utils

class TransactionDetailsApp(App):
    def compose(self) -> ComposeResult:
        yield TransactionDetails()

class TransactionTableApp(App):
    def compose(self) -> ComposeResult:
        yield TransactionTable()

@pytest.mark.asyncio
async def test_transaction_details_update():
    app = TransactionDetailsApp()
    async with app.run_test() as _:
        # Create a mock transaction
        row = utils.mock_raw_trx_data(Name="Test Item", Amount="-10.00")
        trx = Transaction(RawTransaction(row))
        trx.set_category("Test Category")

        # Update sidebar
        widget = app.query_one(TransactionDetails)
        widget.update_transaction(trx)

        # Check labels
        # Note: Static.render() returns the content
        assert str(app.query_one("#det-desc").render()) == "Test Item"
        assert str(app.query_one("#det-amt").render()) == "-10.0"
        assert str(app.query_one("#det-category").render()) == "Test Category"

@pytest.mark.asyncio
async def test_transaction_details_clear():
    app = TransactionDetailsApp()
    async with app.run_test() as _:
        # Set some data first
        row = utils.mock_raw_trx_data(Name="Test Item")
        trx = Transaction(RawTransaction(row))
        widget = app.query_one(TransactionDetails)
        widget.update_transaction(trx)

        # Clear widget
        widget.clear_transaction()

        # Check labels reset to default
        assert str(app.query_one("#det-desc").render()) == "--"
        assert str(app.query_one("#det-amt").render()) == "--"
        assert str(app.query_one("#det-category").render()) == "--"

@pytest.mark.asyncio
async def test_transaction_table_load_data():
    app = TransactionTableApp()
    async with app.run_test() as _:
        # Create mock transactions
        trxs = []
        for i in range(3):
            row = utils.mock_raw_trx_data(Name=f"Item {i}", Amount=f"-{10+i}.00")
            trxs.append(Transaction(RawTransaction(row)))

        table = app.query_one(TransactionTable)
        table.load_data(trxs)

        for i in range(3):
            assert table.get_cell_at(Coordinate(i, 2)) == f"Item {i}"
            assert table.get_cell_at(Coordinate(i, 3)) == float(f"-{10+i}.0")

@pytest.mark.asyncio
async def test_transaction_table_get_index():
    app = TransactionTableApp()
    async with app.run_test() as _:
        trxs = [Transaction(RawTransaction(utils.mock_raw_trx_data())) for _ in range(3)]
        table = app.query_one(TransactionTable)
        table.load_data(trxs)

        # Default cursor is at 0,0
        assert table.get_current_transaction_index() == 0

        # Move cursor to second row
        table.move_cursor(row=1)
        assert table.get_current_transaction_index() == 1

@pytest.mark.asyncio
async def test_transaction_table_update_row():
    app = TransactionTableApp()
    async with app.run_test() as _:
        row = utils.mock_raw_trx_data(Name="Original Name")
        trx = Transaction(RawTransaction(row), processed_columns={"category": "Old Cat"})
        table = app.query_one(TransactionTable)
        table.load_data([trx])

        # Verify initial state
        assert table.get_cell_at(Coordinate(0, 2)) == "Original Name"
        assert table.get_cell_at(Coordinate(0, 5)) == "Old Cat" # Category is last column

        # Update transaction
        trx.set_category("New Cat")

        table.update_current_row(trx)

        assert table.get_cell_at(Coordinate(0, 5)) == "New Cat"

@pytest.mark.asyncio
async def test_transaction_table_vim_navigation():
    app = TransactionTableApp()
    async with app.run_test() as pilot:
        table = app.query_one(TransactionTable)

        # Load some data
        trxs = [Transaction(RawTransaction(utils.mock_raw_trx_data())) for _ in range(3)]
        table.load_data(trxs)

        # Ensure focus (load_data focuses it, but good to be sure)
        table.focus()

        # Initial pos
        assert table.cursor_coordinate.row == 0

        # Press j -> down
        await pilot.press("j")
        assert table.cursor_coordinate.row == 1

        # Press k -> up
        await pilot.press("k")
        assert table.cursor_coordinate.row == 0
