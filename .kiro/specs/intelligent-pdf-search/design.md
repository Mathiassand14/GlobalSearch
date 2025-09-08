# Design Document - Intelligent Multi-Format Document Search Application

## Overview

The Intelligent Multi-Format Document Search Application is a native desktop application built with Tauri and React that provides advanced search capabilities across diverse document collections. The application features multiple independent windows that can be dragged, docked, and managed like an IDE, with a FastAPI backend for document processing and search operations. The application combines exact text matching, fuzzy search for spelling tolerance, and semantic AI-powered search to help users find relevant content efficiently across PDF, DOCX, TXT, and Markdown files.

The system addresses the core user need for intelligent document discovery with spelling mistake tolerance and semantic understanding, enabling researchers, legal professionals, and students to efficiently navigate large document collections without requiring perfect recall of exact terms.

The system follows a clean architecture with clear separation between the native desktop frontend, API layer, and business logic, ensuring testability and maintainability. The application leverages containerized Elasticsearch for powerful indexing and search capabilities, with AI embeddings for semantic understanding. The multi-window desktop interface provides an IDE-like experience optimized for research workflows with independent document viewers and search panels.

### Technology Stack Decision

**Mandatory Technology Stack (Non-negotiable):**

The design uses **FastAPI backend + Web frontend architecture** with the following fixed technology choices:

**Backend:**
1. **Python 3.11+**: Required for modern type hints and performance optimizations, with mandatory type hints on all functions and classes
2. **FastAPI**: Exclusive API framework choice for high-performance async web APIs with automatic OpenAPI documentation
3. **pdfplumber**: Mandatory PDF processing library (never PyMuPDF) for reliable text extraction
4. **Elasticsearch**: Required search engine with containerized deployment via Docker Compose
5. **sentence-transformers (all-MiniLM-L6-v2)**: Specific model for semantic search embeddings
6. **rapidfuzz**: Required fuzzy matching library (never fuzzywuzzy) for spelling correction
7. **UV**: Mandatory package manager for dependency management
8. **Numba**: JIT compilation for performance-critical numerical operations (embedding calculations, similarity computations)

**Frontend:**
9. **Tauri**: Native desktop application framework with Rust backend and web frontend
10. **React/TypeScript**: Modern reactive framework for component-based UI development with type safety
11. **Native PDF Rendering**: Platform-specific PDF libraries for optimal performance
12. **Native OS Integration**: File dialogs, drag-and-drop, window management APIs

**Infrastructure:**
13. **Docker Compose**: Required for service orchestration (FastAPI, Elasticsearch)
14. **Multi-Window Architecture**: Independent native windows with inter-window communication

**Architecture Rationale:**
- **Performance Requirements**: Sub-500ms search response for collections under 1000 documents
- **Memory Management**: 1GB memory limit with explicit cleanup and LRU caching
- **UI Responsiveness**: QThread mandatory for all I/O operations to prevent UI blocking
- **Code Standards**: snake_case naming, PascalCase classes, comprehensive type hints
- **Service Integration**: Automatic Docker service startup with health checking

## Architecture

### High-Level Architecture

The application is structured in four main layers:

1. **Native Desktop Frontend (Tauri)**: Multi-window native application with React components
2. **FastAPI Backend**: RESTful API layer handling HTTP requests and responses
3. **Core Business Logic**: Framework-agnostic business operations and services  
4. **Data Layer**: External services and storage systems (Elasticsearch, file storage)

### Design Principles

1. **Framework-Agnostic Core**: All business logic resides in `src/core/` and can be tested independently of the API framework
2. **RESTful API Design**: Clean HTTP endpoints with proper status codes and standardized request/response formats
3. **Repository Pattern**: All data access operations are abstracted through repository interfaces
4. **Separation of Concerns**: Native frontend handles presentation and window management, API handles routing, core services handle business logic
5. **Extensible Architecture**: Document processors use plugin architecture for multi-format support
6. **Performance-First Design**: All operations use async/await patterns with background processing and caching
7. **Stateless API**: Backend API maintains no session state, enabling horizontal scaling

## Components and Interfaces

### Core Components

