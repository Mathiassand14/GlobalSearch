# Repository Guidelines

## Project Structure & Module Organization
- Follow MVC separation:
  - `src/core/` — business logic only (`search/`, `documents/`, `indexing/`, `performance/`, `events/`, `exceptions/`). No PyQt6 imports here.
  - `src/gui/` — PyQt6 windows/widgets/workers; all I/O in `QThread`.
  - `src/main.py` — application entry point.
  - `config/settings.json` — persisted app settings via `PathResolver`.
  - `tests/` — unit tests for core; `pytest-qt` for GUI tests.
- Always use `cross_ide_path_utils` (`resolve_path`, `get_config_path`, `get_src_path`) for paths.

## Build, Test, and Development Commands
- Setup (uv): `python -m venv .venv && source .venv/bin/activate && pip install uv && uv sync`.
- Run app: `python -m src.main`.
- Start Elasticsearch: `docker compose up -d elasticsearch` (required for indexing).
- Tests: `pytest -q`; GUI: `pytest -q -k "window"` (with `pytest-qt`).
- Optional: `ruff check .`, `black .`, `isort .` if configured.

## Coding Style & Naming Conventions
- Type hints: required on all functions/methods.
- Paths: use `pathlib.Path` and `PathResolver` only.
- Naming: Classes `PascalCase`; functions/vars `snake_case`; constants `UPPER_SNAKE_CASE`.
- Mandatory stack: `PyQt6`, `pdfplumber`, `rapidfuzz`, `sentence_transformers` (model `all-MiniLM-L6-v2`), `elasticsearch`, `numba`, `joblib`.

## Testing Guidelines
- Framework: `pytest`; place tests under `tests/` mirroring `src/` (e.g., `tests/core/test_search_manager.py`).
- GUI: use `pytest-qt` for Qt widgets/windows.
- Conventions: arrange–act–assert; isolate core from GUI; add regression tests for bugs.

## Commit & Pull Request Guidelines
- Conventional Commits (e.g., `feat: add fuzzy search`). Reference requirement numbers and touched files (e.g., “Implements 2.3 in `src/core/search/...`”).
- PRs: include purpose, linked issues, repro steps, and screenshots/logs for UI.
- Pre-checks: pass `pytest` and linters/formatters before review.

## Agent-Specific Instructions
- Update `taskStatus` before/after each task; one task at a time.
- Reference requirement IDs in code and descriptions; stop after each task for review.
- Use `EventBus` for inter-window events, `QThread` for I/O, custom exceptions for errors, LRU-style cleanup for memory, and Numba/joblib for performance-critical paths.
- After a task is implemented and tests pass, commit your changes with a Conventional Commit message referencing requirement IDs. Example: `git add -A && git commit -m "feat(search): implement fuzzy search (req 2.3)"`.

## Task Workflow
- Update status: set `taskStatus` to `in_progress` and reference requirement IDs.
- Implement: follow MVC, mandatory stack, type hints, and `PathResolver` for paths.
- Test: run `pytest -q` (and GUI tests with `pytest-qt`); start Elasticsearch if required.
- Commit: `git add -A && git commit -m "<type>(<scope>): <summary> (req X.Y)"`.
- Request review: push/open PR, set `taskStatus` to `completed`, and wait for review.
