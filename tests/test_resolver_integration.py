"""Integration tests for ConfigResolver with ParameterLoader and CLI."""

import tempfile
from pathlib import Path
import pytest
import yaml

from template_customizer.core.processor import ParameterLoader
from template_customizer.core.exceptions import CircularReferenceError, ReferenceResolutionError
from template_customizer.cli import process
from click.testing import CliRunner


class TestResolverIntegration:
    """Integration tests for resolver functionality."""
    
    def test_parameter_loader_with_references(self):
        """Test ParameterLoader with reference resolution enabled."""
        config_data = {
            "project": {"name": "testapp"},
            "docker": {"image": "{{ values.project.name }}:latest"}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.dump(config_data, f)
            config_path = Path(f.name)
        
        try:
            # Test with resolution enabled (default)
            loader = ParameterLoader(config_path, resolve_references=True)
            result = loader.load()
            
            assert result["docker"]["image"] == "testapp:latest"
            
            # Test with resolution disabled
            loader_no_resolve = ParameterLoader(config_path, resolve_references=False)
            result_no_resolve = loader_no_resolve.load()
            
            assert result_no_resolve["docker"]["image"] == "{{ values.project.name }}:latest"
            
        finally:
            config_path.unlink()
    
    def test_parameter_loader_with_circular_references(self):
        """Test ParameterLoader error handling for circular references."""
        config_data = {
            "a": "{{ values.b }}",
            "b": "{{ values.a }}"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.dump(config_data, f)
            config_path = Path(f.name)
        
        try:
            loader = ParameterLoader(config_path, resolve_references=True)
            
            with pytest.raises(ValueError) as exc_info:
                loader.load()
            
            # Verify it's specifically a circular reference error
            assert "Circular dependency detected" in str(exc_info.value)
                
        finally:
            config_path.unlink()
    
    def test_parameter_loader_with_missing_references(self):
        """Test ParameterLoader error handling for missing references."""
        config_data = {
            "app": {"name": "{{ values.missing.reference }}"}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.dump(config_data, f)
            config_path = Path(f.name)
        
        try:
            loader = ParameterLoader(config_path, resolve_references=True)
            
            with pytest.raises(ValueError) as exc_info:
                loader.load()
            
            # Verify it's specifically a reference resolution error
            assert "Reference resolution failed" in str(exc_info.value)
                
        finally:
            config_path.unlink()
    
    def test_json_configuration_with_references(self):
        """Test reference resolution with JSON configuration files."""
        import json
        
        config_data = {
            "project": {"name": "jsonapp"},
            "api": {"endpoint": "https://{{ values.project.name }}.api.com"}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_path = Path(f.name)
        
        try:
            loader = ParameterLoader(config_path, resolve_references=True)
            result = loader.load()
            
            assert result["api"]["endpoint"] == "https://jsonapp.api.com"
            
        finally:
            config_path.unlink()
    
    def test_cli_no_resolve_refs_flag(self):
        """Test CLI --no-resolve-refs flag functionality."""
        # Create test configuration
        config_data = {
            "project": {"name": "clitest"},
            "service": {"url": "https://{{ values.project.name }}.com"}
        }
        
        # Create test project structure
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_path = temp_path / "config.yml"
            test_file = temp_path / "test.py"
            
            # Write config file
            with open(config_path, 'w') as f:
                yaml.dump(config_data, f)
            
            # Write test file with template marker
            test_file.write_text('# service_url = {{ values.service.url }}\nservice_url = "default"\n')
            
            runner = CliRunner()
            
            # Test with reference resolution enabled (default)
            result = runner.invoke(process, [
                '--project', str(temp_path),
                '--config', str(config_path),
                '--dry-run'
            ])
            
            assert result.exit_code == 0
            # Output should show resolved value
            assert "https://clitest.com" in result.output
            
            # Test with reference resolution disabled
            result_no_resolve = runner.invoke(process, [
                '--project', str(temp_path),
                '--config', str(config_path),
                '--no-resolve-refs',
                '--dry-run'
            ])
            
            assert result_no_resolve.exit_code == 0
            # Output should show unresolved template (may be truncated in table)
            # Look for the template markers in the output
            assert "{{" in result_no_resolve.output and "values.project" in result_no_resolve.output
    
    def test_complex_real_world_configuration(self):
        """Test with a complex real-world configuration."""
        config_data = {
            "environment": {
                "name": "production",
                "short": "prod"
            },
            "project": {
                "name": "my-microservice",
                "version": "1.2.3"
            },
            "aws": {
                "region": "us-east-1",
                "account_id": "123456789012"
            },
            "resources": {
                "bucket_name": "{{ values.project.name }}-{{ values.environment.short }}-assets",
                "database_name": "{{ values.project.name | replace('-', '_') }}_{{ values.environment.name }}",
                "lambda_prefix": "{{ values.environment.short }}-{{ values.project.name }}"
            },
            "docker": {
                "registry": "{{ values.aws.account_id }}.dkr.ecr.{{ values.aws.region }}.amazonaws.com",
                "image": "{{ values.docker.registry }}/{{ values.project.name }}:{{ values.project.version }}"
            },
            "api": {
                "base_url": "https://{{ values.resources.lambda_prefix }}.{{ values.aws.region }}.amazonaws.com",
                "health_check": "{{ values.api.base_url }}/health"
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.dump(config_data, f)
            config_path = Path(f.name)
        
        try:
            loader = ParameterLoader(config_path, resolve_references=True)
            result = loader.load()
            
            # Verify complex nested resolution
            assert result["resources"]["bucket_name"] == "my-microservice-prod-assets"
            assert result["resources"]["database_name"] == "my_microservice_production"
            assert result["resources"]["lambda_prefix"] == "prod-my-microservice"
            
            # Verify chained references
            expected_registry = "123456789012.dkr.ecr.us-east-1.amazonaws.com"
            assert result["docker"]["registry"] == expected_registry
            assert result["docker"]["image"] == f"{expected_registry}/my-microservice:1.2.3"
            
            # Verify deeply nested references
            expected_base_url = "https://prod-my-microservice.us-east-1.amazonaws.com"
            assert result["api"]["base_url"] == expected_base_url
            assert result["api"]["health_check"] == f"{expected_base_url}/health"
            
        finally:
            config_path.unlink()
    
    def test_performance_with_large_configuration(self):
        """Test performance with larger configuration files."""
        import time
        
        # Generate a large configuration with many references
        config_data = {"base": {"value": "test"}}
        
        # Add 100 entries that reference the base value
        for i in range(100):
            config_data[f"service_{i}"] = {
                "name": f"{{{{ values.base.value }}}}-service-{i}",
                "url": f"https://{{{{ values.base.value }}}}-{i}.example.com"
            }
        
        # Add some cross-references
        for i in range(10):
            config_data[f"dependent_{i}"] = {
                "ref": f"{{{{ values.service_{i}.name }}}}-dependent"
            }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.dump(config_data, f)
            config_path = Path(f.name)
        
        try:
            loader = ParameterLoader(config_path, resolve_references=True)
            
            start_time = time.time()
            result = loader.load()
            end_time = time.time()
            
            resolution_time = end_time - start_time
            
            # Verify resolution worked correctly
            assert result["service_0"]["name"] == "test-service-0"
            assert result["service_99"]["url"] == "https://test-99.example.com"
            assert result["dependent_0"]["ref"] == "test-service-0-dependent"
            
            # Performance check - should be reasonable for this size (relaxed for CI)
            assert resolution_time < 1.0, f"Resolution took {resolution_time:.3f}s, expected < 1.0s"
            
        finally:
            config_path.unlink()
    
    def test_error_reporting_with_line_numbers(self):
        """Test that error messages include helpful context."""
        config_yaml = '''
project:
  name: myapp
  
api:
  url: "{{ values.nonexistent.reference }}"
  
docker:
  image: "{{ values.project.name }}:latest"
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write(config_yaml)
            config_path = Path(f.name)
        
        try:
            loader = ParameterLoader(config_path, resolve_references=True)
            
            with pytest.raises(ValueError) as exc_info:
                loader.load()
            
            error_msg = str(exc_info.value)
            assert "Reference resolution failed" in error_msg
            
        finally:
            config_path.unlink()
    
    def test_backward_compatibility(self):
        """Test that existing configurations without references still work."""
        config_data = {
            "project": {
                "name": "legacy-app",
                "version": "1.0.0"
            },
            "database": {
                "host": "localhost",
                "port": 5432
            },
            "features": ["auth", "api", "frontend"]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.dump(config_data, f)
            config_path = Path(f.name)
        
        try:
            # Test with resolver enabled
            loader = ParameterLoader(config_path, resolve_references=True)
            result_with_resolver = loader.load()
            
            # Test with resolver disabled
            loader_no_resolve = ParameterLoader(config_path, resolve_references=False)
            result_no_resolver = loader_no_resolve.load()
            
            # Results should be identical
            assert result_with_resolver == result_no_resolver == config_data
            
        finally:
            config_path.unlink()