#### Search Manager 
**File:** `#[[file:src/core/search/search_manager.py]]`
- **Purpose**: Orchestrates all search operations and coordinates between different search strategies with auto-complete and spelling correction
- **Key Methods**:
  - `search(query: str, options: SearchOptions) -> SearchResults`
  - `get_suggestions(partial_query: str) -> List[str]`  # Auto-complete based on indexed content
  - `add_search_strategy(strategy: SearchStrategy) -> None`
  - `get_spelling_suggestions(query: str) -> List[str]`  # For failed searches
  - `search_with_fallback(query: str, options: SearchOptions) -> SearchResults`
  - `parse_boolean_query(query: str) -> ParsedQuery`  # Support AND, OR, NOT operators
  - `apply_filters(results: SearchResults, filters: SearchFilters) -> SearchResults`  # Date, file type, relevance
  - `search_hierarchical_topics(topic_path: str) -> SearchResults`  # Search within topic hierarchy
  - `get_topic_tree() -> TopicTree`  # Get hierarchical topic structure

#### Document Manager
**File:** `#[[file:src/core/documents/document_manager.py]]`
- **Purpose**: Handles multi-format document operations (PDF, DOCX, TXT, MD), text extraction, and document management using pluggable processors with automatic directory monitoring
- **Key Methods**:
  - `extract_text(file_path: str) -> DocumentContent`
  - `get_page_content(file_path: str, page_num: int) -> PageContent`
  - `register_processor(file_extension: str, processor: DocumentProcessor) -> None`
  - `watch_directory(directory: str) -> None`
  - `get_supported_formats() -> List[str]`  # Returns ['.pdf', '.docx', '.txt', '.md']
  - `process_directory(directory: str) -> IndexingStatus`
  - `handle_corrupted_files(file_path: str, error: Exception) -> None`

#### Document Processor Interface
**File:** `#[[file:src/core/documents/processors/base_processor.py]]`
- **Purpose**: Abstract interface for file type-specific document processing
- **Key Methods**:
  - `can_process(file_path: str) -> bool`
  - `extract_text(file_path: str) -> DocumentContent`
  - `get_page_count(file_path: str) -> int`
  - `get_page_content(file_path: str, page_num: int) -> PageContent`

#### Index Manager
**File:** `#[[file:src/core/indexing/index_manager.py]]`
- **Purpose**: Manages Elasticsearch indexing operations and document metadata with background processing
- **Key Methods**:
  - `index_document(document: Document) -> bool`
  - `update_index() -> None`
  - `get_index_status() -> IndexStatus`
  - `bulk_index_documents(documents: List[Document]) -> IndexingResult`
  - `watch_directory_changes(directory: str) -> None`
  - `re_encode_documents(model_name: str) -> ReEncodingResult`  # Re-encode with different model
  - `generate_topic_hierarchy(documents: List[Document]) -> TopicTree`  # Create hierarchical topics

#### Event Bus
**File:** `#[[file:src/core/events/event_bus.py]]`
- **Purpose**: Manages inter-window communication using observer pattern for loose coupling
- **Key Methods**:
  - `subscribe(event_type: str, callback: Callable) -> None`
  - `publish(event: Event) -> None`
  - `unsubscribe(event_type: str, callback: Callable) -> None`
- **Events**: SearchResultSelected, DocumentOpened, WindowClosed, IndexingProgress

#### Performance Optimization Modules
**Directory:** `#[[file:src/core/performance/]]`
- **Numba Accelerated Operations** `#[[file:src/core/performance/numba_ops.py]]`:
  - `@jit` decorated cosine similarity calculations
  - Batch embedding processing for re-encoding operations
  - Vector distance computations for semantic search
- **Cython Extensions** `#[[file:src/core/performance/text_processing.pyx]]`:
  - Fast text tokenization and preprocessing
  - Optimized fuzzy matching loops for large datasets
  - High-performance document parsing routines
- **Compilation**: Automatic Cython compilation during package installation

### Search Strategies

#### Exact Search Strategy
- **Implementation**: Direct Elasticsearch query matching
- **Use Case**: Precise term matching with boolean operators
- **Performance**: Sub-100ms response time

