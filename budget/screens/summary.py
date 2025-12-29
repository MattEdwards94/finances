from textual.app import ComposeResult
from textual.widgets import Label, DataTable, Button
from textual.containers import Vertical, Horizontal, VerticalScroll
from textual.screen import ModalScreen
from textual.binding import Binding
from budget.transaction import Transaction

class SummaryScreen(ModalScreen):
    def __init__(self, transactions: list[Transaction]):
        super().__init__()
        self.transactions = transactions

    def compose(self) -> ComposeResult:
        with Vertical(id="summary-dialog"):
            yield Label("Budget Summary", id="summary-title")
            with VerticalScroll(id="summary-content"):
                yield Label("Category Summary", classes="section-header")
                yield DataTable(id="category-table")

                yield Label("Pot Details", classes="section-header")
                yield Vertical(id="pot-details-container")

            with Horizontal(id="buttons"):
                yield Button("Close", variant="primary", id="close")

    def on_mount(self) -> None:
        self._populate_category_summary()
        self._populate_pot_details()

    def _populate_category_summary(self) -> None:
        table = self.query_one("#category-table", DataTable)
        table.add_columns("Category", "Total Amount")
        table.cursor_type = "row"

        # Calculate sums
        sums = {}
        for trx in self.transactions:
            if trx.excluded():
                continue

            cat = trx.category()
            if not cat:
                cat = "Uncategorized"

            if cat == "Pot":
                continue

            if cat not in sums:
                sums[cat] = 0.0
            sums[cat] += trx.amount()

        # Add to table
        for cat in sorted(sums.keys()):
            amount = sums[cat]
            table.add_row(cat, f"{amount:.2f}")

    def _populate_pot_details(self) -> None:
        container = self.query_one("#pot-details-container", Vertical)

        # Group pot transactions by pot category
        pot_trxs = {}
        for trx in self.transactions:
            if trx.excluded():
                continue

            if trx.category() == "Pot":
                # Filter out "Pot transfer" type
                if trx.type() == "Pot transfer":
                    continue

                pot_cat = trx.pot_category()
                if not pot_cat:
                    pot_cat = "Unassigned Pot"

                if pot_cat not in pot_trxs:
                    pot_trxs[pot_cat] = []
                pot_trxs[pot_cat].append(trx)

        if not pot_trxs:
            container.mount(Label("No pot transactions found."))
            return

        for pot_cat in sorted(pot_trxs.keys()):
            container.mount(Label(f"Pot: {pot_cat}", classes="pot-header"))

            dt = DataTable(classes="pot-table")
            dt.add_columns("Date", "Name", "Amount", "Linked")
            dt.cursor_type = "row"

            for trx in pot_trxs[pot_cat]:
                linked_status = "No"
                if trx.link():
                    linked_status = "Yes"
                    if trx.link() == Transaction.MANUAL_LINK_ID:
                        linked_status = "Manual"

                dt.add_row(
                    str(trx.date()),
                    trx.name(),
                    f"{trx.amount():.2f}",
                    linked_status
                )
            container.mount(dt)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close":
            self.dismiss()

    BINDINGS = [
        Binding("escape", "close", "Close"),
    ]

    def action_close(self) -> None:
        self.dismiss()
