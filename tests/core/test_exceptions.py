import pytest

from src.core.exceptions.exceptions import (
    PDFSearchException,
    ServiceUnavailableError,
    DocumentProcessingError,
    SearchError,
)


def test_exception_hierarchy():
    assert issubclass(ServiceUnavailableError, PDFSearchException)
    assert issubclass(DocumentProcessingError, PDFSearchException)
    assert issubclass(SearchError, PDFSearchException)

    with pytest.raises(PDFSearchException):
        raise DocumentProcessingError("failed")

