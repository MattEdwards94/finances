from textual.screen import ModalScreen
from textual.containers import Horizontal, Vertical
from textual.events import Key
from textual.widgets import Label, Button
from textual.app import ComposeResult

from budget.screens.common import BudgetSelectionList

# pylint: disable=too-many-ancestors
class FilterScreen(ModalScreen[list[str]]):
    def __init__(self, categories: list[str], selected: set[str] = None):
        super().__init__()
        self.categories = sorted(list(set(categories)))
        self.selected = selected or set()

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label("Select Filter", id="question")

            options = []
            filter_options = [
                "All (Active)",
                "Excluded",
                "Uncategorized",
                "Categorized",
                "Unlinked Pot"
            ]
            for opt in filter_options + self.categories:
                state = opt in self.selected
                options.append((opt, opt, state))

            yield BudgetSelectionList(*options, id="filter_options")

            with Horizontal(id="buttons"):
                yield Button("OK", variant="primary", id="ok")
                yield Button("Cancel", variant="error", id="cancel")

    def on_mount(self) -> None:
        self.query_one(BudgetSelectionList).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "ok":
            selection_list = self.query_one(BudgetSelectionList)
            self.dismiss(selection_list.selected)
        elif event.button.id == "cancel":
            self.dismiss(None)

    def on_key(self, event: Key) -> None:
        if event.key == "escape":
            self.dismiss(None)
