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
  - The application uses [Textual](https://textual.textualize.io/) for its TUI, defined in `budget/main.py`.

Testing

- This project uses pytest for tests located in the ./tests directory.
- To run tests locally:
  - Ensure you are in the repository root.
  - Ensure you are in a venv. 
    - If not, and the venv/ folder exists then `source venv/bin/activate`
    - Otherwise create and activate a virtual environment: 
        - `python3 -m venv venv/ && source .venv/bin/activate`
        - `pip install -e .`
  - Run tests: `pytest`
- **Test Data**:
  - Example data is located at `data/test_data.csv`. This file can be used when verifying changes or running
    the application in development.

Code Style

- Lines in markdown files should be limited to about 100 chars, with a hard limit at 120.

Git / Repository rules for agents

- Never perform any git changes unless explicitly asked: 
    - Do not commit, create branches, push, amend, rebase, or modify history in any way.
- It is allowed (and encouraged) to inspect the repository state: 
    - run git status, git log, git show, or other read-only git commands to help analysis.
- If a change is necessary, report the required change clearly rather than performing it.
