---
inclusion: always
---

# PDF Search Application - Development Guide

## Application Overview
Dual-window desktop PDF search application with multi-modal search capabilities (exact, fuzzy, semantic AI) optimized for research workflows.

## Core Architecture Requirements
- **Dual-window design**: Separate search/results window and PDF viewer window
- **MVC separation**: GUI layer (`src/gui/`) contains no business logic
- **Framework-agnostic core**: Business logic in `src/core/` must be testable without GUI
- **Observer pattern**: Use for inter-window communication
- **Repository pattern**: Abstract all data access operations

## Technology Stack (Non-negotiable)
- **Python 3.11+** with mandatory type hints on all functions/classes
- **PyQt6** for GUI (no alternatives), use QThread for I/O operations
- **pdfplumber** for PDF text extraction (never PyMuPDF)
- **Elasticsearch** + **sentence-transformers** (all-MiniLM-L6-v2) for search
- **rapidfuzz** for fuzzy matching (never fuzzywuzzy)
- **UV** for package management, **Docker Compose** for services

## Performance Requirements
- Search response < 500ms for collections under 1000 documents
- Use QThread for all I/O to prevent UI blocking
- Lazy load PDF pages, cache with LRU eviction
- Explicitly release large objects (PDF data, images)

## Code Standards
- **Type hints**: Required for all function signatures and class attributes
- **Naming**: snake_case (files/functions), PascalCase (classes), UPPER_SNAKE_CASE (constants)
- **Imports**: Standard library → Third-party → Local (no relative imports)
- **Error handling**: Use specific exceptions, always log with context
- **Configuration**: Store in `config/settings.json`, validate on startup

## Development Commands
```bash
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt
docker-compose up -d
uv run python src/main.py
```