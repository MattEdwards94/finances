
import contextlib
import unittest.mock
from textual.app import App
from budget.main import BudgetApp
from budget.transaction import Transaction
from budget.raw_transaction import RawTransaction

def mock_raw_trx_data(**overrides):
    """
    Returns a dictionary representing a mock raw transaction data row.
    """
    row = {
        "Transaction ID": " tx123 ",
        "Date": "28/07/2025",
        "Time": "12:34:56",
        "Type": "card",
        "Name": "Coffee Shop",
        "Emoji": "☕",
        "Category": "eating_out",
        "Amount": "-3.50",
        "Currency": "GBP",
        "Local amount": "-3.50",
        "Local currency": "GBP",
        "Notes and #tags": "latte #coffee",
        "Address": "123 Main St",
        "Receipt": "",
        "Description": "Coffee",
        "Category split": "",
        "Money Out": "-3.50",
        "Money In": ""
    }
    row.update(overrides)
    return row

@contextlib.asynccontextmanager
async def run_app_with_mock_data(transactions=None, mock_save=False, mock_path_exists=None):
    """
    Runs the BudgetApp with mocked load_data.

    Args:
        transactions: List of Transaction objects to return from load_data.
        mock_save: If True, mocks save_transactions.
        mock_path_exists: If set (True/False), mocks pathlib.Path.exists.

    Yields:
        (app, pilot, save_mock)
    """
    if transactions is None:
        transactions = []

    with unittest.mock.patch("budget.main.load_data", return_value=transactions):

        stack = contextlib.ExitStack()

        save_mock_obj = None
        if mock_save:
            save_mock_obj = stack.enter_context(
                unittest.mock.patch("budget.main.save_transactions")
            )

        if mock_path_exists is not None:
            stack.enter_context(
                unittest.mock.patch("pathlib.Path.exists", return_value=mock_path_exists)
            )

        with stack:
            app = BudgetApp()
            async with app.run_test() as pilot:
                if transactions:
                    app.load_transactions("dummy.csv")
                yield app, pilot, save_mock_obj

async def perform_save_flow(pilot, filename="save.csv"):
    """Helper to perform the save flow in the UI."""
    # Click Yes (want to save)
    await pilot.click("#yes")
    await pilot.pause()

    # Enter filename and save
    await pilot.click("#filename")
    # We need to type the filename.
    for char in filename:
        await pilot.press(char)
    await pilot.click("#save")
    await pilot.pause()

def mock_transactions_for_filtering():
    """Returns a list of 3 transactions for filtering tests."""
    t1 = Transaction(RawTransaction(mock_raw_trx_data(Name="T1")))
    t1.set_category("Groceries")
    t2 = Transaction(RawTransaction(mock_raw_trx_data(Name="T2")))
    t2.set_category("Entertainment")
    t3 = Transaction(RawTransaction(mock_raw_trx_data(Name="T3")))
    t3.set_category("Transport")
    return [t1, t2, t3]

class ScreenTestApp(App):
    """
    A helper class to create an app for a specific screen for testing
    
    Testing for Textual requires an App, not just a widget, so this class
    simply wraps the widget in an "App"
    """
    def __init__(self, screen_to_test):
        super().__init__()
        self.screen_to_test = screen_to_test
        self.result = None

    def on_mount(self):
        def handle_result(result):
            self.result = result
            self.exit()
        self.push_screen(self.screen_to_test, handle_result)
