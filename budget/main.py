from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable
from textual.containers import Horizontal, Vertical
from textual.binding import Binding
from budget import load_data, save_transactions
from budget.transaction import Transaction
from budget.screens import (
    SaveOrLoadScreen,
    SaveChangesConfirmScreen,
    FilterScreen,
    PotCategoryScreen,
)
from budget.screens.pot_transfer import PotTransferSelectScreen
from budget.widgets import TransactionDetails, TransactionTable

class BudgetApp(App):
    CSS_PATH = "styles/style.tcss"

    BINDINGS = [
        Binding("g", "set_category('Groceries')", "Groceries"),
        Binding("e", "set_category('Entertainment')", "Entertainment"),
        Binding("t", "set_category('Transport')", "Transport"),
        Binding("o", "set_category('Eating Out')", "Eating Out"),
        Binding("n", "set_category('General')", "General"),
        Binding("h", "set_category('Holidays')", "Holidays"),
        Binding("p", "set_category('Pot')", "Pot"),
        Binding("f", "filter_menu", "Filter"),
        Binding("s", "save_transactions", "Save"),
        Binding("l", "load_file", "Load"),
        Binding("c", "clear_row_data", "Clear Row"),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self, file_path: str | None = None):
        super().__init__()
        self.file_path = file_path
        self.transactions = []
        self.displayed_transactions = []
        self.filter_categories = {"All"}
        self.unsaved_changes = False

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            with Vertical(id="left-pane"):
                yield TransactionTable()
            yield TransactionDetails(id="right-pane")
        yield Footer()

    def on_mount(self) -> None:
        if self.file_path:
            self.load_transactions(self.file_path)

    def load_transactions(self, file_path: str) -> None:
        try:
            self.transactions = load_data(file_path)
            self.unsaved_changes = False
        except (ValueError, IOError) as e:
            self.notify(f"Error loading file: {e}", severity="error")
            return

        self._apply_filters()

    def _apply_filters(self) -> None:
        # Normalize filter categories to lowercase for case-insensitive comparison
        # Keep special keys as is or handle them specifically
        filters = {f.lower() for f in self.filter_categories}

        table = self.query_one(TransactionTable)
        cursor_row = table.cursor_coordinate.row

        if "all" in filters:
            self.displayed_transactions = self.transactions
        else:
            self.displayed_transactions = []
            for trx in self.transactions:
                cat = trx.category()
                if "uncategorized" in filters and not cat:
                    self.displayed_transactions.append(trx)
                    continue
                if "categorized" in filters and cat:
                    self.displayed_transactions.append(trx)
                    continue
                if cat.lower() in filters:
                    self.displayed_transactions.append(trx)
                    continue

        table.load_data(self.displayed_transactions)

        # Restore cursor position
        if table.row_count > 0:
            new_row = min(cursor_row, table.row_count - 1)
            table.cursor_coordinate = (new_row, 0)

    def action_filter_menu(self) -> None:
        # Collect unique categories
        categories = [t.category() for t in self.transactions if t.category()]

        def check_filter(result: list[str] | None) -> None:
            if result is not None:
                self.filter_categories = set(result)
                self.notify(f"Filter: {', '.join(self.filter_categories)}")
                self._apply_filters()

        self.push_screen(FilterScreen(categories, self.filter_categories), check_filter)

    def on_data_table_row_highlighted(self, _event: DataTable.RowHighlighted) -> None:
        """Updates the sidebar using the row key from the highlight event."""
        if not self.displayed_transactions:
            return
        trx = self._get_trx_for_cursor()
        self._update_sidebar(trx)

    def action_set_category(self, category: str) -> None:
        table = self.query_one(TransactionTable)
        if table.row_count == 0:
            return

        trx = self._get_trx_for_cursor()
        trx.set_category(category)

        if category == "Pot":
            def check_pot(result: str | None) -> None:
                if result:
                    trx.set_pot_category(result)
                    self.unsaved_changes = True

                    # Now ask for linked transaction
                    def check_link(linked_id: str | None) -> None:
                        if linked_id:
                            trx.set_link(linked_id)
                            linked_trx = self._find_transaction_by_id(linked_id)
                            if linked_trx:
                                linked_trx.set_category("Pot")
                                linked_trx.set_pot_category(result)
                                linked_trx.set_link(trx.id())

                        self._update_row()

                    self.push_screen(PotTransferSelectScreen(trx, self.transactions), check_link)
                else:
                    self._update_row()

            self.push_screen(PotCategoryScreen(), check_pot)
        else:
            trx.set_pot_category("")
            trx.set_link("")
            self.unsaved_changes = True
            self._update_row()

    def action_clear_row_data(self) -> None:
        table = self.query_one(TransactionTable)
        if table.row_count == 0:
            return

        trx = self._get_trx_for_cursor()

        # Handle unlinking if necessary
        if trx.link():
            linked_trx = self._find_transaction_by_id(trx.link())
            if linked_trx:
                linked_trx.set_link("")

        trx.clear_processed_fields()
        self.unsaved_changes = True
        self._update_row()

    def action_save_transactions(self) -> None:
        def check_save(filename: str | None) -> None:
            if filename:
                save_transactions(filename, self.transactions)
                self.unsaved_changes = False
                self.notify(f"Saved to {filename}")

        self.push_screen(SaveOrLoadScreen("save"), check_save)

    def action_load_file(self) -> None:
        if not self.transactions:
            self._show_load_screen()
            return

        def check_clear(response: str) -> None:
            if response == "cancel":
                return

            if response == "yes":
                self._save_and_clear(next_action=self._show_load_screen)
            else:
                self._clear_internal()
                self._show_load_screen()

        self.push_screen(SaveChangesConfirmScreen("Save before loading?"), check_clear)

    def _show_load_screen(self) -> None:
        def check_load(filename: str | None) -> None:
            if filename:
                self.load_transactions(filename)
                self.notify(f"Loaded {filename}")

        self.push_screen(SaveOrLoadScreen("load"), check_load)

    def action_clear_data(self) -> None:
        if not self.transactions:
            self.notify("No data to clear.")
            return

        def check_clear(response: str) -> None:
            if response == "cancel":
                return

            if response == "yes":
                self._save_and_clear()
            else:
                self._clear_internal()

        self.push_screen(SaveChangesConfirmScreen("Save before clearing?"), check_clear)

    def _save_and_clear(self, next_action=None):
        def after_save(filename: str | None) -> None:
            if filename:
                save_transactions(filename, self.transactions)
                self.unsaved_changes = False
                self.notify(f"Saved to {filename}")
                self._clear_internal()
                if next_action:
                    next_action()
            # If cancelled, filename==None, do nothing.

        self.push_screen(SaveOrLoadScreen("save"), after_save)

    def _clear_internal(self):
        self.transactions = []
        self.displayed_transactions = []
        self.query_one(TransactionTable).clear()
        self.query_one(TransactionDetails).clear_transaction()
        self.unsaved_changes = False
        self.notify("Data cleared")

    async def action_quit(self) -> None:
        if self.unsaved_changes:
            def check_quit(response: str) -> None:
                if response == "yes":
                    def after_save(filename: str | None) -> None:
                        if filename:
                            save_transactions(filename, self.transactions)
                            self.unsaved_changes = False
                            self.notify(f"Saved to {filename}")
                            self.exit()

                    self.push_screen(SaveOrLoadScreen("save"), after_save)
                elif response == "no":
                    self.exit()
                # cancel: do nothing

            self.push_screen(SaveChangesConfirmScreen("Save changes before exiting?"), check_quit)
        else:
            self.exit()

    def _get_trx_for_cursor(self) -> Transaction:
        """
        Maps the current cursor position in the table to the corresponding transaction
        """
        table = self.query_one(TransactionTable)
        index = table.get_current_transaction_index()
        return self.displayed_transactions[index]

    def _update_row(self) -> None:
        """
        Reloads the table data to reflect changes and apply filters,
        then updates the sidebar.
        """
        self._apply_filters()

        if self.displayed_transactions:
            trx = self._get_trx_for_cursor()
            self._update_sidebar(trx)
        else:
            self.query_one(TransactionDetails).clear_transaction()

    def _update_sidebar(self, trx: Transaction) -> None:
        linked_trx = None
        if trx.link():
            linked_trx = self._find_transaction_by_id(trx.link())
        self.query_one(TransactionDetails).update_transaction(trx, linked_trx)

    def _find_transaction_by_id(self, trx_id: str) -> Transaction | None:
        for t in self.transactions:
            if t.id() == trx_id:
                return t
        return None
