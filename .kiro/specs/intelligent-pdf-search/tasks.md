# Implementation Plan

- [x] 1. Set up project foundation and dependencies
  - Create project directory structure following MVC pattern using pathlib (src/core/, src/gui/, config/, tests/, src/core/performance/)
  - Create requirements.txt with all mandatory dependencies (PyQt6, pdfplumber, elasticsearch, sentence-transformers, rapidfuzz, numba, cython, joblib, torch)
  - Add GPU acceleration dependencies (torch with CUDA support, sentence-transformers GPU backend)
  - Set up Docker Compose configuration for Elasticsearch service
  - Create pyproject.toml for UV package management and Cython compilation
  - Create basic .gitignore for Python projects
  - _Requirements: 6.1, 6.3, 6.5_

- [x] 2. Implement core data models and exceptions
  - Create Document, SearchResult, TopicNode, TopicTree, and Configuration dataclasses with mandatory type hints
  - Use pathlib.Path for all file path attributes and operations
  - Add ReEncodingResult dataclass for model switching operations
  - Implement custom exception hierarchy (PDFSearchException, ServiceUnavailableError, etc.)
  - Add validation methods for all data models including topic hierarchy validation with pathlib path validation
  - Write unit tests for data model validation and serialization
  - _Requirements: 2.2, 4.5, 5.4_

- [x] 3. Create configuration management system
  - Implement ApplicationConfig dataclass with all settings (search, UI, performance, Docker services)
  - Use pathlib.Path for all directory and file path configurations
  - Create ConfigurationManager class with JSON schema validation and pathlib path handling
  - Add settings.json template with sensible defaults using pathlib paths
  - Implement configuration persistence and hot-reload functionality with pathlib file operations
  - Write unit tests for configuration validation and persistence
  - _Requirements: 6.2, 6.5_

- [ ] 4. Implement extensible document processing architecture
- [x] 4.1 Create document processor interface and base classes
  - Define DocumentProcessor abstract base class with standard methods using pathlib.Path parameters
  - Create DocumentContent and PageContent dataclasses for unified document representation with pathlib paths
  - Implement DocumentManager class with processor registration system using pathlib for file operations
  - Add file type detection and processor routing logic with pathlib suffix checking
  - Write unit tests for processor registration and routing
  - _Requirements: 2.1, 2.2_

- [x] 4.2 Implement PDF document processor using pdfplumber
  - Create PDFProcessor class implementing DocumentProcessor interface with pathlib.Path handling
  - Integrate pdfplumber (mandatory library) for PDF text extraction with metadata preservation
  - Implement page-by-page content extraction for PDF files using pathlib for file operations
  - Handle corrupted and password-protected PDF error cases gracefully (log and continue)
  - Write unit tests for PDF processing and error handling with pathlib paths
  - _Requirements: 2.1, 2.2, 2.4_

- [x] 4.3 Implement additional document processors for multi-format support
  - Create TextProcessor for .txt and .md files with encoding detection using pathlib
  - Create DocxProcessor for Microsoft Word documents using python-docx with pathlib paths
  - Add processor auto-discovery mechanism for easy extension using pathlib directory scanning
  - Implement file watching functionality for automatic directory monitoring with pathlib
  - Write unit tests for each processor type and auto-discovery
  - _Requirements: 2.1, 2.3_

- [ ] 5. Implement Docker service management
  - Create DockerServiceManager class for automatic service startup
  - Implement service health checking and startup verification
  - Add clear error messaging with troubleshooting guidance for service failures
  - Create docker-compose.yml with Elasticsearch configuration
  - Write integration tests for service management
  - _Requirements: 6.1, 6.3, 6.4_

- [ ] 6. Implement Elasticsearch integration and indexing
  - Create IndexManager class with Elasticsearch client configuration
  - Implement document indexing with text content and metadata storage
  - Add GPU-accelerated vector embedding generation using sentence-transformers (all-MiniLM-L6-v2 mandatory model)
  - Create index schema with dense_vector fields for semantic search and topic hierarchy
  - Implement bulk indexing operations with joblib parallel processing for performance optimization
  - Add re-encoding functionality for switching embedding models with GPU acceleration
  - Implement topic hierarchy generation using AI clustering of document embeddings with parallel processing
  - Write integration tests with test Elasticsearch instance
  - _Requirements: 2.1, 2.3, 1.2, 5.1_

- [ ] 7. Implement search strategies and search manager
- [ ] 7.1 Create exact search strategy with Elasticsearch queries
  - Implement ExactSearchStrategy class with boolean operator support (AND, OR, NOT)
  - Add query parsing and validation for complex search expressions
  - Ensure sub-500ms response time for collections under 1000 documents
  - Write unit tests for query parsing and exact matching
  - _Requirements: 1.1, 4.4, 5.1_

