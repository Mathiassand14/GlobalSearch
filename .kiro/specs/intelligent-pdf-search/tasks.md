# Implementation Plan

- [ ] 1. Set up project foundation and dependencies for Tauri + FastAPI architecture
  - Create project directory structure following clean architecture (src/core/, src/api/, src-tauri/, src/, config/, tests/)
  - Create backend requirements with FastAPI dependencies (fastapi, uvicorn, pdfplumber, elasticsearch, sentence-transformers, rapidfuzz, numba)
  - Set up Tauri project structure with React/TypeScript frontend
  - Set up Docker Compose configuration for FastAPI backend and Elasticsearch services
  - Create pyproject.toml for UV package management for backend
  - Create package.json with Tauri dependencies for native desktop application
  - Create Cargo.toml for Rust backend dependencies
  - Create basic .gitignore for Python, JavaScript, and Rust projects
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

- [x] 4. Implement extensible document processing architecture
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

- [x] 5. Implement Docker service management
  - Create DockerServiceManager class for automatic service startup
  - Implement service health checking and startup verification
  - Add clear error messaging with troubleshooting guidance for service failures
  - Create docker-compose.yml with Elasticsearch configuration
  - Write integration tests for service management
  - _Requirements: 6.1, 6.3, 6.4_

- [x] 5.1 Optimize docker-compose.yml for PDF search application requirements
  - Remove unnecessary services (PostgreSQL, Redis) that are not required for PDF search functionality
  - Keep only Elasticsearch service (required for search indexing and semantic search)
  - Add application service configuration with proper build context and multi-stage target specification
  - Configure service dependencies with health checks (app depends on healthy Elasticsearch)
  - Add volume mounts for documents, config, and logs directories using pathlib-compatible paths
  - Set appropriate environment variables for Elasticsearch connection and document storage paths
  - Add resource limits and restart policies for production deployment stability
  - Update service networking and port configurations optimized for desktop application use case
  - Create .dockerignore file to optimize build context and reduce image size
  - Write docker-compose validation tests to ensure services start correctly and communicate properly
  - _Requirements: 6.1, 6.3, 6.4_

- [x] 5.2 Fix Docker Compose configuration issues and warnings
  - Remove obsolete `version` attribute from docker-compose.yml (Docker Compose v2+ no longer requires it)
  - Clean up orphaned containers using `docker-compose down --remove-orphans` command
  - Add UV_LINK_MODE=copy environment variable to suppress hardlink warnings in containerized environments
  - Configure proper volume mounting to avoid filesystem hardlink issues between host and container
  - Add container cleanup and restart policies to prevent orphaned container accumulation
  - Update Dockerfile to set UV_LINK_MODE=copy for consistent behavior across different filesystems
  - Add docker-compose.override.yml to .gitignore to prevent IDE-generated override files from being committed
  - Write validation script to check for common Docker Compose configuration issues
  - _Requirements: 6.1, 6.4_

- [x] 5.3 Optimize UV package management in Docker containers
  - Set UV_LINK_MODE=copy environment variable in Dockerfile to prevent hardlink warnings
  - Configure UV cache directory to use container-local storage for better performance
  - Add UV optimization flags for containerized environments (--no-cache, --frozen)
  - Implement multi-stage build optimization to reduce final image size and dependency download time
  - Add UV environment variables for consistent behavior across development and production containers
  - Configure proper UV workspace detection for containerized Python applications
  - Write Docker build optimization tests to verify UV performance improvements
  - _Requirements: 6.8_

- [x] 5.4 Fix PyQt6 dependency and GUI container support
  - Add system dependencies for PyQt6 in Dockerfile (libgl1-mesa-glx, libxkbcommon-x11-0, libxcb-xinerama0, python3-pyqt6)
  - Verify PyQt6 is properly included in pyproject.toml dependencies and UV sync operations
  - Configure X11 forwarding for GUI applications in Docker containers with DISPLAY environment variable
  - Add X11 socket volume mounts (/tmp/.X11-unix:/tmp/.X11-unix:rw) for GUI support in Linux environments
  - Create headless mode fallback when GUI is not available in container environment using QT_QPA_PLATFORM=offscreen
  - Add separate docker-compose profiles for GUI vs headless operation modes
  - Configure xvfb-run wrapper for headless GUI testing in containerized CI/CD environments
  - Add proper Qt platform plugin configuration for container environments
  - Write tests to verify PyQt6 imports and GUI initialization work correctly in both GUI and headless modes
  - _Requirements: 6.1, 6.8_

