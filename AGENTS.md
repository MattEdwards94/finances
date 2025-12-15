AGENTS

Purpose

This file documents how automated agents (or contributors) should interact with this repository.

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

Git / Repository rules for agents

- Never perform any git changes unless explicitly asked: 
    - Do not commit, create branches, push, amend, rebase, or modify history in any way.
- It is allowed (and encouraged) to inspect the repository state: 
    - run git status, git log, git show, or other read-only git commands to help analysis.
- If a change is necessary, report the required change clearly rather than performing it.

Notes

- Example data is in the repository root (test_data.csv)
- Tests are minimal; running pytest will validate that the package imports. 
  Add more tests under ./tests as needed.
