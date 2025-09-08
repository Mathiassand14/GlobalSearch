# Agent Implementation Guide - Intelligent PDF Search Application

## Overview for AI Agents

This guide provides specific instructions for AI coding agents (Codex, Claude, etc.) implementing the intelligent PDF search application. Follow these guidelines to ensure consistent, high-quality implementation that meets all requirements.

## Critical Implementation Rules

### 1. Task Management Protocol
- **ALWAYS** update task status using the taskStatus tool before starting and after completing each task
- **NEVER** implement multiple tasks simultaneously - focus on ONE task at a time
- **ALWAYS** reference specific requirements in your implementation (e.g., "This implements requirement 2.3")
- **STOP** after completing each task and wait for user review before proceeding

### 2. Mandatory Technology Stack (Non-Negotiable)
```python
# Required imports and libraries - DO NOT substitute
import pathlib  # MANDATORY for all file operations
from PyQt6 import QtWidgets, QtCore, QtGui  # NEVER use PyQt5 or other GUI frameworks
import pdfplumber  # MANDATORY for PDF processing - NEVER use PyMuPDF
import rapidfuzz  # MANDATORY for fuzzy search - NEVER use fuzzywuzzy
from sentence_transformers import SentenceTransformer  # Model: all-MiniLM-L6-v2
import elasticsearch
import numba
import joblib
```

### 3. Code Standards (Strictly Enforced)
```python
# Type hints are MANDATORY on ALL functions and class methods
def search_documents(query: str, options: SearchOptions) -> SearchResults:
    pass

# Use pathlib.Path for ALL file operations with cross-IDE support
from pathlib import Path
from cross_ide_path_utils import resolve_path, get_config_path, get_src_path

# ALWAYS use PathResolver for consistent path resolution across IDEs
document_path: Path = resolve_path("documents/file.pdf")  # Works in VSCode and PyCharm
config_path: Path = get_config_path("settings.json")     # Resolves to project/config/settings.json

# Naming conventions
class DocumentProcessor:  # PascalCase for classes
    def extract_text(self, file_path: Path) -> str:  # snake_case for methods
        pass

MAX_MEMORY_USAGE: int = 1024 * 1024 * 1024  # UPPER_SNAKE_CASE for constants
```

### 4. Architecture Requirements

#### MVC Separation (Critical)
```
src/
├── core/           # Business logic ONLY - no GUI imports
│   ├── search/     # #[[file:src/core/search/]]
│   ├── documents/  # #[[file:src/core/documents/]]
│   ├── indexing/   # #[[file:src/core/indexing/]]
│   └── performance/ # #[[file:src/core/performance/]]
├── gui/            # PyQt6 GUI components ONLY
│   ├── windows/    # #[[file:src/gui/windows/]]
│   └── widgets/    # #[[file:src/gui/widgets/]]
└── main.py         # #[[file:src/main.py]] - Application entry point
```

#### Observer Pattern Implementation
```python
# Use EventBus for inter-window communication
# File: #[[file:src/core/events/event_bus.py]]
from src.core.events.event_bus import EventBus

# File: #[[file:src/gui/windows/search_window.py]]
class SearchWindow(QtWidgets.QMainWindow):
    def __init__(self):
        self.event_bus = EventBus()
        self.event_bus.subscribe("search_result_selected", self.handle_result_selection)
```

### 5. Performance Requirements (Must Meet)

#### Threading (Mandatory)
```python
# ALL I/O operations MUST use QThread
# File: #[[file:src/gui/workers/indexing_worker.py]]
class IndexingWorker(QtCore.QThread):
    def run(self):
        # Indexing logic here - NEVER block UI thread
        pass

# Usage in GUI - File: #[[file:src/gui/windows/search_window.py]]
worker = IndexingWorker()
worker.start()  # NEVER call run() directly
```

#### Memory Management
```python
# Implement explicit cleanup for large objects
# File: #[[file:src/core/cache/document_cache.py]]
class DocumentCache:
    def __init__(self, max_size: int = 50):
        self.cache: Dict[str, Any] = {}
        self.max_size = max_size
    
    def cleanup_if_needed(self):
        if len(self.cache) > self.max_size:
            # LRU eviction logic
            pass
```

#### Performance Optimization
```python
# Use Numba for numerical operations
# File: #[[file:src/core/performance/numba_ops.py]]
from numba import jit

@jit(nopython=True)
def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# Use joblib for parallel processing
# File: #[[file:src/core/processing/parallel_processor.py]]
from joblib import Parallel, delayed

results = Parallel(n_jobs=-1)(
    delayed(process_document)(doc) for doc in documents
)
```

