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
                yield Label("Income Summary", classes="section-header")
                yield DataTable(id="income-table")

                yield Label("Category Summary", classes="section-header")
                yield DataTable(id="category-table")

                yield Label("Pot Details", classes="section-header")
                yield Vertical(id="pot-details-container")

            with Horizontal(id="buttons"):
                yield Button("Close", variant="primary", id="close")

    def on_mount(self) -> None:
        self._populate_income_summary()
        self._populate_category_summary()
        self._populate_pot_details()

    def _populate_income_summary(self) -> None:
        table = self.query_one("#income-table", DataTable)
        table.add_columns("Date", "Name", "Amount")
        table.cursor_type = "row"

        income_trxs = [t for t in self.transactions if t.income() and not t.excluded()]

        total_income = 0.0
        for trx in income_trxs:
            table.add_row(str(trx.date()), trx.name(), f"{trx.amount():.2f}")
            total_income += trx.amount()

        table.add_row("Total", "", f"{total_income:.2f}")

    def _populate_category_summary(self) -> None:
        table = self.query_one("#category-table", DataTable)
        table.add_columns("Category", "Total Amount")
        table.cursor_type = "row"

        # Calculate sums
        sums = {}
        for trx in self.transactions:
            if trx.excluded():
                continue

            if trx.income():
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
            dt.add_column("Date", key="Date")
            dt.add_column("Name", key="Name")
            dt.add_column("Amount", key="Amount")
            dt.add_column("Linked", key="Linked")
            dt.add_column("Notes", key="Notes")
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
                    linked_status,
                    trx.notes(),
                    key=trx.id()
                )
            container.mount(dt)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        # Optional: maybe show details or something?
        pass

    def on_key(self, event) -> None:
        if event.key == "m":
            self._handle_manual_link_toggle()

    def _handle_manual_link_toggle(self) -> None:
        # Find which table is focused
        focused = self.app.focused
        if not isinstance(focused, DataTable) or "pot-table" not in focused.classes:
            return

        cursor_row = focused.cursor_coordinate.row
        if cursor_row < 0 or cursor_row >= focused.row_count:
            return

        # Get transaction ID from row key
        # We need to get the row key for the cursor position
        # DataTable.coordinate_to_cell_key returns CellKey(row_key, column_key)
        try:
            row_key = focused.coordinate_to_cell_key(focused.cursor_coordinate).row_key
            trx_id = row_key.value
        except Exception: # pylint: disable=broad-exception-caught
            return

        # Find transaction
        trx = next((t for t in self.transactions if t.id() == trx_id), None)
        if not trx:
            return

        # Toggle manual link
        if trx.link() == Transaction.MANUAL_LINK_ID:
            trx.set_link("")
            self.notify("Manual link removed")
        else:
            # If linked to something else, unlink it first?
            # Consistent with main screen behavior:
            if trx.link():
                # We need to find the linked transaction to clear its link
                linked_trx = next((t for t in self.transactions if t.id() == trx.link()), None)
                if linked_trx:
                    linked_trx.set_link("")

            trx.set_link(Transaction.MANUAL_LINK_ID)
            self.notify("Marked as manually linked")

        # Refresh the specific row in the table
        linked_status = "No"
        if trx.link():
            linked_status = "Yes"
            if trx.link() == Transaction.MANUAL_LINK_ID:
                linked_status = "Manual"

        # Update the "Linked" column (index 3)
        focused.update_cell(row_key, "Linked", linked_status)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close":
            self.dismiss()

    BINDINGS = [
        Binding("escape", "close", "Close"),
    ]

    def action_close(self) -> None:
        self.dismiss()
