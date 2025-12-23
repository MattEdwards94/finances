from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Label
from textual.containers import Horizontal, Vertical
from textual.binding import Binding
from budget import load_data

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
            table.add_row(
                trx.date(), trx.type(), trx.name(), trx.amount(), trx.notes(), trx.category(),
                key=str(index)
            )

        table.focus()

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        """Updates the sidebar using the row key from the highlight event."""
        table = self.query_one(DataTable)
        # Get the row data using the row key
        row_data = table.get_row(event.row_key)

        self.query_one("#det-desc").update(str(row_data[2]))
        self.query_one("#det-amt").update(str(row_data[3]))
        self.query_one("#det-category").update(str(row_data[5]))
        self.query_one("#det-status").update(str(row_data[1]))

    def action_set_category(self, category: str) -> None:
        table = self.query_one(DataTable)
        if table.row_count == 0:
            return

        # Get the current row key
        coordinate = table.cursor_coordinate
        row_key = table.coordinate_to_cell_key(coordinate).row_key

        # Update the transaction
        index = int(row_key.value)
        self.transactions[index].set_category(category)

        # Update the table
        # Category is the 6th column (index 5)
        table.update_cell_at((coordinate.row, 5), category)

        # Update the sidebar
        self.query_one("#det-category").update(category)