#### Fuzzy Search Strategy
- **Implementation**: Combines Elasticsearch fuzzy queries with rapidfuzz for local matching (mandatory library choice)
- **Configuration**: Configurable edit distance (default: 2) with 80% accuracy target as specified in requirements
- **Confidence Scoring**: Highlights match confidence levels for user feedback
- **Fallback**: Automatic spelling correction suggestions when no exact matches found
- **Performance**: 
  - Contributes to sub-500ms search response requirement
  - **Cython-optimized** text preprocessing for large document collections
  - **Numba-accelerated** similarity scoring for fuzzy match ranking

#### Semantic Search Strategy
- **Implementation**: sentence-transformers (all-MiniLM-L6-v2) for embedding generation (mandatory model choice)
- **Storage**: Vector embeddings stored in Elasticsearch dense_vector fields
- **Similarity**: Cosine similarity with configurable threshold (default: 0.7)
- **Performance**: 
  - Embedding caching for repeated queries to meet response time requirements
  - **Numba-optimized** cosine similarity calculations for large result sets
  - **Numba JIT** compilation for batch embedding operations during re-encoding
### API Layer Components

#### FastAPI Application
**File:** `src/api/main.py`
- **Framework**: FastAPI with automatic OpenAPI documentation generation
- **Middleware**: CORS, file upload handling, error handling, request logging
- **Authentication**: Optional JWT-based authentication for multi-user scenarios
- **File Upload**: Multipart form data handling for drag-and-drop file uploads
- **WebSocket**: Real-time progress updates for long-running operations

#### Search API Endpoints
**File:** `src/api/routes/search.py`
- **GET /api/search**: Main search endpoint with query parameters for filters
- **GET /api/search/suggestions**: Auto-complete suggestions endpoint
- **GET /api/search/topics**: Hierarchical topic tree endpoint
- **POST /api/search/advanced**: Complex search with JSON body for advanced filters
- **Response Format**: Standardized JSON with pagination, metadata, and error handling

#### Document API Endpoints
**File:** `src/api/routes/documents.py`
- **POST /api/documents/upload**: File upload endpoint with progress tracking
- **GET /api/documents/{id}**: Document retrieval with content streaming
- **GET /api/documents/{id}/pages/{page}**: Page-specific content for large documents
- **DELETE /api/documents/{id}**: Document deletion with index cleanup
- **GET /api/documents**: Document listing with pagination and filtering

#### Configuration API Endpoints
**File:** `src/api/routes/config.py`
- **GET /api/config**: Application configuration retrieval
- **PUT /api/config**: Configuration updates with validation
- **GET /api/config/models**: Available AI models listing
- **POST /api/config/models/switch**: Model switching with re-encoding trigger
- **GET /api/health**: Service health check endpoint

### Tauri Desktop Frontend Components

#### Main Application Window
**File:** `src-tauri/src/main.rs` + `frontend/src/App.tsx`
- **Window Management**: Multi-window architecture with independent search and document windows
- **State Management**: Global state for search results, configuration, and UI state shared across windows
- **Native Integration**: OS-level window management, file dialogs, drag-and-drop
- **Error Handling**: Native error dialogs with user-friendly error messages

#### Search Window Component
**File:** `frontend/src/windows/SearchWindow.tsx`
- **Features**:
  - Real-time search with debounced input (300ms delay)
  - Advanced filters panel (date range, file type, relevance threshold)
  - Results list with pagination and sorting options
  - Auto-complete dropdown with API integration
  - Spelling correction suggestions display
  - Hierarchical topic tree navigation
- **Window Management**: Can be docked or floating, resizable, minimizable
- **API Integration**: RESTful API calls with proper error handling and loading states

#### Document Viewer Window Component
**File:** `frontend/src/windows/DocumentViewerWindow.tsx`
- **Multi-format Support**: Native PDF rendering for PDFs, custom viewers for text-based documents
- **PDF Rendering**: Platform-specific PDF libraries with custom highlight overlay for search terms
- **Text Rendering**: Syntax-highlighted display for markdown and code files
- **Navigation**: Page controls, search result jumping, zoom controls
- **Window Independence**: Each document opens in its own window, can be moved/resized independently
- **Highlighting**: Dynamic text highlighting based on search terms

