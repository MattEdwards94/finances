import pytest
from textual.app import App
from textual.widgets import DirectoryTree, SelectionList
from budget.screens import (
    SaveOrLoadScreen,
    FilterScreen,
    BudgetDirectoryTree,
    BudgetSelectionList,
)

class ScreenTestApp(App):
    def __init__(self, screen_to_test):
        super().__init__()
        self.screen_to_test = screen_to_test

    def on_mount(self):
        self.push_screen(self.screen_to_test)

def test_budget_directory_tree_bindings():
    """Test that BudgetDirectoryTree has j and k bindings."""
    bindings = BudgetDirectoryTree.BINDINGS
    keys = {b.key: b.action for b in bindings}
    assert "j" in keys
    assert keys["j"] == "cursor_down"
    assert "k" in keys
    assert keys["k"] == "cursor_up"

def test_budget_selection_list_bindings():
    """Test that BudgetSelectionList has j and k bindings."""
    bindings = BudgetSelectionList.BINDINGS
    keys = {b.key: b.action for b in bindings}
    assert "j" in keys
    assert keys["j"] == "cursor_down"
    assert "k" in keys
    assert keys["k"] == "cursor_up"

@pytest.mark.asyncio
async def test_load_screen_uses_custom_tree():
    """Test that LoadScreen uses BudgetDirectoryTree."""
    screen = SaveOrLoadScreen(mode="load")
    app = ScreenTestApp(screen)
    async with app.run_test() as _:
        tree = screen.query_one(DirectoryTree)
        assert isinstance(tree, BudgetDirectoryTree)

@pytest.mark.asyncio
async def test_save_screen_uses_custom_tree():
    """Test that SaveScreen uses BudgetDirectoryTree."""
    screen = SaveOrLoadScreen(mode="save")
    app = ScreenTestApp(screen)
    async with app.run_test() as _:
        tree = screen.query_one(DirectoryTree)
        assert isinstance(tree, BudgetDirectoryTree)

@pytest.mark.asyncio
async def test_filter_screen_uses_custom_list():
    """Test that FilterScreen uses BudgetSelectionList."""
    screen = FilterScreen(["Food", "Rent"])
    app = ScreenTestApp(screen)
    async with app.run_test() as _:
        selection_list = screen.query_one(SelectionList)
        assert isinstance(selection_list, BudgetSelectionList)

@pytest.mark.asyncio
async def test_directory_tree_navigation():
    """Test that j and k keys move the cursor in the tree."""
    class TestTree(BudgetDirectoryTree):
        # pylint: disable=too-many-ancestors
        def __init__(self):
            super().__init__(".")

    app = App()
    app.compose = lambda: [TestTree()]

    async with app.run_test() as pilot:
        tree = app.query_one(BudgetDirectoryTree)
        tree.focus()

        # Wait for tree to populate
        async def wait_for_load():
            while tree.last_line <= 0:
                await pilot.pause(0.1)
        await wait_for_load()

        if tree.last_line < 1:
            pytest.skip("Not enough files in current directory to test navigation")

        tree.cursor_line = 0
        assert tree.cursor_line == 0

        await pilot.press("j")
        assert tree.cursor_line == 1

        await pilot.press("k")
        assert tree.cursor_line == 0

@pytest.mark.asyncio
async def test_filter_screen_navigation():
    """Test that j and k keys move the selection in the list."""
    screen = FilterScreen(["Food", "Rent"])
    app = ScreenTestApp(screen)

    async with app.run_test() as pilot:
        selection_list = screen.query_one(BudgetSelectionList)
        selection_list.focus()

        assert selection_list.highlighted == 0

        await pilot.press("j")
        assert selection_list.highlighted == 1

        await pilot.press("j")
        assert selection_list.highlighted == 2

        await pilot.press("k")
        assert selection_list.highlighted == 1
