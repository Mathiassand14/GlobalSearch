---
inclusion: fileMatch
fileMatchPattern: ['requirements.txt', 'pyproject.toml', 'docker-compose.yml', 'Dockerfile']
---

# Technology Stack & Library Requirements

## Required Dependencies
```python
# Core dependencies (requirements.txt)
PyQt6>=6.6.0
pdfplumber>=0.10.0  # Never use PyMuPDF
Pillow>=10.0.0
asyncio-mqtt>=0.13.0

# Search & AI
elasticsearch>=8.11.0
sentence-transformers>=2.2.2  # Use all-MiniLM-L6-v2 model
rapidfuzz>=3.5.0  # Never use fuzzywuzzy

# Data & Infrastructure
psycopg2-binary>=2.9.0
redis>=5.0.0

# Development
black>=23.0.0
ruff>=0.1.0
pytest>=7.4.0
```

## Containerized Services (docker-compose.yml)
```yaml
services:
  elasticsearch:
    image: elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    ports:
      - "9200:9200"
  
  postgresql:
    image: postgres:16
    environment:
      POSTGRES_DB: pdf_search
      POSTGRES_USER: app
      POSTGRES_PASSWORD: dev_password
    ports:
      - "5432:5432"
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

## Library Usage Rules
- **PDF Processing**: Always use `pdfplumber.open()` for text extraction
- **GUI Threading**: Use `QThread` for I/O operations, never block main thread
- **Search**: Combine Elasticsearch (full-text) + sentence-transformers (semantic)
- **Fuzzy Matching**: Use `rapidfuzz.fuzz.ratio()` for string similarity
- **Async Operations**: Use `asyncio` in core modules, `QThread` in GUI
- **Memory Management**: Call `.close()` on PDF objects, use context managers

## Development Workflow
```bash
# Setup
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt

# Services
docker-compose up -d

# Quality checks (required before commits)
uv run black src/ tests/
uv run ruff check src/ tests/
uv run pytest tests/ -v
```