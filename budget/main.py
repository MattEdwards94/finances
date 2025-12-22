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
        table.add_columns(*EXPECTED_RAW_FIELDS)

        for index, trx in enumerate(trxs):
            table.add_row(
                trx.date, trx.description, trx.amount, trx.category, 
                key=str(index)
            )

        table.focus()