- [ ] 7.2 Create fuzzy search strategy with spelling correction using rapidfuzz
  - Implement FuzzySearchStrategy using Elasticsearch fuzzy queries and rapidfuzz (mandatory library)
  - Add automatic spelling suggestion generation for failed searches
  - Configure edit distance parameters and confidence thresholds (80% accuracy target)
  - Highlight match confidence levels for user feedback
  - Write unit tests for fuzzy matching and spelling correction
  - _Requirements: 1.1, 1.4, 1.5_

- [ ] 7.3 Create semantic search strategy with GPU-accelerated AI embeddings
  - Implement SemanticSearchStrategy using sentence-transformers embeddings with GPU acceleration
  - Add GPU-accelerated cosine similarity search with configurable threshold (default 0.7)
  - Implement embedding caching for performance optimization with GPU memory management
  - Add toggle functionality to disable AI search and use only pre-encoded files
  - Implement automatic GPU/CPU fallback based on hardware availability
  - Write unit tests for semantic similarity matching and AI toggle behavior
  - _Requirements: 1.2, 4.1_

- [ ] 7.4 Implement search manager orchestration
  - Create SearchManager class that coordinates all search strategies
  - Implement auto-complete suggestions based on indexed content
  - Add search result ranking and relevance scoring
  - Implement search result caching with TTL expiration
  - Add hierarchical topic search functionality (e.g., "algorithms > trees")
  - Implement topic tree navigation and filtering
  - Write integration tests for multi-strategy search coordination and topic hierarchy
  - _Requirements: 1.3, 4.5, 5.1_

- [ ] 8. Implement performance optimization modules
- [ ] 8.1 Create GPU and Numba-accelerated operations
  - Implement numba_ops.py with @jit decorated cosine similarity functions with GPU support
  - Add GPU-accelerated batch embedding processing functions for re-encoding operations
  - Create vector distance computation functions for semantic search with GPU acceleration
  - Implement joblib parallel processing for CPU-bound operations when GPU unavailable
  - Add automatic GPU/CPU device selection and memory management
  - Write performance benchmarks comparing GPU vs CPU vs standard implementations
  - _Requirements: 5.1, 5.3_

- [ ] 8.2 Create Cython extensions for text processing with parallel support
  - Implement text_processing.pyx with fast tokenization functions
  - Add optimized fuzzy matching loops for large datasets with joblib parallel processing
  - Create high-performance document parsing routines with multi-threading support
  - Set up automatic Cython compilation during package installation
  - Implement parallel text processing for batch operations using joblib
  - Write unit tests for Cython extension functionality and parallel processing
  - _Requirements: 1.1, 2.1, 5.1_

- [ ] 9. Implement event bus for inter-window communication
  - Create EventBus class using observer pattern for decoupled window communication
  - Define event types (SearchResultSelected, DocumentOpened, WindowClosed, IndexingProgress)
  - Implement subscribe/publish/unsubscribe methods with type safety
  - Add thread-safe event handling for GUI operations
  - Write unit tests for event bus functionality
  - _Requirements: 3.2, 3.3, 3.5_

- [ ] 10. Create search window GUI components
- [ ] 10.1 Implement main search window layout and controls
  - Create SearchWindow class with PyQt6 widgets (search bar, filters, results list, topic tree)
  - Implement debounced search input with 300ms delay using QTimer (exact requirement)
  - Add advanced filter controls (date range, file type, relevance threshold, boolean operators)
  - Create results list widget with pagination and lazy loading
  - Add hierarchical topic tree browser widget for navigation
  - Add settings button to access configuration panel
  - Use QThread for all I/O operations to prevent UI blocking (mandatory)
  - _Requirements: 3.1, 4.2, 4.3, 4.5_

- [ ] 10.2 Implement search result display and interaction
  - Create custom QListWidget items for search results with relevance scores
  - Add result sorting options (relevance, date, document name)
  - Implement result selection handling and document viewer communication via EventBus
  - Add loading indicators and progress feedback for long operations
  - Implement topic tree navigation and filtering integration
  - Add drag-and-drop support for files onto search window with automatic copying to document folder
  - Ensure sub-2-second response time with loading indicators
  - Write GUI unit tests using pytest-qt
  - _Requirements: 2.5, 4.5, 3.2, 5.1_

- [ ] 11. Create settings window GUI components
- [ ] 11.1 Implement settings window layout and AI model configuration
  - Create SettingsWindow class with tabbed interface (AI Models, Search, Performance, Services, GPU Settings)
  - Add model selection dropdown with sentence-transformers model options
  - Implement GPU/CPU device selection and memory allocation controls
  - Implement custom model path input and validation interface using pathlib path browser
  - Create model download and validation functionality with GPU support detection using pathlib for model storage
  - Add re-encoding trigger interface for existing documents with new model and GPU acceleration
  - _Requirements: 6.2, 6.5_

