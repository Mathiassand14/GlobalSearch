from __future__ import annotations

from dataclasses import dataclass


class PDFSearchException(Exception):
    """Base exception for the Intelligent PDF Search application."""


class ServiceUnavailableError(PDFSearchException):
    """Raised when required services (e.g., Elasticsearch) are unavailable."""


class DocumentProcessingError(PDFSearchException):
    """Raised when document processing fails (corrupt/password-protected)."""


class SearchError(PDFSearchException):
    """Raised for search and query processing failures."""

