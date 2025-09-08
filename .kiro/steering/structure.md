---
inclusion: fileMatch
fileMatchPattern: ['src/**/*.py', 'tests/**/*.py']
---

# Directory Structure & Implementation Rules

## Required Project Structure
```
src/
├── main.py                 # Application entry point
├── gui/                    # UI layer (PyQt6 only)
│   ├── main_window.py      # Primary search/results window
│   ├── viewer_window.py    # Secondary PDF viewer window
│   └── components/         # Reusable UI widgets
├── core/                   # Business logic (framework-agnostic)
│   ├── pdf_processor.py    # PDF text extraction & processing
│   ├── search_engine.py    # Search indexing & querying
│   ├── file_manager.py     # File system operations
│   └── database.py         # Data persistence layer
├── models/                 # Data entities
│   ├── document.py         # Document model
│   ├── search_result.py    # Search result model
│   └── settings.py         # Application settings model
└── utils/                  # Shared utilities
    ├── config.py           # Configuration management
    ├── logger.py           # Logging setup
    └── helpers.py          # Common helper functions
```

## Implementation Guidelines
- **GUI Layer**: Only handle user interactions and display logic, delegate all business operations to `core/` modules
- **Core Layer**: Must be framework-agnostic and testable without GUI dependencies
- **Models**: Use dataclasses or Pydantic models with type annotations
- **Dependency Injection**: Pass dependencies through constructors, not global imports
- **Async Operations**: Use `asyncio` in core modules, `QThread` in GUI layer
- **Error Boundaries**: Catch exceptions at GUI layer, log in core layer

## File Creation Rules
- New Python files must include type hints for all public functions
- GUI files must inherit from appropriate PyQt6 base classes
- Core modules must not import from `gui/` package
- All modules must include proper logging setup
- Configuration files go in `config/` directory (create if missing)