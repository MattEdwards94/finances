from pathlib import Path
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.containers import Horizontal, Vertical
from textual.widgets import Label, Button, Input, DirectoryTree
from textual.events import Key

from budget.screens.common import BudgetDirectoryTree

class SaveOrLoadScreen(ModalScreen[str]):
    def __init__(self, mode: str = "save"):
        super().__init__()
        if mode not in ("save", "load"):
            raise ValueError("mode must be 'save' or 'load'")

        self.mode = mode

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            with Horizontal(classes="header"):
                yield Label("Select folder:", id="question")
                yield Button("Up", id="up", variant="primary")
            yield BudgetDirectoryTree(str(Path.home() / "budget_data"))
            yield Input(placeholder="Enter filename", id="filename")
            with Horizontal(id="buttons"):
                yield Button(self.mode, variant="primary", id=self.mode)
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

    def handle_save(self):
        input_widget = self.query_one(Input)
        filename = input_widget.value
        if not filename:
            return

        if Path(filename).exists():
            def check_overwrite(should_overwrite: bool) -> None:
                if should_overwrite:
                    self.dismiss(filename)
                # else do nothing, stay on SaveScreen

            self.app.push_screen(OverwriteConfirmScreen(), check_overwrite)
        else:
            self.dismiss(filename)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            self.handle_save()
        elif event.button.id == "load":
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
        if self.mode == "load":
            self.dismiss(event.value)
        elif self.mode == "save":
            self.handle_save()
        else:
            raise ValueError("Invalid mode")

    def on_key(self, event: Key) -> None:
        if event.key == "escape":
            self.dismiss(None)

# pylint: disable=too-many-ancestors
class OverwriteConfirmScreen(ModalScreen[bool]):
    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label("File already exists. Overwrite?", id="question")
            with Horizontal(id="buttons"):
                yield Button("Yes", variant="primary", id="yes")
                yield Button("No", variant="error", id="no")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "yes":
            self.dismiss(True)
        else:
            self.dismiss(False)

    def on_key(self, event: Key) -> None:
        if event.key == "escape":
            self.dismiss(False)

class SaveChangesConfirmScreen(ModalScreen[str]):
    def __init__(self, message: str = "Save changes?"):
        super().__init__()
        self.message = message

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label(self.message, id="question")
            with Horizontal(id="buttons"):
                yield Button("Yes", variant="primary", id="yes")
                yield Button("No", variant="error", id="no")
                yield Button("Cancel", variant="default", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "yes":
            self.dismiss("yes")
        elif event.button.id == "no":
            self.dismiss("no")
        else:
            self.dismiss("cancel")

    def on_key(self, event: Key) -> None:
        if event.key == "escape":
            self.dismiss("cancel")