### 6. Error Handling Patterns

```python
# Custom exception hierarchy
# File: #[[file:src/core/exceptions/exceptions.py]]
class PDFSearchException(Exception):
    """Base exception for PDF search application"""
    pass

class DocumentProcessingError(PDFSearchException):
    """Raised when document processing fails"""
    pass

# Graceful error handling
# File: #[[file:src/core/documents/document_manager.py]]
def process_document(file_path: Path) -> Optional[DocumentContent]:
    try:
        return extract_text(file_path)
    except DocumentProcessingError as e:
        logger.error(f"Failed to process {file_path}: {e}")
        return None  # Continue processing other files
```

### 7. Configuration Management

```python
# Use dataclasses with type hints
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class SearchSettings:
    fuzzy_edit_distance: int = 2
    semantic_similarity_threshold: float = 0.7
    enable_ai_search: bool = True
    current_model_name: str = "all-MiniLM-L6-v2"

# JSON persistence with pathlib
import json
from pathlib import Path

def save_config(config: ApplicationConfig, config_path: Path) -> None:
    with config_path.open('w') as f:
        json.dump(asdict(config), f, indent=2)
```

### 8. Testing Requirements

```python
# Unit tests for core logic (no GUI dependencies)
import pytest
from src.core.search.search_manager import SearchManager

def test_fuzzy_search():
    manager = SearchManager()
    results = manager.search("algoritm", SearchOptions(enable_fuzzy=True))
    assert len(results) > 0
    assert any("algorithm" in result.snippet.lower() for result in results)

# GUI tests with pytest-qt
import pytest
from pytestqt import qtbot

def test_search_window(qtbot):
    window = SearchWindow()
    qtbot.addWidget(window)
    # Test GUI interactions
```

### Key Configuration Files:
```python
# File: #[[file:config/settings.json]] - Main application configuration
# File: #[[file:pyproject.toml]] - UV package management and Cython setup
# File: #[[file:docker-compose.yml]] - Elasticsearch service configuration with UV sync
# File: #[[file:Dockerfile]] - Container configuration using UV sync
# File: #[[file:.gitignore]] - Git ignore patterns
```

### UV Sync Development Workflow (Mandatory):
```bash
# File: #[[file:pyproject.toml]] defines all dependencies
# ALWAYS use UV sync for dependency management

# Initial setup
uv sync                          # Install all dependencies from pyproject.toml
uv sync --dev                   # Include development dependencies

# Docker development
docker-compose up -d            # Starts Elasticsearch with UV sync
uv run python src/main.py      # Run application with UV

# Testing
uv run pytest                  # Run tests with UV
uv run mypy src/               # Type checking with UV

# Adding dependencies (update pyproject.toml, then sync)
uv add pdfplumber              # Add new dependency
uv sync                        # Sync to install new dependency
```

## Implementation Checklist for Each Task

### Before Starting Any Task:
1. [ ] Read the specific task requirements and referenced requirement numbers
2. [ ] Update task status to "in_progress" using taskStatus tool
3. [ ] Identify which files need to be created or modified using file references
4. [ ] Check if any dependencies need to be imported

### During Implementation:
1. [ ] Follow MVC architecture - no business logic in GUI files
2. [ ] Use mandatory libraries (pdfplumber, rapidfuzz, PyQt6, etc.)
3. [ ] Add type hints to ALL functions and methods
4. [ ] Use pathlib.Path for ALL file operations
5. [ ] Implement proper error handling with custom exceptions
6. [ ] Add logging with structured format
7. [ ] Use QThread for any I/O operations in GUI code
8. [ ] Write unit tests for core business logic

### After Completing Task:
1. [ ] Verify implementation meets all referenced requirements
2. [ ] Test the implemented functionality
3. [ ] Update task status to "completed" using taskStatus tool
4. [ ] Document any assumptions or design decisions made
5. [ ] STOP and wait for user review before proceeding to next task

## Cross-IDE Path Resolution (Critical)

### Always Use PathResolver for File Operations
```python
# Import the cross-IDE path utilities
# File: #[[file:cross_ide_path_utils.py]]
from cross_ide_path_utils import (
    resolve_path, get_config_path, get_src_path, 
    get_document_path, get_logs_path, PathResolver
)

# CORRECT: Works in VSCode, PyCharm, and command line
config_path = get_config_path("settings.json")
document_dir = get_document_path()
log_file = get_logs_path("app.log")

# INCORRECT: May fail in different IDEs due to working directory differences
config_path = Path("config/settings.json")  # DON'T DO THIS
```

