import pytest
from budget.transaction import Transaction
from budget.raw_transaction import RawTransaction
from budget.screens.summary import SummaryScreen
from textual.widgets import DataTable, Label
from .. import utils

@pytest.mark.asyncio
async def test_summary_screen_category_sums():
    # Setup data
    t1 = Transaction(RawTransaction(utils.mock_raw_trx_data(Name="T1", Amount="-10.00")))
    t1.set_category("Groceries")
    
    t2 = Transaction(RawTransaction(utils.mock_raw_trx_data(Name="T2", Amount="-20.00")))
    t2.set_category("Groceries")
    
    t3 = Transaction(RawTransaction(utils.mock_raw_trx_data(Name="T3", Amount="-5.00")))
    t3.set_category("Transport")
    
    t4 = Transaction(RawTransaction(utils.mock_raw_trx_data(Name="T4", Amount="-100.00")))
    t4.set_category("Pot") # Should be ignored in category summary
    
    t5 = Transaction(RawTransaction(utils.mock_raw_trx_data(Name="T5", Amount="-50.00")))
    t5.set_excluded(True) # Should be ignored
    
    transactions = [t1, t2, t3, t4, t5]
    
    screen = SummaryScreen(transactions)
    app = utils.ScreenTestApp(screen)
    
    async with app.run_test() as pilot:
        table = app.screen.query_one("#category-table", DataTable)
        
        # Check rows
        # Groceries: -30.00
        # Transport: -5.00
        
        # DataTable stores data as rows. We can iterate or check specific cells.
        # Assuming sorted by category name.
        
        assert table.row_count == 2
        
        # Row 0: Groceries
        assert table.get_cell_at((0, 0)) == "Groceries"
        assert table.get_cell_at((0, 1)) == "-30.00"
        
        # Row 1: Transport
        assert table.get_cell_at((1, 0)) == "Transport"
        assert table.get_cell_at((1, 1)) == "-5.00"

@pytest.mark.asyncio
async def test_summary_screen_pot_details():
    # Setup data
    # Pot 1: Holiday
    t1 = Transaction(RawTransaction(utils.mock_raw_trx_data(Name="Flight", Amount="-200.00", Date="2023-01-01", **{"Transaction ID": "1"})))
    t1.set_category("Pot")
    t1.set_pot_category("Holiday")
    t1.set_link("LINK1")
    
    # Pot 2: Car
    t2 = Transaction(RawTransaction(utils.mock_raw_trx_data(Name="Fuel", Amount="-50.00", Date="2023-01-02", **{"Transaction ID": "2"})))
    t2.set_category("Pot")
    t2.set_pot_category("Car")
    # Unlinked
    
    # Pot Transfer (should be ignored)
    t3 = Transaction(RawTransaction(utils.mock_raw_trx_data(Name="Transfer", Amount="100.00", Type="Pot transfer", **{"Transaction ID": "3"})))
    t3.set_category("Pot")
    t3.set_pot_category("Holiday")
    
    # Manual Link
    t4 = Transaction(RawTransaction(utils.mock_raw_trx_data(Name="Hotel", Amount="-150.00", Date="2023-01-03", **{"Transaction ID": "4"})))
    t4.set_category("Pot")
    t4.set_pot_category("Holiday")
    t4.set_link(Transaction.MANUAL_LINK_ID)
    
    transactions = [t1, t2, t3, t4]
    
    screen = SummaryScreen(transactions)
    app = utils.ScreenTestApp(screen)
    
    async with app.run_test() as pilot:
        # Check Pot Headers
        # We expect "Pot: Car" and "Pot: Holiday" labels
        
        labels = [str(w.render()) for w in app.screen.query(".pot-header")]
        assert "Pot: Car" in labels[0]
        assert "Pot: Holiday" in labels[1]
        
        # Check Tables
        tables = list(app.screen.query(".pot-table"))
        assert len(tables) == 2
        
        # Table 0: Car (1 transaction)
        dt_car = tables[0]
        assert dt_car.row_count == 1
        assert dt_car.get_cell_at((0, 1)) == "Fuel"
        assert dt_car.get_cell_at((0, 3)) == "No" # Linked status
        
        # Table 1: Holiday (2 transactions, t3 ignored)
        dt_holiday = tables[1]
        assert dt_holiday.row_count == 2
        
        # T1: Flight, Linked
        # T4: Hotel, Manual
        # Order depends on list order? The code iterates `pot_trxs[pot_cat]`.
        # Since we appended in order, T1 then T4.
        
        assert dt_holiday.get_cell_at((0, 1)) == "Flight"
        assert dt_holiday.get_cell_at((0, 3)) == "Yes"
        
        assert dt_holiday.get_cell_at((1, 1)) == "Hotel"
        assert dt_holiday.get_cell_at((1, 3)) == "Manual"

@pytest.mark.asyncio
async def test_summary_screen_manual_link_toggle():
    # Setup data
    t1 = Transaction(RawTransaction(utils.mock_raw_trx_data(Name="T1", Transaction_ID="1")))
    t1.set_category("Pot")
    t1.set_pot_category("TestPot")
    
    transactions = [t1]
    
    screen = SummaryScreen(transactions)
    app = utils.ScreenTestApp(screen)
    
    async with app.run_test() as pilot:
        # Find the table
        table = app.screen.query_one(".pot-table", DataTable)
        
        # Focus table and select row
        table.focus()
        table.cursor_coordinate = (0, 0)
        
        # Initial state: No
        assert table.get_cell_at((0, 3)) == "No"
        assert t1.link() == ""
        
        # Press 'm'
        await pilot.press("m")
        await pilot.pause()
        
        # Should be Manual
        assert table.get_cell_at((0, 3)) == "Manual"
        assert t1.link() == Transaction.MANUAL_LINK_ID
        
        # Press 'm' again to toggle off
        await pilot.press("m")
        await pilot.pause()
        
        # Should be No
        assert table.get_cell_at((0, 3)) == "No"
        assert t1.link() == ""
