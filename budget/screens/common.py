from textual.widgets import DirectoryTree, SelectionList
from textual.binding import Binding

# pylint: disable=too-many-ancestors
class BudgetDirectoryTree(DirectoryTree):
    BINDINGS = [
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
    ]

# pylint: disable=too-many-ancestors
class BudgetSelectionList(SelectionList):
    BINDINGS = [
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
    ]