### Project Structure Detection
```python
# The PathResolver automatically detects project root by looking for:
# - pyproject.toml (UV/Poetry projects)
# - .kiro/ directory (Kiro workspace)
# - src/ directory (Python projects)
# - .git directory (Git repos)

resolver = PathResolver()
print(f"Project root: {resolver.project_root}")
print(f"Running from: {Path.cwd()}")

# Debug path issues during development
if __name__ == "__main__":
    from cross_ide_path_utils import debug_path_info
    debug_path_info()  # Prints detailed path information
```

## Common Implementation Patterns

### Document Processing
```python
# File: #[[file:src/core/documents/processors/base_processor.py]]
class DocumentProcessor(ABC):
    @abstractmethod
    def extract_text(self, file_path: Path) -> DocumentContent:
        pass

# File: #[[file:src/core/documents/processors/pdf_processor.py]]
class PDFProcessor(DocumentProcessor):
    def extract_text(self, file_path: Path) -> DocumentContent:
        # file_path should already be resolved using PathResolver
        with pdfplumber.open(file_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
        return DocumentContent(text=text, page_count=len(pdf.pages))

# Usage with cross-IDE path support
# File: #[[file:src/core/documents/document_manager.py]]
from cross_ide_path_utils import get_document_path

processor = PDFProcessor()
pdf_file = get_document_path("sample.pdf")  # Works in any IDE
content = processor.extract_text(pdf_file)
```

### Search Strategy Pattern
```python
# File: #[[file:src/core/search/strategies/base_strategy.py]]
class SearchStrategy(ABC):
    @abstractmethod
    def search(self, query: str, index: Any) -> List[SearchResult]:
        pass

# File: #[[file:src/core/search/strategies/fuzzy_search_strategy.py]]
class FuzzySearchStrategy(SearchStrategy):
    def search(self, query: str, index: Any) -> List[SearchResult]:
        # Use rapidfuzz for fuzzy matching
        from rapidfuzz import fuzz
        # Implementation here
```

### GUI Component Structure
```python
# File: #[[file:src/gui/windows/search_window.py]]
class SearchWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_connections()
        self.setup_threading()
    
    def setup_ui(self):
        # UI layout code
        pass
    
    def setup_connections(self):
        # Signal/slot connections
        pass
    
    def setup_threading(self):
        # QThread setup for I/O operations
        pass
```

## Debugging and Troubleshooting

### Common Issues and Solutions:
1. **UI Freezing**: Always use QThread for I/O operations
2. **Import Errors**: Check mandatory library usage (pdfplumber, not PyMuPDF)
3. **Path Issues**: Use pathlib.Path consistently across all platforms
4. **Memory Leaks**: Implement explicit cleanup and LRU caching
5. **Performance Issues**: Use Numba JIT and joblib parallel processing

### Logging Configuration:
```python
# File: #[[file:src/core/logging/logger_config.py]]
import logging
from cross_ide_path_utils import get_logs_path

def setup_logging():
    log_file = get_logs_path("app.log")
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
```

### Testing Patterns with File References:
```python
# File: #[[file:tests/core/test_search_manager.py]]
import pytest
from src.core.search.search_manager import SearchManager

def test_fuzzy_search():
    manager = SearchManager()
    results = manager.search("algoritm", SearchOptions(enable_fuzzy=True))
    assert len(results) > 0
    assert any("algorithm" in result.snippet.lower() for result in results)

# File: #[[file:tests/gui/test_search_window.py]]
import pytest
from pytestqt import qtbot
from src.gui.windows.search_window import SearchWindow

def test_search_window(qtbot):
    window = SearchWindow()
    qtbot.addWidget(window)
    # Test GUI interactions

# File: #[[file:tests/conftest.py]]
import pytest
from cross_ide_path_utils import get_config_path

@pytest.fixture
def test_config():
    return get_config_path("test_settings.json")
```

## Final Notes for Agents

- **Quality over Speed**: Take time to implement correctly rather than rushing
- **Test as You Go**: Write and run tests for each component
- **Document Decisions**: Comment complex logic and design choices
- **Follow the Plan**: Stick to the task list order and don't skip ahead
- **Ask for Clarification**: If requirements are unclear, ask before implementing

Remember: The goal is a production-ready application that meets all performance and quality requirements. Each task builds on the previous ones, so careful implementation is crucial for success.