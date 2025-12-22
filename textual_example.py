from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Static, Label
from textual.containers import Horizontal, Vertical
from textual.binding import Binding

# Mock Data: [Date, Description, Amount, Category]
TX_DATA = [
    ("2023-10-01", "Tesco", "-£45.20", "Uncategorized"),
    ("2023-10-02", "Pot Transfer: Bills", "-£100.00", "Pot Spend"),
    ("2023-10-02", "Shell Garage", "-£60.00", "Uncategorized"),
    ("2023-10-03", "Salary", "+£2500.00", "Income"),
]

class SpendingSorter(App):
    CSS = """
    Screen {
        layout: horizontal;
    }
    #left-pane {
        width: 70%;
        border-right: tall $primary;
    }
    #right-pane {
        width: 30%;
        padding: 1;
        background: $boost;
    }
    .detail-label {
        color: $accent;
        text-style: bold;
        margin-top: 1;
    }
    DataTable {
        height: 1fr;
    }
    """

    BINDINGS = [
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
        Binding("g", "set_category('Groceries')", "Groceries"),
        Binding("e", "set_category('Entertainment')", "Entertainment"),
        Binding("p", "set_category('Pot Spend')", "Pot"),
        Binding("m", "match_pot", "Match Pot"),
    ]

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
        table.add_columns("Date", "Description", "Amount", "Category")
        table.add_rows(TX_DATA)
        table.focus()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Called when you press Enter on a row."""
        self.notify(f"Selected: {event.row_key}")

    def on_data_table_cell_highlighted(self, event: DataTable.CellHighlighted) -> None:
        """Updates the sidebar using the coordinate from the highlight event."""
        table = self.query_one(DataTable)
        # Get the row data using the row index from the coordinate
        row_data = table.get_row_at(event.coordinate.row)
        
        self.query_one("#det-desc").update(str(row_data[1]))
        self.query_one("#det-amt").update(str(row_data[2]))
        self.query_one("#det-status").update(str(row_data[3]))

    def action_set_category(self, category: str) -> None:
        """Logic to update the category of the highlighted row."""
        table = self.query_one(DataTable)
        cursor_cell = table.cursor_coordinate
        # Update the 'Category' column (index 3)
        table.update_cell_at((cursor_cell.row, 3), category)
        self.notify(f"Categorized as {category}")
        # Auto-move down after categorizing
        table.action_cursor_down()

    def action_match_pot(self) -> None:
        """Trigger a modal or switch screen to the 'Pot Matcher' view."""
        self.notify("Switching to Pot Matching View...", severity="information")

if __name__ == "__main__":
    app = SpendingSorter()
    app.run()
