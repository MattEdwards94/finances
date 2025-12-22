from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Static, Label
from textual.containers import Horizontal, Vertical
from budget import load_data, EXPECTED_RAW_FIELDS

class BudgetApp(App):
    CSS_PATH = "styles/style.tcss"

    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            with Vertical(id="left-pane"):
                yield DataTable(zebra_stripes=True)
            with Vertical(id="right-pane"):
                yield Label("TRANSACTION DETAILS", id="sidebar-title")
                yield Label("Description:", classes="detail-label")
                yield Label("--", id="det-desc")
                yield Label("Amount:", classes="detail-label")
                yield Label("--", id="det-amt")
                yield Label("Status:", classes="detail-label")
                yield Label("--", id="det-status")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        trxs = load_data(self.file_path)
        table.add_columns("Date", "Type", "Name", "Amount", "Notes")

        for index, trx in enumerate(trxs):
            table.add_row(
                trx.date(), trx.type(), trx.name(), trx.amount(), trx.notes(),
                key=str(index)
            )

        table.focus()

    def on_data_table_cell_highlighted(self, event: DataTable.CellHighlighted) -> None:
        """Updates the sidebar using the coordinate from the highlight event."""
        table = self.query_one(DataTable)
        # Get the row data using the row index from the coordinate
        row_data = table.get_row_at(event.coordinate.row)
        
        self.query_one("#det-desc").update(str(row_data[2]))
        self.query_one("#det-amt").update(str(row_data[3]))
        self.query_one("#det-status").update(str(row_data[1]))

