from textual.app import ComposeResult
from textual.widgets import Label, Static, DataTable
from textual.containers import Vertical
from textual.binding import Binding
from budget.transaction import Transaction

FIELDS_TO_DISPLAY = [
    "date",
    "type",
    "name",
    "amount",
    "notes",
    "category",
    "pot_category",
]

class TransactionTable(DataTable):
    BINDINGS = [
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
    ]

    def on_mount(self) -> None:
        self.zebra_stripes = True
        self.cursor_type = "row"
        self.add_columns("Date", "Type", "Name", "Amount", "Notes")
        self.add_column("Category", width=20)
        self.add_column("Pot Category", width=20)

    def load_data(self, transactions: list[Transaction]) -> None:
        self.clear()
        for index, trx in enumerate(transactions):
            fields = [getattr(trx, field)() for field in FIELDS_TO_DISPLAY]
            self.add_row(
                *fields,
                key=str(index)
            )
        self.focus()

    def update_current_row(self, trx: Transaction) -> None:
        for col_index, field in enumerate(FIELDS_TO_DISPLAY):
            value = getattr(trx, field)()
            self.update_cell_at((self.cursor_coordinate.row, col_index), value)

    def get_current_transaction_index(self) -> int:
        if self.row_count == 0:
            raise ValueError("No rows in the table")
        row_key = self.coordinate_to_cell_key(self.cursor_coordinate).row_key
        return int(row_key.value)

class TransactionDetails(Vertical):
    def compose(self) -> ComposeResult:
        yield Label("TRANSACTION DETAILS", id="sidebar-title")
        yield Label("Description:", classes="detail-label")
        yield Label("--", id="det-desc")
        yield Label("Amount:", classes="detail-label")
        yield Label("--", id="det-amt")
        yield Label("Category:", classes="detail-label")
        yield Label("--", id="det-category")
        yield Label("Pot Category:", classes="detail-label")
        yield Label("--", id="det-pot-category")
        yield Label("Status:", classes="detail-label")
        yield Label("--", id="det-status")

    def update_transaction(self, trx: Transaction) -> None:
        self.query_one("#det-desc", Static).update(trx.raw.name())
        self.query_one("#det-amt", Static).update(str(trx.raw.amount()))
        self.query_one("#det-category", Static).update(trx.category())
        self.query_one("#det-pot-category", Static).update(trx.pot_category())
        self.query_one("#det-status", Static).update(trx.status())

    def clear_transaction(self) -> None:
        self.query_one("#det-desc", Static).update("--")
        self.query_one("#det-amt", Static).update("--")
        self.query_one("#det-category", Static).update("--")
        self.query_one("#det-pot-category", Static).update("--")
        self.query_one("#det-status", Static).update("--")