#### Native File Management Component
**File:** `frontend/src/components/FileManager.tsx`
- **Drag-and-Drop**: Native OS drag-and-drop API integration via Tauri
- **File Dialogs**: Native file picker dialogs for file selection
- **Progress Tracking**: Real-time progress bars for file processing
- **File Validation**: Client-side file type and size validation
- **Batch Processing**: Multiple file selection and parallel processing
- **Error Handling**: Native error dialogs for file operation failures

#### Settings Window Component
**File:** `frontend/src/windows/SettingsWindow.tsx`
- **Configuration Management**: Native form controls for configuration editing with validation
- **AI Model Management**: Model selection, download progress, switching interface
- **Search Behavior**: Toggle controls for AI search, fuzzy matching sensitivity
- **Performance Settings**: Cache size, timeout configuration
- **Service Status**: Real-time service health monitoring display
- **Window Management**: Modal or independent window for settings

#### Service Management Component (Tauri Backend)
**File:** `src-tauri/src/services/service_manager.rs`
- **Automatic Service Startup**: Detects and launches required backend services on application startup
- **Docker Integration**: Uses Docker CLI or Docker API to manage containerized services
- **Health Monitoring**: Continuously monitors service health and displays status in UI
- **Service Discovery**: Automatically detects if services are already running
- **Error Handling**: Provides detailed error messages and troubleshooting guidance
- **Lifecycle Management**: Properly shuts down services when application closes

## Data Models

### Document Model
```python
@dataclass
class Document:
    id: str
    file_path: str
    title: str
    content: str
    page_count: int
    file_size: int
    created_date: datetime
    modified_date: datetime
    metadata: Dict[str, Any]
```

### Search Result Model
```python
@dataclass
class SearchResult:
    document_id: str
    document_title: str
    page_number: int
    snippet: str
    relevance_score: float
    match_type: MatchType  # EXACT, FUZZY, SEMANTIC
    highlighted_text: str
    topic_path: Optional[str] = None  # e.g., "algorithms/trees/binary_trees"

@dataclass
class TopicNode:
    name: str
    path: str
    children: List['TopicNode']
    document_count: int
    relevance_score: float

@dataclass
class TopicTree:
    root_nodes: List[TopicNode]
    total_topics: int
    generation_timestamp: datetime
```

### Configuration Model
```python
@dataclass
class ApplicationConfig:
    elasticsearch_url: str = "http://localhost:9200"
    document_directories: List[str]
    supported_file_types: List[str] = field(default_factory=lambda: ['.pdf', '.docx', '.txt', '.md'])
    search_settings: SearchSettings
    ui_settings: UISettings
    performance_settings: PerformanceSettings
    docker_services: DockerServiceConfig

@dataclass
class SearchSettings:
    fuzzy_edit_distance: int = 2
    fuzzy_accuracy_target: float = 0.8  # 80% accuracy requirement
    semantic_similarity_threshold: float = 0.7
    search_timeout_seconds: int = 2  # Sub-2-second requirement
    core_search_timeout_ms: int = 500  # Sub-500ms for core search
    enable_auto_complete: bool = True
    enable_spelling_correction: bool = True
    enable_boolean_operators: bool = True  # AND, OR, NOT support
    enable_ai_search: bool = True  # Toggle for AI semantic search
    fallback_to_preencoded_only: bool = False  # Use only pre-encoded files
    current_model_name: str = "all-MiniLM-L6-v2"  # Current embedding model
    custom_model_path: Optional[str] = None  # Path to custom model
    enable_topic_hierarchy: bool = True  # Enable hierarchical topic tree
    topic_hierarchy_depth: int = 3  # Maximum depth for topic tree

@dataclass
class PerformanceSettings:
    max_cached_documents: int = 50
    max_memory_usage_gb: float = 1.0  # Hard limit as per requirements
    indexing_batch_size: int = 100
    search_debounce_ms: int = 300  # Exact requirement specification
    page_preload_range: int = 10  # Load active page ± 10 pages
    auto_cleanup_threshold: float = 0.8  # Cleanup when 80% of memory limit reached
    max_collection_size_fast_search: int = 1000  # Performance guarantee threshold

@dataclass
class DockerServiceConfig:
    auto_start_services: bool = True  # Automatic startup requirement
    elasticsearch_port: int = 9200
    health_check_timeout: int = 30
    required_services: List[str] = field(default_factory=lambda: ["elasticsearch"])
    service_startup_verification: bool = True  # Verify all services on startup
```

