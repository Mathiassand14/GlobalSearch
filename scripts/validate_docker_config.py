#!/usr/bin/env python3
"""
Docker Compose Configuration Validation Script

Checks for common Docker Compose configuration issues and best practices.
"""

import json
import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional

try:
    import yaml
except ImportError:
    print("Warning: PyYAML not installed. Install with: pip install PyYAML")
    yaml = None


class DockerConfigValidator:
    """Validates Docker Compose configuration for common issues."""
    
    def __init__(self, compose_file: Path = Path("docker-compose.yml")):
        self.compose_file = compose_file
        self.issues: List[str] = []
        self.warnings: List[str] = []
        
    def validate(self) -> bool:
        """Run all validation checks. Returns True if no critical issues found."""
        print(f"Validating Docker Compose configuration: {self.compose_file}")
        
        if not self.compose_file.exists():
            self.issues.append(f"Docker Compose file not found: {self.compose_file}")
            return False
            
        if yaml is None:
            self.warnings.append("PyYAML not available - skipping YAML parsing checks")
            config = {}
        else:
            try:
                with open(self.compose_file, 'r') as f:
                    config = yaml.safe_load(f)
            except yaml.YAMLError as e:
                self.issues.append(f"Invalid YAML syntax: {e}")
                return False
            
        self._check_version_attribute(config)
        self._check_restart_policies(config)
        self._check_health_checks(config)
        self._check_volume_mounts(config)
        self._check_environment_variables(config)
        self._check_resource_limits(config)
        self._check_docker_compose_syntax()
        self._check_orphaned_containers()
        
        return len(self.issues) == 0
        
    def _check_version_attribute(self, config: Dict[str, Any]) -> None:
        """Check for obsolete version attribute."""
        if 'version' in config:
            self.warnings.append(
                "Found 'version' attribute in docker-compose.yml. "
                "This is obsolete in Docker Compose v2+ and should be removed."
            )
            
    def _check_restart_policies(self, config: Dict[str, Any]) -> None:
        """Check that services have appropriate restart policies."""
        services = config.get('services', {})
        for service_name, service_config in services.items():
            if 'restart' not in service_config:
                self.warnings.append(
                    f"Service '{service_name}' has no restart policy. "
                    "Consider adding 'restart: unless-stopped' for production services."
                )
                
    def _check_health_checks(self, config: Dict[str, Any]) -> None:
        """Check that critical services have health checks."""
        services = config.get('services', {})
        critical_services = ['elasticsearch', 'database', 'redis']
        
        for service_name, service_config in services.items():
            if any(critical in service_name.lower() for critical in critical_services):
                if 'healthcheck' not in service_config:
                    self.warnings.append(
                        f"Critical service '{service_name}' has no health check. "
                        "Consider adding health check for better dependency management."
                    )
                    
    def _check_volume_mounts(self, config: Dict[str, Any]) -> None:
        """Check for potential volume mounting issues."""
        services = config.get('services', {})
        
        for service_name, service_config in services.items():
            volumes = service_config.get('volumes', [])
            for volume in volumes:
                if isinstance(volume, str):
                    # Check for root directory mounts that might cause hardlink issues
                    if volume.startswith('./:/') or volume.startswith('.:/'):
                        self.warnings.append(
                            f"Service '{service_name}' mounts entire project root. "
                            "This can cause hardlink issues. Consider mounting specific directories."
                        )
                        
    def _check_environment_variables(self, config: Dict[str, Any]) -> None:
        """Check for required environment variables."""
        services = config.get('services', {})
        
        for service_name, service_config in services.items():
            env_vars = service_config.get('environment', [])
            if isinstance(env_vars, list):
                env_dict = {var.split('=')[0]: var.split('=', 1)[1] if '=' in var else None 
                           for var in env_vars}
            else:
                env_dict = env_vars
                
            # Check for UV_LINK_MODE in services that use UV
            if 'uv' in str(service_config.get('command', '')).lower():
                if 'UV_LINK_MODE' not in env_dict:
                    self.warnings.append(
                        f"Service '{service_name}' uses UV but doesn't set UV_LINK_MODE=copy. "
                        "This may cause hardlink warnings in containers."
                    )
            
            # Check for GUI-related environment variables
            if service_name == 'app':
                if 'DISPLAY' in env_dict:
                    volumes = service_config.get('volumes', [])
                    has_x11_volume = any('/tmp/.X11-unix' in str(vol) for vol in volumes)
                    if not has_x11_volume:
                        self.warnings.append(
                            f"Service '{service_name}' has DISPLAY but no X11 volume mount. "
                            "Add '/tmp/.X11-unix:/tmp/.X11-unix:rw' for GUI support."
                        )
                    
    def _check_resource_limits(self, config: Dict[str, Any]) -> None:
        """Check for resource limits on services."""
        services = config.get('services', {})
        
        for service_name, service_config in services.items():
            deploy = service_config.get('deploy', {})
            resources = deploy.get('resources', {})
            
            if not resources.get('limits'):
                self.warnings.append(
                    f"Service '{service_name}' has no resource limits. "
                    "Consider adding memory/CPU limits for production deployments."
                )
                
    def _check_docker_compose_syntax(self) -> None:
        """Validate Docker Compose syntax using docker-compose config."""
        try:
            result = subprocess.run(
                ['docker', 'compose', 'config', '--quiet'],
                cwd=self.compose_file.parent,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                self.issues.append(f"Docker Compose syntax validation failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            self.warnings.append("Docker Compose syntax validation timed out")
        except FileNotFoundError:
            self.warnings.append("Docker Compose not found - cannot validate syntax")
        except Exception as e:
            self.warnings.append(f"Could not validate Docker Compose syntax: {e}")
            
    def _check_orphaned_containers(self) -> None:
        """Check for orphaned containers."""
        try:
            result = subprocess.run(
                ['docker', 'compose', 'ps', '--all', '--format', 'json'],
                cwd=self.compose_file.parent,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0 and result.stdout.strip():
                containers = []
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        try:
                            containers.append(json.loads(line))
                        except json.JSONDecodeError:
                            pass
                            
                orphaned = [c for c in containers if c.get('State') == 'exited']
                if orphaned:
                    self.warnings.append(
                        f"Found {len(orphaned)} orphaned containers. "
                        "Run 'docker compose down --remove-orphans' to clean up."
                    )
        except Exception as e:
            self.warnings.append(f"Could not check for orphaned containers: {e}")
            
    def print_results(self) -> None:
        """Print validation results."""
        if self.issues:
            print("\n❌ CRITICAL ISSUES:")
            for issue in self.issues:
                print(f"  • {issue}")
                
        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"  • {warning}")
                
        if not self.issues and not self.warnings:
            print("\n✅ No issues found!")
        elif not self.issues:
            print(f"\n✅ No critical issues found ({len(self.warnings)} warnings)")
        else:
            print(f"\n❌ Found {len(self.issues)} critical issues and {len(self.warnings)} warnings")


def main():
    """Main entry point."""
    compose_file = Path("docker-compose.yml")
    if len(sys.argv) > 1:
        compose_file = Path(sys.argv[1])
        
    validator = DockerConfigValidator(compose_file)
    is_valid = validator.validate()
    validator.print_results()
    
    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()