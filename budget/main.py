from pathlib import Path
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Label, Static, Input, Button, DirectoryTree
from textual.containers import Horizontal, Vertical
from textual.binding import Binding
from textual.screen import ModalScreen
from budget import load_data, save_transactions
from budget.transaction import Transaction

FIELDS_TO_DISPLAY = [
    "date",
    "type",
    "name",
    "amount",
    "notes",
    "category",
]

class OverwriteConfirmScreen(ModalScreen[bool]):
    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label("File already exists. Overwrite?", id="question")
            with Horizontal(id="buttons"):
                yield Button("Yes", variant="primary", id="yes")
                yield Button("No", variant="error", id="no")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "yes":
            self.dismiss(True)
        else:
            self.dismiss(False)

class ClearDataConfirmScreen(ModalScreen[str]):
    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label("Save before clearing?", id="question")
            with Horizontal(id="buttons"):
                yield Button("Yes", variant="primary", id="yes")
                yield Button("No", variant="error", id="no")
                yield Button("Cancel", variant="default", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "yes":
            self.dismiss("yes")
        elif event.button.id == "no":
            self.dismiss("no")
        else:
            self.dismiss("cancel")

class LoadScreen(ModalScreen[str]):
    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            with Horizontal(classes="header"):
                yield Label("Select file to load:", id="question")
                yield Button("Up", id="up", variant="primary")
            yield DirectoryTree(str(Path.home() / "budget_data"))
            yield Input(placeholder="Enter filename", id="filename")
            with Horizontal(id="buttons"):
                yield Button("Load", variant="primary", id="load")
                yield Button("Cancel", variant="error", id="cancel")

    def on_mount(self) -> None:
        self.query_one(Input).focus()

    def on_directory_tree_directory_selected(self, event: DirectoryTree.DirectorySelected) -> None:
        input_widget = self.query_one(Input)
        input_widget.value = str(event.path) + "/"
        input_widget.focus()

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        input_widget = self.query_one(Input)
        input_widget.value = str(event.path)
        input_widget.focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "load":
            input_widget = self.query_one(Input)
            self.dismiss(input_widget.value)
        elif event.button.id == "up":
            tree = self.query_one(DirectoryTree)
            current = Path(tree.path).resolve()
            parent = current.parent
            tree.path = str(parent)
            tree.reload()
        elif event.button.id == "cancel":
            self.dismiss(None)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.dismiss(event.value)

class SaveScreen(ModalScreen[str]):
    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            with Horizontal(classes="header"):
                yield Label("Select folder:", id="question")
                yield Button("Up", id="up", variant="primary")
            yield DirectoryTree(str(Path.home() / "budget_data"))
            yield Input(placeholder="Enter filename", id="filename")
            with Horizontal(id="buttons"):
                yield Button("Save", variant="primary", id="save")
                yield Button("Cancel", variant="error", id="cancel")

    def on_mount(self) -> None:
        self.query_one(Input).focus()

    def on_directory_tree_directory_selected(self, event: DirectoryTree.DirectorySelected) -> None:
        input_widget = self.query_one(Input)
        input_widget.value = str(event.path) + "/"
        input_widget.focus()

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        input_widget = self.query_one(Input)
        input_widget.value = str(event.path)
        input_widget.focus()

    def handle_save(self):
        input_widget = self.query_one(Input)
        filename = input_widget.value
        if not filename:
            return

        if Path(filename).exists():
            def check_overwrite(should_overwrite: bool) -> None:
                if should_overwrite:
                    self.dismiss(filename)
                # else do nothing, stay on SaveScreen

            self.app.push_screen(OverwriteConfirmScreen(), check_overwrite)
        else:
            self.dismiss(filename)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            self.handle_save()
        elif event.button.id == "up":
            tree = self.query_one(DirectoryTree)
            current = Path(tree.path).resolve()
            parent = current.parent
            tree.path = str(parent)
            tree.reload()
        elif event.button.id == "cancel":
            self.dismiss(None)

    def on_input_submitted(self, _event: Input.Submitted) -> None:
        self.handle_save()

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
        Binding("s", "save_transactions", "Save"),
        Binding("l", "load_file", "Load"),
        Binding("c", "clear_data", "Clear"),
    ]

    def __init__(self, file_path: str | None = None):
        super().__init__()
        self.file_path = file_path
        self.transactions = []

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            with Vertical(id="left-pane"):
                yield DataTable(zebra_stripes=True, cursor_type="row")
            with Vertical(id="right-pane"):
                yield Label("TRANSACTION DETAILS", id="sidebar-title")
                yield Label("Description:", classes="detail-label")
                yield Label("--", id="det-desc")
                yield Label("Amount:", classes="detail-label")
                yield Label("--", id="det-amt")
                yield Label("Category:", classes="detail-label")
                yield Label("--", id="det-category")
                yield Label("Status:", classes="detail-label")
                yield Label("--", id="det-status")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("Date", "Type", "Name", "Amount", "Notes")
        table.add_column("Category", width=20)

        if self.file_path:
            self.load_transactions(self.file_path)

    def load_transactions(self, file_path: str) -> None:
        table = self.query_one(DataTable)
        try:
            self.transactions = load_data(file_path)
        except Exception as e:
            self.notify(f"Error loading file: {e}", severity="error")
            return

        table.clear()
        for index, trx in enumerate(self.transactions):
            fields = [getattr(trx, field)() for field in FIELDS_TO_DISPLAY]
            table.add_row(
                *fields,
                key=str(index)
            )

        table.focus()

    def on_data_table_row_highlighted(self, _event: DataTable.RowHighlighted) -> None:
        """Updates the sidebar using the row key from the highlight event."""
        if not self.transactions:
            return
        trx = self._get_trx_for_cursor()
        self._update_sidebar(trx)

    def action_set_category(self, category: str) -> None:
        table = self.query_one(DataTable)
        if table.row_count == 0:
            return

        trx = self._get_trx_for_cursor()
        trx.set_category(category)

        self._update_row()

    def action_save_transactions(self) -> None:
        def check_save(filename: str | None) -> None:
            if filename:
                save_transactions(filename, self.transactions)
                self.notify(f"Saved to {filename}")

        self.push_screen(SaveScreen(), check_save)

    def action_load_file(self) -> None:
        if self.transactions:
            self.notify("Data already loaded. Please clear data first.", severity="error")
            return

        def check_load(filename: str | None) -> None:
            if filename:
                self.load_transactions(filename)
                self.notify(f"Loaded {filename}")

        self.push_screen(LoadScreen(), check_load)

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

        self.push_screen(ClearDataConfirmScreen(), check_clear)

    def _save_and_clear(self):
        def after_save(filename: str | None) -> None:
            if filename:
                save_transactions(filename, self.transactions)
                self.notify(f"Saved to {filename}")
                self._clear_internal()
            # If cancelled, filename==None, do nothing.

        self.push_screen(SaveScreen(), after_save)

    def _clear_internal(self):
        self.transactions = []
        self.query_one(DataTable).clear()
        self.query_one("#det-desc", Static).update("--")
        self.query_one("#det-amt", Static).update("--")
        self.query_one("#det-category", Static).update("--")
        self.query_one("#det-status", Static).update("--")
        self.notify("Data cleared")

    def _get_trx_for_cursor(self) -> Transaction:
        """
        Maps the current cursor position in the table to the corresponding transaction
        """
        table = self.query_one(DataTable)
        if table.row_count == 0:
            raise ValueError("No rows in the table")

        # Note: The row_key relates to the transaction index in self.transactions, which may
        # not be the same as the cursor.row if the order has changed due to e.g. sorting output
        row_key = table.coordinate_to_cell_key(table.cursor_coordinate).row_key
        index = int(row_key.value) # type: ignore

        return self.transactions[index]

    def _update_row(self) -> None:
        """
        Reloads the current row in the table to reflect any changes made to the
        underlying transaction, and updates the sidebar.
        """
        table = self.query_one(DataTable)
        trx = self._get_trx_for_cursor()
        for col_index, field in enumerate(FIELDS_TO_DISPLAY):
            value = getattr(trx, field)()
            table.update_cell_at((table.cursor_coordinate.row, col_index), value) # type: ignore

        self._update_sidebar(trx)

    def _update_sidebar(self, trx: Transaction) -> None:
        self.query_one("#det-desc", Static).update(trx.raw.name())
        self.query_one("#det-amt", Static).update(str(trx.raw.amount()))
        self.query_one("#det-category", Static).update(trx.category())
        self.query_one("#det-status", Static).update(trx.status())