- [x] 6. Implement Elasticsearch integration and indexing
  - Create IndexManager class with Elasticsearch client configuration
  - Implement document indexing with text content and metadata storage
  - Add GPU-accelerated vector embedding generation using sentence-transformers (all-MiniLM-L6-v2 mandatory model)
  - Create index schema with dense_vector fields for semantic search and topic hierarchy
  - Implement bulk indexing operations with joblib parallel processing for performance optimization
  - Add re-encoding functionality for switching embedding models with GPU acceleration
  - Implement topic hierarchy generation using AI clustering of document embeddings with parallel processing
  - Write integration tests with test Elasticsearch instance
  - _Requirements: 2.1, 2.3, 1.2, 5.1_

- [x] 7. Implement search strategies and search manager
- [x] 7.1 Create exact search strategy with Elasticsearch queries
  - Implement ExactSearchStrategy class with boolean operator support (AND, OR, NOT)
  - Add query parsing and validation for complex search expressions
  - Ensure sub-500ms response time for collections under 1000 documents
  - Write unit tests for query parsing and exact matching
  - _Requirements: 1.1, 4.4, 5.1_

- [x] 7.2 Create fuzzy search strategy with spelling correction using rapidfuzz
  - Implement FuzzySearchStrategy using Elasticsearch fuzzy queries and rapidfuzz (mandatory library)
  - Add automatic spelling suggestion generation for failed searches
  - Configure edit distance parameters and confidence thresholds (80% accuracy target)
  - Highlight match confidence levels for user feedback
  - Write unit tests for fuzzy matching and spelling correction
  - _Requirements: 1.1, 1.4, 1.5_

- [x] 7.3 Create semantic search strategy with GPU-accelerated AI embeddings
  - Implement SemanticSearchStrategy using sentence-transformers embeddings with GPU acceleration
  - Add GPU-accelerated cosine similarity search with configurable threshold (default 0.7)
  - Implement embedding caching for performance optimization with GPU memory management
  - Add toggle functionality to disable AI search and use only pre-encoded files
  - Implement automatic GPU/CPU fallback based on hardware availability
  - Write unit tests for semantic similarity matching and AI toggle behavior
  - _Requirements: 1.2, 4.1_

- [x] 7.4 Implement search manager orchestration
  - Create SearchManager class that coordinates all search strategies
  - Implement auto-complete suggestions based on indexed content
  - Add search result ranking and relevance scoring
  - Implement search result caching with TTL expiration
  - Add hierarchical topic search functionality (e.g., "algorithms > trees")
  - Implement topic tree navigation and filtering
  - Write integration tests for multi-strategy search coordination and topic hierarchy
  - _Requirements: 1.3, 4.5, 5.1_

- [x] 8. Implement performance optimization modules
- [x] 8.1 Create GPU and Numba-accelerated operations
  - Implement numba_ops.py with @jit decorated cosine similarity functions with GPU support
  - Add GPU-accelerated batch embedding processing functions for re-encoding operations
  - Create vector distance computation functions for semantic search with GPU acceleration
  - Implement joblib parallel processing for CPU-bound operations when GPU unavailable
  - Add automatic GPU/CPU device selection and memory management
  - Write performance benchmarks comparing GPU vs CPU vs standard implementations
  - _Requirements: 5.1, 5.3_

- [x] 8.2 Create Cython extensions for text processing with parallel support
  - Implement text_processing.pyx with fast tokenization functions
  - Add optimized fuzzy matching loops for large datasets with joblib parallel processing
  - Create high-performance document parsing routines with multi-threading support
  - Set up automatic Cython compilation during package installation
  - Implement parallel text processing for batch operations using joblib
  - Write unit tests for Cython extension functionality and parallel processing
  - _Requirements: 1.1, 2.1, 5.1_

