from pathlib import Path
from textual.app import ComposeResult
from textual.widgets import Label, Input, Button, DirectoryTree, SelectionList, OptionList
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

class PotCategoryScreen(ModalScreen[str]):
    POT_CATEGORIES = [
        "Bills",
        "Car maintenance",
        "Phones",
        "Work and commuting",
        "Dogs",
        "House",
        "Gifts",
        "Holidays",
        "Events",
    ]

    def __init__(self):
        super().__init__()
        self.all_options = sorted(self.POT_CATEGORIES)
        self.filtered_options = self.all_options[:]

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label("Select Pot Category", id="question")
            yield Input(placeholder="Filter categories...", id="filter_input")
            yield OptionList(*self.filtered_options, id="pot_options")

    def on_mount(self) -> None:
        self.query_one(Input).focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        query = event.value.lower()
        self.filtered_options = [
            opt for opt in self.all_options if query in opt.lower()
        ]
        option_list = self.query_one(OptionList)
        option_list.clear_options()
        option_list.add_options(self.filtered_options)
        if self.filtered_options:
            option_list.highlighted = 0

    def on_input_submitted(self, _event: Input.Submitted) -> None:
        option_list = self.query_one(OptionList)
        if (option_list.highlighted is not None and
                0 <= option_list.highlighted < len(self.filtered_options)):
            self.dismiss(self.filtered_options[option_list.highlighted])

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        self.dismiss(str(event.option.prompt))

    def on_key(self, event) -> None:
        if event.key == "down":
            self.query_one(OptionList).action_cursor_down()
        elif event.key == "up":
            self.query_one(OptionList).action_cursor_up()
        elif event.key == "enter":
            pass

    def action_cancel(self) -> None:
        self.dismiss(None)

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

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
