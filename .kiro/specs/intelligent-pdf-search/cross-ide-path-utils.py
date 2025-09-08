"""
Cross-IDE Path Utilities for Intelligent PDF Search Application

This module provides utilities for resolving file paths that work consistently
across different IDEs (VSCode, PyCharm, command line) and operating systems.

Usage:
    from cross_ide_path_utils import PathResolver
    
    resolver = PathResolver()
    config_path = resolver.get_config_path()
    document_path = resolver.resolve_document_path("documents/file.pdf")
"""

import os
import sys
from pathlib import Path
from typing import Optional, Union


class PathResolver:
    """
    Resolves file paths consistently across different IDEs and execution environments.
    
    Handles common issues:
    - VSCode vs PyCharm working directory differences
    - Relative vs absolute path resolution
    - Cross-platform path compatibility
    - Project root detection
    """
    
    def __init__(self):
        self._project_root: Optional[Path] = None
        self._detect_project_root()
    
    def _detect_project_root(self) -> None:
        """
        Detect the project root directory by looking for common project markers.
        
        Searches for:
        1. pyproject.toml (UV/Poetry projects)
        2. requirements.txt (pip projects)
        3. .git directory (Git repositories)
        4. src/ directory (common Python project structure)
        5. .kiro/ directory (Kiro workspace)
        """
        current_path = Path.cwd()
        
        # Common project root indicators
        root_markers = [
            "pyproject.toml",
            "requirements.txt", 
            ".git",
            "src",
            ".kiro",
            "docker-compose.yml"
        ]
        
        # Start from current directory and walk up
        for path in [current_path] + list(current_path.parents):
            for marker in root_markers:
                if (path / marker).exists():
                    self._project_root = path
                    return
        
        # Fallback: use current working directory
        self._project_root = current_path
    
    @property
    def project_root(self) -> Path:
        """Get the detected project root directory."""
        return self._project_root
    
    def resolve_path(self, relative_path: Union[str, Path]) -> Path:
        """
        Resolve a relative path from the project root.
        
        Args:
            relative_path: Path relative to project root
            
        Returns:
            Absolute path resolved from project root
            
        Example:
            resolver.resolve_path("src/main.py") -> /project/src/main.py
            resolver.resolve_path("config/settings.json") -> /project/config/settings.json
        """
        relative_path = Path(relative_path)
        
        # If already absolute, return as-is
        if relative_path.is_absolute():
            return relative_path
        
        # Resolve from project root
        return self.project_root / relative_path
    
    def get_config_path(self, config_file: str = "settings.json") -> Path:
        """
        Get path to configuration file.
        
        Args:
            config_file: Name of config file (default: settings.json)
            
        Returns:
            Path to config file in config/ directory
        """
        return self.resolve_path(f"config/{config_file}")
    
    def get_src_path(self, module_path: str = "") -> Path:
        """
        Get path to source code directory or specific module.
        
        Args:
            module_path: Optional path within src/ directory
            
        Returns:
            Path to src/ directory or specific module
            
        Example:
            get_src_path() -> /project/src/
            get_src_path("core/search") -> /project/src/core/search/
        """
        if module_path:
            return self.resolve_path(f"src/{module_path}")
        return self.resolve_path("src")
    
    def get_document_path(self, document_file: str = "") -> Path:
        """
        Get path to documents directory or specific document.
        
        Args:
            document_file: Optional document filename
            
        Returns:
            Path to documents directory or specific document
        """
        if document_file:
            return self.resolve_path(f"documents/{document_file}")
        return self.resolve_path("documents")
    
    def get_logs_path(self, log_file: str = "app.log") -> Path:
        """
        Get path to logs directory or specific log file.
        
        Args:
            log_file: Name of log file (default: app.log)
            
        Returns:
            Path to log file in logs/ directory
        """
        logs_dir = self.resolve_path("logs")
        logs_dir.mkdir(exist_ok=True)  # Ensure logs directory exists
        return logs_dir / log_file
    
    def get_cache_path(self, cache_file: str = "") -> Path:
        """
        Get path to cache directory or specific cache file.
        
        Args:
            cache_file: Optional cache filename
            
        Returns:
            Path to cache directory or specific cache file
        """
        cache_dir = self.resolve_path("cache")
        cache_dir.mkdir(exist_ok=True)  # Ensure cache directory exists
        
        if cache_file:
            return cache_dir / cache_file
        return cache_dir
    
    def ensure_directory_exists(self, directory_path: Union[str, Path]) -> Path:
        """
        Ensure a directory exists, creating it if necessary.
        
        Args:
            directory_path: Path to directory (relative to project root)
            
        Returns:
            Absolute path to the directory
        """
        full_path = self.resolve_path(directory_path)
        full_path.mkdir(parents=True, exist_ok=True)
        return full_path
    
    def get_relative_to_project(self, absolute_path: Union[str, Path]) -> Path:
        """
        Get path relative to project root from absolute path.
        
        Args:
            absolute_path: Absolute file path
            
        Returns:
            Path relative to project root
        """
        absolute_path = Path(absolute_path)
        try:
            return absolute_path.relative_to(self.project_root)
        except ValueError:
            # Path is not under project root, return as-is
            return absolute_path
    
    def is_under_project_root(self, path: Union[str, Path]) -> bool:
        """
        Check if a path is under the project root directory.
        
        Args:
            path: Path to check
            
        Returns:
            True if path is under project root, False otherwise
        """
        path = Path(path).resolve()
        try:
            path.relative_to(self.project_root.resolve())
            return True
        except ValueError:
            return False


# Global instance for easy access
path_resolver = PathResolver()


def get_project_root() -> Path:
    """Get the project root directory."""
    return path_resolver.project_root


def resolve_path(relative_path: Union[str, Path]) -> Path:
    """Resolve a path relative to project root."""
    return path_resolver.resolve_path(relative_path)


def get_config_path(config_file: str = "settings.json") -> Path:
    """Get path to configuration file."""
    return path_resolver.get_config_path(config_file)


def get_src_path(module_path: str = "") -> Path:
    """Get path to source directory or module."""
    return path_resolver.get_src_path(module_path)


def get_document_path(document_file: str = "") -> Path:
    """Get path to documents directory or file."""
    return path_resolver.get_document_path(document_file)


def get_logs_path(log_file: str = "app.log") -> Path:
    """Get path to logs directory or file."""
    return path_resolver.get_logs_path(log_file)


def get_cache_path(cache_file: str = "") -> Path:
    """Get path to cache directory or file."""
    return path_resolver.get_cache_path(cache_file)


# IDE-specific debugging utilities
def debug_path_info():
    """
    Print debugging information about path resolution.
    Useful for troubleshooting IDE-specific path issues.
    """
    print("=== Path Resolution Debug Info ===")
    print(f"Current working directory: {Path.cwd()}")
    print(f"Script location: {Path(__file__).parent if '__file__' in globals() else 'Unknown'}")
    print(f"Python executable: {sys.executable}")
    print(f"Detected project root: {get_project_root()}")
    print(f"Config path: {get_config_path()}")
    print(f"Source path: {get_src_path()}")
    print(f"Documents path: {get_document_path()}")
    print("================================")


if __name__ == "__main__":
    # Run debug info when executed directly
    debug_path_info()