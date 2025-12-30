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
        self.update_row_by_index(self.cursor_coordinate.row, trx)

    def update_row_by_index(self, index: int, trx: Transaction) -> None:
        for col_index, field in enumerate(FIELDS_TO_DISPLAY):
            value = getattr(trx, field)()
            self.update_cell_at((index, col_index), value)

    def get_current_transaction_index(self) -> int:
        if self.row_count == 0:
            raise ValueError("No rows in the table")
        row_key = self.coordinate_to_cell_key(self.cursor_coordinate).row_key
        return int(row_key.value)

class TransactionDetails(Vertical):
    def compose(self) -> ComposeResult:
        yield Label("TRANSACTION DETAILS", id="sidebar-title")
        yield Label("Date:", classes="detail-label")
        yield Label("--", id="det-date")
        yield Label("Description:", classes="detail-label")
        yield Label("--", id="det-desc")
        yield Label("Amount:", classes="detail-label")
        yield Label("--", id="det-amt")
        yield Label("Category:", classes="detail-label")
        yield Label("--", id="det-category")
        yield Label("Pot Category:", classes="detail-label")
        yield Label("--", id="det-pot-category")
        yield Label("Linked Transaction:", classes="detail-label")
        yield Label("--", id="det-link")
        yield Label("Income:", classes="detail-label")
        yield Label("--", id="det-income")
        yield Label("Status:", classes="detail-label")
        yield Label("--", id="det-status")

    def update_transaction(self, trx: Transaction, linked_trx: Transaction | None = None) -> None:
        self.query_one("#det-date", Static).update(str(trx.date()))
        self.query_one("#det-desc", Static).update(trx.raw.name())
        self.query_one("#det-amt", Static).update(str(trx.raw.amount()))
        self.query_one("#det-category", Static).update(trx.category())
        self.query_one("#det-pot-category", Static).update(trx.pot_category())

        if trx.link() == Transaction.MANUAL_LINK_ID:
            link_text = "Manually Linked"
        elif linked_trx:
            link_text = f"{linked_trx.name()} ({linked_trx.amount()}) - {linked_trx.date()}"
        elif trx.link():
            link_text = f"ID: {trx.link()} (Not found)"
        else:
            link_text = "--"
        self.query_one("#det-link", Static).update(link_text)

        self.query_one("#det-income", Static).update("Yes" if trx.income() else "No")
        self.query_one("#det-status", Static).update(trx.status())

    def clear_transaction(self) -> None:
        self.query_one("#det-date", Static).update("--")
        self.query_one("#det-desc", Static).update("--")
        self.query_one("#det-amt", Static).update("--")
        self.query_one("#det-category", Static).update("--")
        self.query_one("#det-pot-category", Static).update("--")
        self.query_one("#det-link", Static).update("--")
        self.query_one("#det-income", Static).update("--")
        self.query_one("#det-status", Static).update("--")
