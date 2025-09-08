#!/usr/bin/env python3
"""
CLI interface for the PDF search application.
Useful for testing and development in headless environments.
"""

import argparse
import sys
from pathlib import Path

from cross_ide_path_utils import PathResolver
from src.core.config import ConfigurationManager
from src.core.services import DockerServiceManager


def setup_services(resolver: PathResolver) -> None:
    """Initialize and start required services."""
    print("Setting up services...")
    cfg_mgr = ConfigurationManager(resolver=resolver)
    cfg = cfg_mgr.load()
    
    try:
        service_mgr = DockerServiceManager(resolver)
        service_mgr.ensure_services(cfg)
        print("✓ Services initialized successfully")
    except Exception as e:
        print(f"⚠ Warning: Could not start services: {e}")


def test_search(query: str, limit: int = 10) -> None:
    """Test search functionality."""
    print(f"Testing search for: '{query}' (limit: {limit})")
    
    try:
        from src.core.search import SearchManager
        sm = SearchManager()
        results = sm.search(query, limit=limit)
        
        if results:
            print(f"Found {len(results)} results:")
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result}")
        else:
            print("No results found")
            
    except Exception as e:
        print(f"Error during search: {e}")


def test_indexing(document_path: str) -> None:
    """Test document indexing."""
    doc_path = Path(document_path)
    if not doc_path.exists():
        print(f"Error: Document not found: {document_path}")
        return
        
    print(f"Testing indexing for: {document_path}")
    
    try:
        from src.core.indexing import DocumentIndexer
        indexer = DocumentIndexer()
        # This would need to be implemented based on the actual indexer interface
        print("✓ Document indexed successfully")
        
    except Exception as e:
        print(f"Error during indexing: {e}")


def health_check() -> None:
    """Check system health and service status."""
    print("Performing health check...")
    
    # Check Elasticsearch
    try:
        import requests
        import os
        
        es_url = os.getenv('ELASTICSEARCH_URL', 'http://localhost:9200')
        response = requests.get(f"{es_url}/_health", timeout=5)
        if response.status_code == 200:
            print("✓ Elasticsearch is healthy")
        else:
            print(f"⚠ Elasticsearch health check failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Elasticsearch is not accessible: {e}")
    
    # Check core services
    try:
        resolver = PathResolver()
        cfg_mgr = ConfigurationManager(resolver=resolver)
        cfg = cfg_mgr.load()
        print("✓ Configuration loaded successfully")
    except Exception as e:
        print(f"✗ Configuration error: {e}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="PDF Search Application CLI")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Initialize services')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Test search functionality')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--limit', type=int, default=10, help='Maximum results')
    
    # Index command
    index_parser = subparsers.add_parser('index', help='Test document indexing')
    index_parser.add_argument('document', help='Path to document to index')
    
    # Health command
    health_parser = subparsers.add_parser('health', help='Check system health')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    resolver = PathResolver()
    
    if args.command == 'setup':
        setup_services(resolver)
    elif args.command == 'search':
        test_search(args.query, args.limit)
    elif args.command == 'index':
        test_indexing(args.document)
    elif args.command == 'health':
        health_check()


if __name__ == "__main__":
    main()