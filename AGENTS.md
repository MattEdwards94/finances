AGENTS

Purpose

This file documents how automated agents (or contributors) should interact with this repository.

Testing

- This project uses pytest for tests located in the ./tests directory.
- To run tests locally:
  - Ensure you are in the repository root.
  - (Optional) Create and activate a virtual environment: python3 -m venv .venv && source .venv/bin/activate
  - Install pytest if needed: python3 -m pip install -U pip && python3 -m pip install pytest
  - Run tests: python3 -m pytest -q tests

Git / Repository rules for agents

- Never perform any git changes: do not commit, create branches, push, amend, rebase, or modify history in any way.
- It is allowed (and encouraged) to inspect the repository state: run git status, git log, git show, or other read-only git commands to help analysis.
- If a change is necessary, report the required change clearly rather than performing it.

Notes

- Example data is in the repository root (MonzoDataExport_28Jul-27Aug_2025-08-25_094131.csv) and example docs are in ./examples.
- Tests are minimal; running pytest will validate that the package imports. Add more tests under ./tests as needed.
