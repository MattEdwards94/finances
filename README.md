# Finances Budget Tool

A terminal-based budget sorting application designed to help users categorize and manage their
financial transactions.
This tool is specifically built to work with Monzo CSV exports, providing a convenient
Terminal User Interface (TUI) for interactive data processing.

NOTE: This project has been created largely using AI code generation.

## Features

- **Transaction Management**: Load and view transactions from Monzo CSV exports.
- **Categorization**: Sort transactions into categories such as Income, General Spend, and Pot Spend.
- **Pot Linking**: Link pot transfers to specific transactions to track spending accurately.
- **Filtering**: Filter transactions by status (e.g., Excluded, Uncategorized, Categorized).
- **Persistence**: Save and load your progress to resume budgeting sessions later.
- **TUI Interface**: Built with [Textual](https://textual.textualize.io/) for a rich terminal experience.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd finances
    ```

2.  **Set up a virtual environment (recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -e .
    ```
    For development dependencies (testing, linting):
    ```bash
    pip install -e ".[dev]"
    ```

## Usage

To start the application, run the `budget_tool.py` script.
You can optionally provide a path to a CSV file to load immediately.

```bash
# Run the app
python budget_tool.py

# Run with a specific file
python budget_tool.py --file path/to/transactions.csv
```

### Navigation

- Use the mouse or keyboard to navigate the interface.
- Follow on-screen instructions for specific actions (e.g., categorizing, saving).


## Project Structure

- `budget/`: Core application code.
    - `main.py`: Application entry point and logic.
    - `screens/`: UI screens (Save, Load, Filter, etc.).
    - `widgets.py`: Custom Textual widgets.
    - `transaction.py` & `raw_transaction.py`: Data models.
- `tests/`: Test suite.
- `data/`: Example data for testing.