- [x] 9. Implement event bus for inter-window communication
  - Create EventBus class using observer pattern for decoupled window communication
  - Define event types (SearchResultSelected, DocumentOpened, WindowClosed, IndexingProgress)
  - Implement subscribe/publish/unsubscribe methods with type safety
  - Add thread-safe event handling for GUI operations
  - Write unit tests for event bus functionality
  - _Requirements: 3.2, 3.3, 3.5_

- [x] 10. Create FastAPI backend endpoints
- [x] 10.1 Implement main FastAPI application and middleware
  - Create FastAPI application with automatic OpenAPI documentation
  - Add CORS middleware for frontend communication
  - Implement file upload middleware for multipart form data handling
  - Add error handling middleware with standardized error responses
  - Create request logging and performance monitoring middleware
  - Add health check endpoint for service monitoring
  - _Requirements: 3.1, 6.1, 6.3_

- [ ] 10.2 Implement search API endpoints
  - Create GET /api/search endpoint with query parameters for basic search
  - Add GET /api/search/suggestions endpoint for auto-complete functionality
  - Implement GET /api/search/topics endpoint for hierarchical topic tree
  - Create POST /api/search/advanced endpoint for complex search with JSON body
  - Add proper HTTP status codes and error handling for all endpoints
  - Implement pagination and sorting in search responses
  - Write API unit tests using FastAPI TestClient
  - _Requirements: 1.1, 1.3, 4.2, 4.5_

- [ ] 11. Create document management API endpoints
- [ ] 11.1 Implement document upload and management endpoints
  - Create POST /api/documents/upload endpoint with multipart form data support
  - Add progress tracking for file uploads using WebSocket connections
  - Implement GET /api/documents endpoint with pagination and filtering
  - Create GET /api/documents/{id} endpoint for document retrieval
  - Add DELETE /api/documents/{id} endpoint with index cleanup
  - Implement file validation and error handling for unsupported formats
  - Write API tests for document upload and management operations
  - _Requirements: 7.1, 7.2, 7.6_

- [ ] 11.2 Implement configuration API endpoints
  - Create GET /api/config endpoint for application configuration retrieval
  - Add PUT /api/config endpoint for configuration updates with validation
  - Implement GET /api/config/models endpoint for available AI models
  - Create POST /api/config/models/switch endpoint for model switching
  - Add configuration persistence and validation on the backend
  - Write API tests for configuration management
  - _Requirements: 6.5, 6.7_

- [ ] 11.3 Implement file streaming and content delivery
  - Create GET /api/documents/{id}/content endpoint for document content streaming
  - Add GET /api/documents/{id}/pages/{page} endpoint for page-specific content
  - Implement efficient file serving with proper HTTP headers and caching
  - Add support for range requests for large file streaming
  - Create thumbnail generation endpoint for document previews
  - Write performance tests for file streaming operations
  - _Requirements: 3.2, 3.4, 5.2_

- [ ] 12. Create Tauri native desktop application
- [ ] 12.1 Set up Tauri project with multi-window architecture and service management
  - Initialize Tauri project with React/TypeScript configuration
  - Set up build system with Vite for development and production
  - Configure ESLint and Prettier for code quality and formatting
  - Add CSS framework (Tailwind) for responsive design
  - Set up Tauri window management for multiple independent windows
  - Configure Tauri permissions for file system access, dialogs, window management, and shell commands
  - Implement Rust service manager for automatic Docker service startup and management
  - Add Docker CLI integration for service lifecycle management from native application
  - _Requirements: 8.3, 3.1, 6.1_

- [ ] 12.2 Implement main search window
  - Create main search window with native window controls
  - Implement search input component with debounced API calls (300ms delay)
  - Add advanced filters panel with date range, file type, and relevance controls
  - Implement search results list with pagination and virtual scrolling
  - Create auto-complete dropdown with API integration
  - Add hierarchical topic tree navigation component
  - Implement search result sorting and filtering options
  - Add window state management (position, size, docking)
  - _Requirements: 3.1, 1.1, 1.3, 4.2, 4.5_

- [ ] 12.3 Implement document viewer windows
  - Create independent document viewer windows for each opened document
  - Integrate native PDF rendering libraries for optimal performance
  - Create text document viewer with syntax highlighting for markdown
  - Add search term highlighting overlay for all document types
  - Implement navigation controls (page navigation, zoom, search result jumping)
  - Add lazy loading for large documents with native performance optimization
  - Create document thumbnail and preview components
  - Implement window independence (move, resize, minimize, close individually)
  - _Requirements: 3.2, 3.3, 3.4, 3.7_