- [ ] 11.2 Implement search behavior and topic hierarchy settings
  - Add toggle controls for AI semantic search enable/disable
  - Implement fallback to pre-encoded files only mode setting
  - Create fuzzy search sensitivity and threshold controls (80% accuracy target)
  - Add topic hierarchy generation and management controls
  - Implement topic tree depth and refresh settings
  - Write GUI unit tests for settings persistence and validation
  - _Requirements: 1.2, 4.1, 6.5_

- [ ] 11.3 Implement file and directory management interface
  - Add "Add Files" button that launches native file browser (Dolphin on Linux, Explorer on Windows, Finder on macOS)
  - Implement directory browser for document collection management using QFileDialog
  - Add file list display with remove/edit capabilities for configured document directories
  - Create cross-platform file browser integration using pathlib and QFileDialog
  - Add drag-and-drop support for files and directories with automatic copying to designated document folder
  - Implement file copying mechanism using pathlib when files are dragged onto the application
  - Create configurable document storage directory with automatic organization
  - Write unit tests for file browser integration, drag-and-drop, and file copying functionality
  - _Requirements: 6.2_

- [ ] 12. Create document viewer window GUI components
- [ ] 12.1 Implement extensible document viewer architecture
  - Create DocumentViewerWindow base class with common viewer functionality
  - Define DocumentViewer interface for file-type-specific rendering
  - Implement viewer factory pattern for selecting appropriate viewer
  - Add common navigation controls and zoom functionality
  - _Requirements: 3.2, 3.3, 3.4_

- [ ] 12.2 Implement PDF viewer with Qt PDF rendering
  - Create PDFViewer class implementing DocumentViewer interface
  - Integrate QPdfView widget for PDF rendering
  - Add search term highlighting overlay using custom QPainter
  - Create navigation between multiple search results in same document
  - _Requirements: 3.2, 3.3, 3.4_

- [ ] 12.3 Implement text-based document viewers for multi-format support
  - Create TextViewer class for .txt and .md files using QTextEdit
  - Add syntax highlighting for markdown files
  - Implement search term highlighting for text-based documents
  - Create simple navigation for text documents without page concept
  - _Requirements: 3.2, 3.3, 3.4_

- [ ] 12.4 Implement document viewer performance optimizations
  - Add lazy content loading with background QThread operations (mandatory)
  - Implement LRU cache for rendered document content (max 50 documents)
  - Add memory cleanup for large document objects with 1GB limit monitoring
  - Create progress indicators for document loading operations
  - Load active page ± 10 pages, unload distant pages during scrolling
  - Write performance tests for large document handling
  - _Requirements: 5.2, 5.3, 5.5_

- [ ] 13. Implement background processing and threading with GPU acceleration
  - Create QThread workers for multi-format document indexing operations (mandatory for UI responsiveness)
  - Implement background directory watching with file system events for all supported file types
  - Add GPU-accelerated progress reporting for long-running indexing and re-encoding operations
  - Create thread-safe communication between workers and GUI with GPU memory management
  - Implement background topic hierarchy generation with GPU acceleration and progress updates
  - Use joblib for CPU-bound parallel processing when GPU is unavailable or busy
  - Write tests for concurrent operations and thread safety with multiple file formats and GPU operations
  - _Requirements: 2.3, 5.2, 5.4_

- [ ] 14. Add comprehensive error handling and user feedback
  - Implement error dialog components with actionable troubleshooting steps
  - Add status bar indicators for service connectivity, indexing progress, and re-encoding status
  - Create logging configuration with structured format and file rotation
  - Implement graceful degradation when services are unavailable or AI is disabled
  - Add error handling for model loading failures and re-encoding errors
  - Handle corrupted and password-protected PDF files gracefully (log and continue)
  - Write error scenario tests for all major failure modes
  - _Requirements: 2.4, 6.4, 5.4_

- [ ] 15. Create application entry point and main window coordination
  - Implement main.py with application initialization and automatic service startup using pathlib
  - Create main application class that manages search, viewer, and settings windows
  - Add application configuration loading and validation on startup with pathlib path resolution
  - Implement clean shutdown procedures with resource cleanup and Cython extension cleanup
  - Add command-line argument parsing for configuration overrides with pathlib path handling
  - Verify all required services are running and display status on startup
  - Write end-to-end integration tests for complete application workflows
  - _Requirements: 6.1, 6.3, 3.1, 3.5_
