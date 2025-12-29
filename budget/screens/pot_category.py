from textual.app import ComposeResult
from textual.widgets import Label, Input, OptionList
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen

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
