from textual.app import ComposeResult
from textual.widgets import Label, DataTable, Button
from textual.containers import Vertical, Horizontal
from textual.screen import ModalScreen
from textual.binding import Binding
from budget.transaction import Transaction

class PotTransferSelectScreen(ModalScreen[str | None]):
    def __init__(self, current_transaction: Transaction, all_transactions: list[Transaction]):
        super().__init__()
        self.current_transaction = current_transaction
        self.candidates = self._get_candidates(all_transactions)

    def _get_candidates(self, all_transactions: list[Transaction]) -> list[Transaction]:
        # Filter out the current transaction itself and ensure type is "Pot transfer"
        candidates = [
            t for t in all_transactions
            if t.id() != self.current_transaction.id() and t.type() == "Pot transfer"
        ]

        # Sort by closeness to the absolute amount
        target_amount = abs(self.current_transaction.amount())
        candidates.sort(key=lambda t: abs(abs(t.amount()) - target_amount))

        return candidates

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            label_text = (f"Select transaction to link to: {self.current_transaction.name()} "
                          f"({self.current_transaction.amount()})")
            yield Label(label_text, id="question")
            yield DataTable(id="candidate_table")
            with Horizontal(classes="buttons"):
                yield Button("Skip/Cancel", variant="default", id="cancel")

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.add_columns("Date", "Name", "Amount", "Category")

        for trx in self.candidates:
            table.add_row(
                str(trx.date()),
                trx.name(),
                str(trx.amount()),
                trx.category(),
                key=trx.id()
            )

        table.focus()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        self.dismiss(event.row_key.value)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.dismiss(None)

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
    ]

    def action_cursor_down(self) -> None:
        self.query_one(DataTable).action_cursor_down()

    def action_cursor_up(self) -> None:
        self.query_one(DataTable).action_cursor_up()

    def action_cancel(self) -> None:
        self.dismiss(None)