- [ ] 12.4 Implement native file management integration
  - Integrate Tauri file system APIs for native file operations
  - Create native file dialogs for file selection and management
  - Implement native drag-and-drop support for files and folders
  - Add file validation and progress tracking for file operations
  - Create native file browser integration for document management
  - Implement file watching for automatic index updates
  - Write tests for native file operations and drag-and-drop functionality
  - _Requirements: 7.1, 7.2, 7.6_

- [ ] 13. Implement inter-window communication and state management
- [ ] 13.1 Create Tauri event system for window communication
  - Set up Tauri event system for communication between windows
  - Implement event handlers for search result selection, document opening
  - Create shared state management across multiple windows
  - Add window lifecycle management (creation, destruction, focus)
  - Implement window coordination for search and document viewing
  - Create event-driven architecture for decoupled window communication
  - Write tests for inter-window communication and state synchronization
  - _Requirements: 3.2, 3.5, 3.7_

- [ ] 13.2 Implement service management and native OS integration
  - Implement automatic backend service detection and startup on application launch
  - Create service health monitoring with real-time status updates in UI
  - Add service lifecycle management (start, stop, restart) from native application
  - Set up native OS notifications for service status and processing completion
  - Create native system tray integration for background service operation
  - Implement native keyboard shortcuts and menu integration
  - Add native window management (docking, snapping, workspace integration)
  - Create native file association for supported document types
  - Implement native clipboard integration for search and content
  - Write tests for service management and native OS integration features
  - _Requirements: 6.1, 6.3, 6.4, 7.7_

- [ ] 14. Implement settings window and configuration interface
- [ ] 14.1 Create native settings window
  - Implement settings window with native controls and tabbed interface (AI Models, Search, Performance)
  - Add AI model selection dropdown with download and switching functionality
  - Create search behavior toggles (AI search enable/disable, fuzzy matching sensitivity)
  - Implement performance settings (cache size, timeout configuration)
  - Add service status monitoring display with health indicators
  - Create configuration validation and persistence using Tauri storage APIs
  - Implement window management for settings (modal or independent window)
  - Write tests for settings window and API integration
  - _Requirements: 6.5, 6.7, 1.2_

- [ ] 14.2 Add comprehensive error handling and native user feedback
  - Implement native error dialogs for graceful error handling
  - Add native notifications for user feedback and status updates
  - Create loading states and progress indicators for better user experience
  - Implement retry mechanisms for failed API requests
  - Add offline detection and graceful degradation with native indicators
  - Create error logging and reporting functionality using Tauri logging
  - Write error scenario tests for native components
  - _Requirements: 2.4, 6.4, 5.4_

- [ ] 15. Create application packaging and deployment configuration
- [ ] 15.1 Implement Docker Compose configuration for backend services
  - Create docker-compose.yml with FastAPI backend and Elasticsearch services
  - Configure service dependencies and health checks for proper startup order
  - Add volume mounts for document storage, configuration, and logs
  - Set up environment variables for service configuration
  - Create production-ready Docker images with multi-stage builds
  - Remove web frontend services (replaced by native Tauri application)
  - _Requirements: 6.1, 6.3_

- [ ] 15.2 Create Tauri application packaging and distribution
  - Configure Tauri build system for cross-platform compilation (Windows, macOS, Linux)
  - Set up application signing and notarization for distribution
  - Create installer packages for each target platform
  - Implement auto-updater functionality for seamless updates
  - Add application metadata and icons for proper OS integration
  - Create distribution scripts for automated builds and releases
  - Write end-to-end integration tests for complete application workflows
  - _Requirements: 6.1, 6.3, 3.1_

- [ ] 15.3 Remove unnecessary web application components
  - Remove web-specific dependencies and configuration
  - Clean up web-specific routing and navigation code
  - Remove web browser compatibility code and polyfills
  - Update project structure to focus on native desktop + API architecture
  - Remove web-specific performance optimizations (virtual scrolling, lazy loading)
  - Clean up web deployment and serving configuration
  - Update documentation to reflect native desktop architecture
  - _Requirements: 8.2, 8.3_
