from pathlib import Path
from textual.app import ComposeResult
from textual.widgets import Label, Input, Button, DirectoryTree, SelectionList
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.events import Key

# pylint: disable=too-many-ancestors
class BudgetSelectionList(SelectionList):
    BINDINGS = [
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
    ]

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
            for opt in ["All", "Uncategorized", "Categorized"] + self.categories:
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

# pylint: disable=too-many-ancestors
class BudgetDirectoryTree(DirectoryTree):
    BINDINGS = [
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
    ]

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

class SaveScreen(ModalScreen[str]):
    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            with Horizontal(classes="header"):
                yield Label("Select folder:", id="question")
                yield Button("Up", id="up", variant="primary")
            yield BudgetDirectoryTree(str(Path.home() / "budget_data"))
            yield Input(placeholder="Enter filename", id="filename")
            with Horizontal(id="buttons"):
                yield Button("Save", variant="primary", id="save")
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
        elif event.button.id == "up":
            tree = self.query_one(DirectoryTree)
            current = Path(tree.path).resolve()
            parent = current.parent
            tree.path = str(parent)
            tree.reload()
        elif event.button.id == "cancel":
            self.dismiss(None)

    def on_input_submitted(self, _event: Input.Submitted) -> None:
        self.handle_save()

    def on_key(self, event: Key) -> None:
        if event.key == "escape":
            self.dismiss(None)
