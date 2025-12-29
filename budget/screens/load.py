from pathlib import Path
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.events import Key
from textual.widgets import Label, Button, Input, DirectoryTree
from textual.screen import ModalScreen

from budget.screens.common import BudgetDirectoryTree

class LoadScreen(ModalScreen[str]):
    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            with Horizontal(classes="header"):
                yield Label("Select file to load:", id="question")
                yield Button("Up", id="up", variant="primary")
            yield BudgetDirectoryTree(str(Path.home() / "budget_data"))
            yield Input(placeholder="Enter filename", id="filename")
            with Horizontal(id="buttons"):
                yield Button("Load", variant="primary", id="load")
                yield Button("Cancel", variant="error", id="cancel")

    def on_mount(self) -> None:
        self.query_one(Input).focus()

    def on_directory_tree_directory_selected(self, event: DirectoryTree.DirectorySelected) -> None:
        input_widget = self.query_one(Input)
        input_widget.value = str(event.path) + "/"
        input_widget.focus()

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        input_widget = self.query_one(Input)
        input_widget.value = str(event.path)
        input_widget.focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "load":
            input_widget = self.query_one(Input)
            self.dismiss(input_widget.value)
        elif event.button.id == "up":
            tree = self.query_one(DirectoryTree)
            current = Path(tree.path).resolve()
            parent = current.parent
            tree.path = str(parent)
            tree.reload()
        elif event.button.id == "cancel":
            self.dismiss(None)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.dismiss(event.value)

    def on_key(self, event: Key) -> None:
        if event.key == "escape":
            self.dismiss(None)