### Document Processor Models
```python
@dataclass
class DocumentContent:
    text: str
    page_count: int
    metadata: Dict[str, Any]
    file_type: str
    file_path: str
    created_date: datetime
    modified_date: datetime

@dataclass
class PageContent:
    page_number: int
    text: str
    images: List[bytes]
    metadata: Dict[str, Any]

class DocumentProcessor(ABC):
    @abstractmethod
    def can_process(self, file_path: str) -> bool:
        """Check if this processor can handle the given file type"""
        pass
    
    @abstractmethod
    def extract_text(self, file_path: str) -> DocumentContent:
        """Extract full document text with metadata preservation"""
        pass
    
    @abstractmethod
    def get_page_content(self, file_path: str, page_num: int) -> PageContent:
        """Extract specific page content for viewer display"""
        pass
    
    @abstractmethod
    def handle_processing_error(self, file_path: str, error: Exception) -> None:
        """Handle corrupted or password-protected files gracefully"""
        pass

# Concrete processor implementations for multi-format support
class PDFProcessor(DocumentProcessor):
    """PDF processing using pdfplumber (mandatory library choice)"""
    pass

class DocxProcessor(DocumentProcessor):
    """Microsoft Word document processing"""
    pass

class TextProcessor(DocumentProcessor):
    """Plain text and markdown file processing with encoding detection"""
    pass

### Service Management Models
```python
@dataclass
class ServiceStatus:
    service_name: str
    is_running: bool
    health_status: str
    error_message: Optional[str] = None

@dataclass
class IndexingStatus:
    total_documents: int
    processed_documents: int
    failed_documents: int
    is_complete: bool
    current_file: Optional[str] = None

@dataclass
class ReEncodingResult:
    total_documents: int
    re_encoded_documents: int
    failed_documents: int
    old_model: str
    new_model: str
    is_complete: bool
    estimated_time_remaining: Optional[int] = None  # seconds

class ServiceManager:
    def start_docker_services(self) -> List[ServiceStatus]:
        """Start required Docker services with health checking"""
        pass
    
    def verify_service_health(self, service_name: str) -> ServiceStatus:
        """Verify individual service health"""
        pass
    
    def get_all_service_status(self) -> List[ServiceStatus]:
        """Get status of all required services"""
        pass
```

## Error Handling

### Error Categories

1. **Service Connectivity Errors**
   - Elasticsearch connection failures
   - Docker service unavailability
   - Network timeouts

2. **File Processing Errors**
   - Corrupted PDF files (requirement 2.4: log error and continue processing)
   - Password-protected documents (requirement 2.4: graceful handling)
   - Insufficient file permissions
   - Unsupported file formats within supported extensions
   - Encoding issues in text files

3. **Search Errors**
   - Malformed queries
   - Index corruption
   - Memory exhaustion

### Error Handling Strategy

- **Graceful Degradation**: Application continues functioning with reduced capabilities when services are unavailable
- **User Feedback**: Clear error messages with actionable troubleshooting steps
- **Logging**: Comprehensive logging with structured format for debugging
- **Recovery**: Automatic retry mechanisms with exponential backoff

### Exception Hierarchy
```python
class PDFSearchException(Exception):
    """Base exception for PDF search application"""

class ServiceUnavailableError(PDFSearchException):
    """Raised when required services are not available"""

class DocumentProcessingError(PDFSearchException):
    """Raised when PDF processing fails"""

class SearchError(PDFSearchException):
    """Raised when search operations fail"""
