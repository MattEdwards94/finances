AGENTS

Purpose

This file documents how automated agents (or contributors) should interact with this repository.

Project Overview

This project is a budget sorter application designed to help users categorize and manage their financial
transactions. It provides a Terminal User Interface (TUI) for interacting with transaction data.

Architecture

- **Core Data Structures**:
  - `RawTransaction` (`budget/raw_transaction.py`): Represents an immutable view of a single row from the
    source CSV. It handles parsing and validation of raw fields.
  - `Transaction` (`budget/transaction.py`): Wraps a `RawTransaction` and adds mutable fields for processing
    (e.g., `excluded`, categorization). This allows the original data to remain untouched while storing
    user-defined attributes.
- **User Interface**:
  - The application uses [Textual](https://textual.textualize.io/) for its TUI.
  - `budget/main.py`: Contains the main `BudgetApp` class and application logic.
  - `budget/widgets.py`: Contains custom widgets like `TransactionTable` and `TransactionDetails`.
  - `budget/screens.py`: Contains modal screens for interactions (Save, Load, Filter, Confirmations).

Testing

- This project uses `pytest` and `pytest-asyncio` for tests located in the `./tests` directory.
- **Running Tests**:
  - Ensure you are in the repository root and have the virtual environment activated.
    - `source venv/bin/activate` if the venv exists
    - `python3 -m venv venv && source venv/bin/activate && pip install -e ".[dev]"` to create
      the venv and install dependencies if it does not exist.
  - Run: `pytest`
- **Writing Tests**:
  - Use `pytest.mark.asyncio` for async tests, especially those involving Textual apps.
  - Use `textual.app.App.run_test()` context manager to interact with the app via `pilot`.
  - Mock external dependencies (file I/O, `load_data`, `save_transactions`) using `unittest.mock`.
  - Refer to `tests/test_app.py` or `tests/test_screens.py` for examples of testing UI flows.
- **Test Data**:
  - Example data is located at `data/test_data.csv`. This file can be used when verifying changes or running
    the application in development.

Code Style

- **Linting**: The project enforces high code quality. 
  - You MUST run `pylint` on modified files and achieve a 10/10 score.
- Lines in markdown files should be limited to about 100 chars, with a hard limit at 120.

Git / Repository rules for agents

- Never perform any git changes unless explicitly asked: 
    - Do not commit, create branches, push, amend, rebase, or modify history in any way.
- It is allowed (and encouraged) to inspect the repository state: 
    - run git status, git log, git show, or other read-only git commands to help analysis.
- If a change is necessary, report the required change clearly rather than performing it.

- **Testing**:
  - Always write new tests when adding new features or fixing bugs.
  - Ensure all tests pass before completing the task.
