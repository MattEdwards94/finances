import pytest
from budget.transaction import Transaction
from budget.raw_transaction import RawTransaction
from budget.screens.summary import SummaryScreen
from budget.widgets import TransactionTable, TransactionDetails
from textual.widgets import DataTable
from .. import utils

@pytest.mark.asyncio
async def test_toggle_income_action():
    t1 = Transaction(RawTransaction(utils.mock_raw_trx_data(Name="Salary", Amount="2000.00")))
    
    mock_trxs = [t1]
    
    async with utils.run_app_with_mock_data(mock_trxs) as (app, pilot, _):
        # Select row
        table = app.query_one(TransactionTable)
        table.cursor_coordinate = (0, 0)
        
        # Initial state
        assert t1.income() is False
        
        await pilot.press("i")
        await pilot.pause()
        
        assert t1.income() is True
        
        # Verify sidebar
        income_label = app.query_one("#det-income")
        assert str(income_label.render()) == "Yes"
        
        # Toggle back
        await pilot.press("i")
        await pilot.pause()
        
        assert t1.income() is False
        assert str(income_label.render()) == "No"

@pytest.mark.asyncio
async def test_summary_screen_income_section():
    # Setup data
    t1 = Transaction(RawTransaction(utils.mock_raw_trx_data(Name="Salary", Amount="2000.00")))
    t1.set_income(True)
    
    t2 = Transaction(RawTransaction(utils.mock_raw_trx_data(Name="Groceries", Amount="-50.00")))
    t2.set_category("Groceries")
    # Not income
    
    transactions = [t1, t2]
    
    screen = SummaryScreen(transactions)
    app = utils.ScreenTestApp(screen)
    
    async with app.run_test() as pilot:
        # Check Income Table
        income_table = app.screen.query_one("#income-table", DataTable)
        
        # Should have 1 row + total row = 2 rows
        assert income_table.row_count == 2
        
        # Row 0: Salary
        assert income_table.get_cell_at((0, 1)) == "Salary"
        assert income_table.get_cell_at((0, 2)) == "2000.00"
        
        # Row 1: Total
        assert income_table.get_cell_at((1, 0)) == "Total"
        assert income_table.get_cell_at((1, 2)) == "2000.00"
        
        # Check Category Table (should exclude income)
        category_table = app.screen.query_one("#category-table", DataTable)
        
        # Should have 1 row (Groceries)
        assert category_table.row_count == 1
        assert category_table.get_cell_at((0, 0)) == "Groceries"
        assert category_table.get_cell_at((0, 1)) == "-50.00"