```

## Testing Strategy

### Unit Testing
- **Coverage Target**: 90% code coverage for core business logic
- **Framework**: pytest with fixtures for dependency injection
- **Mocking**: Mock external services (Elasticsearch, file system) for isolated testing
- **Test Structure**: Separate test files for each core component

### Integration Testing
- **Scope**: End-to-end workflows including search, indexing, and PDF rendering
- **Environment**: Docker Compose test environment with test data
- **Scenarios**: Multi-document search, concurrent operations, error conditions

### Performance Testing
- **Load Testing**: Search performance with collections of 100, 500, and 1000 documents
- **Memory Testing**: Memory usage monitoring during large file processing
- **UI Responsiveness**: Automated UI tests ensuring sub-2-second response times

### GUI Testing
- **Framework**: pytest-qt for PyQt6 component testing
- **Scope**: User interaction flows, window communication, error dialogs
- **Automation**: Headless testing for CI/CD integration

## Implementation Considerations

### Performance Optimizations

1. **Asynchronous Operations**: All I/O operations use QThread to prevent UI blocking, ensuring UI responsiveness
2. **Caching Strategy**: 
   - Document content cache with LRU eviction (max 50 documents)
   - Search result caching for repeated queries with TTL expiration
   - Elasticsearch query result caching
   - Embedding cache for semantic search performance
3. **Memory Management**: Explicit cleanup of large objects, monitoring usage with 1GB limit and automatic cleanup
4. **Lazy Loading Strategy**: 
   - Document viewer: Load active page ± 10 pages, unload distant pages during scrolling
   - Search results: Load results in batches with pagination
   - Document content: Progressive loading with background threads and visual indicators
   - Automatic memory cleanup when approaching limits
5. **Response Time Targets**: Sub-500ms search response for collections under 1000 documents
6. **Compiled Performance Optimizations**:
   - **Numba JIT**: Vector operations, cosine similarity calculations, embedding batch processing
   - **Cython Extensions**: Text tokenization, large document parsing, fuzzy matching loops
   - **Performance-Critical Modules**: `src/core/performance/` for compiled optimizations

### Service Management and Setup

1. **Docker Integration**: Automatic Docker service startup (Elasticsearch) with health checking as per requirement 6.1
2. **UV Dependency Management**: Docker containers use `uv sync` for fast, reproducible dependency installation from `pyproject.toml`
3. **Service Verification**: Startup verification of all required services with clear status display (requirement 6.3)
4. **Error Handling**: Clear error messages with troubleshooting guidance for service failures (requirement 6.4)
5. **Directory Management**: File browser integration for easy document directory configuration (requirement 6.2)
6. **Auto-Discovery**: Automatic file watching and index updates for directory changes (requirement 2.3)
7. **Configuration Persistence**: Settings persist between application restarts (requirement 6.5)

### Scalability Considerations

1. **Index Partitioning**: Support for multiple Elasticsearch indices for large document collections
2. **Batch Processing**: Bulk indexing operations for initial document processing across multiple formats
3. **Resource Limits**: Configurable limits for concurrent operations and memory usage
4. **Multi-format Support**: Extensible processor architecture for adding new document types

### Security Considerations

1. **Input Validation**: Sanitization of search queries and file paths
2. **File Access**: Restricted file system access within configured directories
3. **Service Security**: Elasticsearch authentication and network isolation via Docker
4. **Error Isolation**: Graceful handling of corrupted or password-protected files

### Docker and Dependency Management

**Docker Compose Configuration** `#[[file:docker-compose.yml]]`:
```yaml
services:
  elasticsearch:
    image: elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - ES_JAVA_OPTS=-Xms512m -Xmx512m
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:9200/_cluster/health || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3

  backend:
    build:
      context: .
      dockerfile: backend/Dockerfile
    depends_on:
      elasticsearch:
        condition: service_healthy
    volumes:
      - ./documents:/app/documents
      - ./config:/app/config
    environment:
      - ELASTICSEARCH_URL=http://elasticsearch:9200
    ports:
      - "8000:8000"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  elasticsearch_data:
```

