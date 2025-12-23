from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Label
from textual.containers import Horizontal, Vertical
from textual.binding import Binding
from budget import load_data
from budget.transaction import Transaction

FIELDS_TO_DISPLAY = [
    "date",
    "type",
    "name",
    "amount",
    "notes",
    "category",
]

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
    ]

    def __init__(self, file_path: str):
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
        self.transactions = load_data(self.file_path)
        table.add_columns("Date", "Type", "Name", "Amount", "Notes")
        table.add_column("Category", width=20)

        for index, trx in enumerate(self.transactions):
            fields = [getattr(trx, field)() for field in FIELDS_TO_DISPLAY]
            table.add_row(
                *fields,
                key=str(index)
            )

        table.focus()

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        """Updates the sidebar using the row key from the highlight event."""
        trx = self._get_trx_for_cursor()
        self._update_sidebar(trx)

    def action_set_category(self, category: str) -> None:
        table = self.query_one(DataTable)
        if table.row_count == 0:
            return

        trx = self._get_trx_for_cursor()
        trx.set_category(category)

        self._update_row()

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
        coordinate = table.cursor_coordinate
        trx = self._get_trx_for_cursor()
        for col_index, field in enumerate(FIELDS_TO_DISPLAY):
            value = getattr(trx, field)()
            table.update_cell_at((table.cursor_coordinate.row, col_index), value) # type: ignore

        self._update_sidebar(trx)

    def _update_sidebar(self, trx: Transaction) -> None:
        self.query_one("#det-desc").update(trx.raw.name())
        self.query_one("#det-amt").update(str(trx.raw.amount()))
        self.query_one("#det-category").update(trx.category())
        self.query_one("#det-status").update(trx.status())