**Backend Dockerfile Configuration** `#[[file:backend/Dockerfile]]`:
```dockerfile
FROM python:3.11-slim

# Install UV package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies using UV sync (fast, reproducible)
RUN uv sync --frozen --no-dev

# Copy application code
COPY . .

# Set entry point
CMD ["uv", "run", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Tauri Configuration** `#[[file:src-tauri/tauri.conf.json]]`:
```json
{
  "build": {
    "beforeDevCommand": "npm run dev",
    "beforeBuildCommand": "npm run build",
    "devPath": "http://localhost:1420",
    "distDir": "../dist"
  },
  "package": {
    "productName": "Intelligent PDF Search",
    "version": "0.1.0"
  },
  "tauri": {
    "allowlist": {
      "all": false,
      "fs": {
        "all": true,
        "readFile": true,
        "writeFile": true,
        "readDir": true,
        "copyFile": true,
        "createDir": true,
        "removeDir": true,
        "removeFile": true,
        "renameFile": true
      },
      "dialog": {
        "all": true,
        "open": true,
        "save": true
      },
      "window": {
        "all": true,
        "create": true,
        "center": true,
        "requestUserAttention": true,
        "setResizable": true,
        "setTitle": true,
        "maximize": true,
        "unmaximize": true,
        "minimize": true,
        "unminimize": true,
        "show": true,
        "hide": true,
        "close": true,
        "setDecorations": true,
        "setAlwaysOnTop": true,
        "setSize": true,
        "setMinSize": true,
        "setMaxSize": true,
        "setPosition": true,
        "setFullscreen": true,
        "setFocus": true,
        "setIcon": true,
        "setSkipTaskbar": true,
        "setCursorGrab": true,
        "setCursorVisible": true,
        "setCursorIcon": true,
        "setCursorPosition": true,
        "setIgnoreCursorEvents": true,
        "startDragging": true,
        "print": true
      }
    },
    "windows": [
      {
        "fullscreen": false,
        "height": 800,
        "resizable": true,
        "title": "Intelligent PDF Search",
        "width": 1200,
        "minWidth": 800,
        "minHeight": 600
      }
    ]
  }
}
```

**Backend UV Configuration** `#[[file:backend/pyproject.toml]]`:
```toml
[project]
name = "intelligent-pdf-search-backend"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "pdfplumber>=0.10.0",
    "elasticsearch>=8.11.0",
    "sentence-transformers>=2.2.2",
    "rapidfuzz>=3.5.0",
    "numba>=0.58.0",
    "joblib>=1.3.0",
    "torch>=2.1.0",
    "python-multipart>=0.0.6",
    "websockets>=12.0",
    "aiofiles>=23.2.1"
]

[tool.uv]
dev-dependencies = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "httpx>=0.25.0",
    "black>=23.0.0",
    "mypy>=1.7.0"
]
```

**Frontend Package Configuration** `#[[file:package.json]]`:
```json
{
  "name": "intelligent-pdf-search",
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "tauri": "tauri",
    "tauri:dev": "tauri dev",
    "tauri:build": "tauri build",
    "test": "vitest"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.8.0",
    "@tanstack/react-query": "^5.0.0",
    "axios": "^1.6.0",
    "@tauri-apps/api": "^1.5.0",
    "tailwindcss": "^3.3.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@vitejs/plugin-react": "^4.0.0",
    "@tauri-apps/cli": "^1.5.0",
    "typescript": "^5.0.0",
    "vite": "^5.0.0",
    "vitest": "^1.0.0",
    "@testing-library/react": "^14.0.0"
  }
}
```

### Configuration Management

- **Storage**: JSON configuration files in `config/settings.json` with comprehensive schema validation
- **Validation**: Comprehensive schema validation on application startup (requirement 6.3)
- **Hot Reload**: Configuration changes applied without restart where possible
- **Persistence**: Settings persistence between application restarts (requirement 6.5)
- **Defaults**: Sensible default values for all configuration options
- **Service Integration**: Automatic Docker service configuration and management (requirement 6.1)
- **UV Integration**: Use `uv sync` for fast, reproducible dependency management in all environments
- **Code Standards**: Follow snake_case naming conventions and mandatory type hints