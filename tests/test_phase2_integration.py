"""Phase 2 integration tests for error handling and CLI improvements."""

import tempfile
from pathlib import Path
import pytest
import yaml
import io
import sys
from contextlib import redirect_stdout, redirect_stderr

from template_customizer.core.processor import ParameterLoader
from template_customizer.core.exceptions import (
    CircularReferenceError,
    ReferenceResolutionError,
    MaxRecursionError,
    TemplateSyntaxError
)
from template_customizer.cli import process
from click.testing import CliRunner


class TestErrorHandlingIntegration:
    """Test error handling improvements in Phase 2."""
    
    def test_circular_reference_error_reporting(self):
        """Test circular reference error reporting with helpful messages."""
        config_data = {
            "a": "{{ values.b }}",
            "b": "{{ values.c }}",
            "c": "{{ values.a }}"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.dump(config_data, f)
            config_path = Path(f.name)
        
        try:
            loader = ParameterLoader(config_path, resolve_references=True)
            
            with pytest.raises(ValueError) as exc_info:
                loader.load()
            
            error_msg = str(exc_info.value)
            assert "Circular dependency detected" in error_msg
            assert str(config_path) in error_msg
            assert "check your configuration for references that form a loop" in error_msg
            
        finally:
            config_path.unlink()
    
    def test_missing_reference_error_reporting(self):
        """Test missing reference error reporting with helpful messages."""
        config_data = {
            "project": {"name": "test"},
            "api": {"url": "{{ values.missing.reference }}"}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.dump(config_data, f)
            config_path = Path(f.name)
        
        try:
            loader = ParameterLoader(config_path, resolve_references=True)
            
            with pytest.raises(ValueError) as exc_info:
                loader.load()
            
            error_msg = str(exc_info.value)
            assert "Reference resolution failed" in error_msg
            assert str(config_path) in error_msg
            assert "ensure all referenced values exist" in error_msg
            
        finally:
            config_path.unlink()
    
    def test_template_syntax_error_reporting(self):
        """Test template syntax error reporting with helpful messages."""
        config_data = {
            "project": {"name": "test"},
            "api": {"url": "{{ values.project.name | invalid_filter }}"}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.dump(config_data, f)
            config_path = Path(f.name)
        
        try:
            loader = ParameterLoader(config_path, resolve_references=True)
            
            with pytest.raises(ValueError) as exc_info:
                loader.load()
            
            error_msg = str(exc_info.value)
            assert "Template syntax error" in error_msg
            assert str(config_path) in error_msg
            assert "check your Jinja2 template syntax" in error_msg
            
        finally:
            config_path.unlink()
    
    def test_cli_error_reporting(self):
        """Test CLI error reporting for resolver issues."""
        config_data = {
            "a": "{{ values.b }}",
            "b": "{{ values.a }}"  # Circular reference
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_path = temp_path / "config.yml"
            test_file = temp_path / "test.py"
            
            # Write config file with circular reference
            with open(config_path, 'w') as f:
                yaml.dump(config_data, f)
            
            # Write test file with template marker
            test_file.write_text('# value = {{ values.a }}\nvalue = "default"\n')
            
            runner = CliRunner()
            result = runner.invoke(process, [
                '--project', str(temp_path),
                '--config', str(config_path),
                '--dry-run'
            ])
            
            assert result.exit_code == 1
            assert "Circular dependency detected" in result.output
    
    def test_cli_with_missing_references(self):
        """Test CLI handling of missing references."""
        config_data = {
            "project": {"name": "test"},
            "missing_ref": "{{ values.nonexistent.value }}"
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_path = temp_path / "config.yml"
            test_file = temp_path / "test.py"
            
            # Write config file with missing reference
            with open(config_path, 'w') as f:
                yaml.dump(config_data, f)
            
            # Write test file with template marker
            test_file.write_text('# value = {{ values.missing_ref }}\nvalue = "default"\n')
            
            runner = CliRunner()
            result = runner.invoke(process, [
                '--project', str(temp_path),
                '--config', str(config_path),
                '--dry-run'
            ])
            
            assert result.exit_code == 1
            assert "Reference resolution failed" in result.output


class TestVerboseModeIntegration:
    """Test verbose mode functionality in Phase 2."""
    
    def test_verbose_resolution_output(self):
        """Test verbose output during resolution."""
        config_data = {
            "base": {"value": "test"},
            "derived": "{{ values.base.value }}-extended"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.dump(config_data, f)
            config_path = Path(f.name)
        
        try:
            # Capture stdout
            captured_output = io.StringIO()
            
            with redirect_stdout(captured_output):
                loader = ParameterLoader(config_path, resolve_references=True, verbose=True)
                result = loader.load()
            
            output = captured_output.getvalue()
            
            # Check that verbose output was generated
            assert "Resolving self-references" in output
            assert "Successfully resolved" in output
            assert "Resolution completed" in output
            
            # Check that resolution worked
            assert result["derived"] == "test-extended"
            
        finally:
            config_path.unlink()
    
    def test_verbose_dependency_graph_output(self):
        """Test verbose output shows dependency graph details."""
        config_data = {
            "a": "base",
            "b": "{{ values.a }}-b",
            "c": "{{ values.b }}-c"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.dump(config_data, f)
            config_path = Path(f.name)
        
        try:
            captured_output = io.StringIO()
            
            with redirect_stdout(captured_output):
                loader = ParameterLoader(config_path, resolve_references=True, verbose=True)
                result = loader.load()
            
            output = captured_output.getvalue()
            
            # Check dependency graph output
            assert "Built dependency graph" in output
            assert "depends on" in output
            assert "Resolution order" in output
            
            # Verify resolution worked
            assert result["c"] == "base-b-c"
            
        finally:
            config_path.unlink()
    
    def test_cli_verbose_mode(self):
        """Test CLI verbose mode functionality."""
        config_data = {
            "project": {"name": "testapp"},
            "service": {"url": "https://{{ values.project.name }}.com"}
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_path = temp_path / "config.yml"
            test_file = temp_path / "test.py"
            
            # Write config file
            with open(config_path, 'w') as f:
                yaml.dump(config_data, f)
            
            # Write test file with template marker
            test_file.write_text('# url = {{ values.service.url }}\nurl = "default"\n')
            
            runner = CliRunner()
            result = runner.invoke(process, [
                '--project', str(temp_path),
                '--config', str(config_path),
                '--verbose',
                '--dry-run'
            ])
            
            assert result.exit_code == 0
            # Should show resolution details in verbose mode
            assert "Resolving self-references" in result.output or "Loading configuration" in result.output
    
    def test_no_verbose_mode_quiet_output(self):
        """Test that non-verbose mode doesn't show resolution details."""
        config_data = {
            "project": {"name": "testapp"},
            "service": {"url": "https://{{ values.project.name }}.com"}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.dump(config_data, f)
            config_path = Path(f.name)
        
        try:
            captured_output = io.StringIO()
            
            with redirect_stdout(captured_output):
                loader = ParameterLoader(config_path, resolve_references=True, verbose=False)
                result = loader.load()
            
            output = captured_output.getvalue()
            
            # Should not show verbose resolution details
            assert "Built dependency graph" not in output
            assert "Resolution order" not in output
            
            # But resolution should still work
            assert result["service"]["url"] == "https://testapp.com"
            
        finally:
            config_path.unlink()


class TestAdvancedErrorCases:
    """Test advanced error cases and edge conditions."""
    
    def test_nested_template_syntax_errors(self):
        """Test handling of nested template syntax errors."""
        config_data = {
            "base": {"value": "test"},
            "complex": {
                "nested": "{{ values.base.value | filter_that_does_not_exist }}"
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.dump(config_data, f)
            config_path = Path(f.name)
        
        try:
            loader = ParameterLoader(config_path, resolve_references=True)
            
            with pytest.raises(ValueError) as exc_info:
                loader.load()
            
            error_msg = str(exc_info.value)
            assert "Template syntax error" in error_msg
            
        finally:
            config_path.unlink()
    
    def test_mixed_error_conditions(self):
        """Test configuration with multiple types of potential errors."""
        config_data = {
            "valid": {"value": "good"},
            "valid_ref": "{{ values.valid.value }}",
            "missing_ref": "{{ values.does.not.exist }}",
            "another_valid": "{{ values.valid_ref }}-extended"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.dump(config_data, f)
            config_path = Path(f.name)
        
        try:
            loader = ParameterLoader(config_path, resolve_references=True)
            
            with pytest.raises(ValueError) as exc_info:
                loader.load()
            
            error_msg = str(exc_info.value)
            assert "Reference resolution failed" in error_msg
            assert "does.not.exist" in error_msg
            
        finally:
            config_path.unlink()
    
    def test_resolution_disabled_no_errors(self):
        """Test that disabling resolution bypasses all resolver errors."""
        config_data = {
            "circular_a": "{{ values.circular_b }}",
            "circular_b": "{{ values.circular_a }}",
            "missing": "{{ values.does.not.exist }}"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.dump(config_data, f)
            config_path = Path(f.name)
        
        try:
            # With resolution disabled, should not raise any resolver errors
            loader = ParameterLoader(config_path, resolve_references=False)
            result = loader.load()
            
            # Should return original unresolved config
            assert result["circular_a"] == "{{ values.circular_b }}"
            assert result["missing"] == "{{ values.does.not.exist }}"
            
        finally:
            config_path.unlink()
    
    def test_malformed_yaml_still_errors(self):
        """Test that YAML syntax errors still occur even with resolver disabled."""
        malformed_yaml = """
        invalid: yaml: content:
          - missing quote: "unclosed
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write(malformed_yaml)
            config_path = Path(f.name)
        
        try:
            loader = ParameterLoader(config_path, resolve_references=False)
            
            with pytest.raises(ValueError) as exc_info:
                loader.load()
            
            error_msg = str(exc_info.value)
            assert "Invalid configuration file format" in error_msg
            
        finally:
            config_path.unlink()


class TestPerformanceAndBenchmarks:
    """Test performance characteristics and add basic benchmarks."""
    
    def test_large_configuration_performance(self):
        """Test performance with large configurations."""
        import time
        
        # Create a large configuration
        config_data = {"base": {"value": "test"}}
        
        # Add 200 simple references
        for i in range(200):
            config_data[f"simple_{i}"] = f"{{{{ values.base.value }}}}-{i}"
        
        # Add 50 chained references
        for i in range(50):
            if i == 0:
                config_data[f"chain_{i}"] = "{{ values.base.value }}-chain"
            else:
                config_data[f"chain_{i}"] = f"{{{{ values.chain_{i-1} }}}}-{i}"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.dump(config_data, f)
            config_path = Path(f.name)
        
        try:
            loader = ParameterLoader(config_path, resolve_references=True)
            
            start_time = time.time()
            result = loader.load()
            end_time = time.time()
            
            resolution_time = end_time - start_time
            
            # Verify correct resolution
            assert result["simple_0"] == "test-0"
            assert result["simple_199"] == "test-199"
            assert "test-chain-1-2" in result["chain_2"]
            
            # Performance should be reasonable (increased from 200ms due to larger dataset)
            assert resolution_time < 0.5, f"Resolution took {resolution_time:.3f}s, expected < 0.5s"
            
        finally:
            config_path.unlink()
    
    def test_deep_nesting_performance(self):
        """Test performance with deeply nested references."""
        import time
        
        config_data = {}
        
        # Create deep nesting structure
        depth = 20
        for i in range(depth):
            if i == 0:
                config_data[f"level_{i}"] = "base"
            else:
                config_data[f"level_{i}"] = f"{{{{ values.level_{i-1} }}}}-{i}"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.dump(config_data, f)
            config_path = Path(f.name)
        
        try:
            loader = ParameterLoader(config_path, resolve_references=True)
            
            start_time = time.time()
            result = loader.load()
            end_time = time.time()
            
            resolution_time = end_time - start_time
            
            # Verify deep nesting resolved correctly
            assert "base" in result[f"level_{depth-1}"]
            assert f"-{depth-1}" in result[f"level_{depth-1}"]
            
            # Should handle deep nesting efficiently
            assert resolution_time < 0.1, f"Deep nesting resolution took {resolution_time:.3f}s, expected < 0.1s"
            
        finally:
            config_path.unlink()


class TestRealWorldConfigurations:
    """Test with realistic real-world configuration patterns."""
    
    def test_microservices_deployment_config(self):
        """Test realistic microservices deployment configuration."""
        config_data = {
            "environment": "production",
            "region": "us-east-1",
            "project": {
                "name": "ecommerce-platform",
                "version": "2.1.0"
            },
            "infrastructure": {
                "vpc_id": "vpc-12345",
                "subnet_prefix": "10.0"
            },
            "services": {
                "api": {
                    "name": "{{ values.project.name }}-api",
                    "port": 8080,
                    "replicas": 3,
                    "image": "{{ values.docker.registry }}/{{ values.services.api.name }}:{{ values.project.version }}",
                    "url": "https://{{ values.services.api.name }}.{{ values.environment }}.{{ values.domain.base }}"
                },
                "frontend": {
                    "name": "{{ values.project.name }}-web",
                    "port": 3000,
                    "replicas": 2,
                    "image": "{{ values.docker.registry }}/{{ values.services.frontend.name }}:{{ values.project.version }}",
                    "url": "https://{{ values.services.frontend.name }}.{{ values.environment }}.{{ values.domain.base }}"
                },
                "worker": {
                    "name": "{{ values.project.name }}-worker",
                    "replicas": 1,
                    "image": "{{ values.docker.registry }}/{{ values.services.worker.name }}:{{ values.project.version }}"
                }
            },
            "docker": {
                "registry": "123456789012.dkr.ecr.{{ values.region }}.amazonaws.com"
            },
            "domain": {
                "base": "mycompany.com"
            },
            "database": {
                "host": "{{ values.project.name }}-{{ values.environment }}.cluster-xyz.{{ values.region }}.rds.amazonaws.com",
                "name": "{{ values.project.name | replace('-', '_') }}_{{ values.environment }}",
                "url": "postgresql://user:pass@{{ values.database.host }}/{{ values.database.name }}"
            },
            "monitoring": {
                "namespace": "{{ values.project.name }}/{{ values.environment }}",
                "alerts": {
                    "api_health": "{{ values.services.api.url }}/health",
                    "frontend_health": "{{ values.services.frontend.url }}/health"
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.dump(config_data, f)
            config_path = Path(f.name)
        
        try:
            loader = ParameterLoader(config_path, resolve_references=True, verbose=True)
            
            # Capture verbose output
            captured_output = io.StringIO()
            with redirect_stdout(captured_output):
                result = loader.load()
            
            # Verify complex resolutions
            assert result["services"]["api"]["name"] == "ecommerce-platform-api"
            assert result["services"]["api"]["image"] == "123456789012.dkr.ecr.us-east-1.amazonaws.com/ecommerce-platform-api:2.1.0"
            assert result["services"]["api"]["url"] == "https://ecommerce-platform-api.production.mycompany.com"
            
            assert result["database"]["host"] == "ecommerce-platform-production.cluster-xyz.us-east-1.rds.amazonaws.com"
            assert result["database"]["name"] == "ecommerce_platform_production"
            assert "postgresql://user:pass@ecommerce-platform-production" in result["database"]["url"]
            
            assert result["monitoring"]["alerts"]["api_health"] == "https://ecommerce-platform-api.production.mycompany.com/health"
            
            # Verify verbose output was generated
            output = captured_output.getvalue()
            assert "Built dependency graph" in output
            
        finally:
            config_path.unlink()
    
    def test_kubernetes_helm_values_pattern(self):
        """Test Kubernetes/Helm values pattern with references."""
        config_data = {
            "global": {
                "imageRegistry": "registry.mycompany.com",
                "imageTag": "v1.2.3",
                "namespace": "my-app-prod"
            },
            "app": {
                "name": "my-application",
                "fullName": "{{ values.global.namespace }}-{{ values.app.name }}",
                "labels": {
                    "app": "{{ values.app.name }}",
                    "version": "{{ values.global.imageTag }}"
                }
            },
            "images": {
                "api": "{{ values.global.imageRegistry }}/{{ values.app.name }}-api:{{ values.global.imageTag }}",
                "worker": "{{ values.global.imageRegistry }}/{{ values.app.name }}-worker:{{ values.global.imageTag }}",
                "nginx": "{{ values.global.imageRegistry }}/nginx:stable"
            },
            "ingress": {
                "enabled": True,
                "host": "{{ values.app.name }}.mycompany.com",
                "annotations": {
                    "rewrite_target": "/{{ values.app.name }}/"
                }
            },
            "secrets": {
                "name": "{{ values.app.fullName }}-secrets",
                "dockerRegistry": "{{ values.app.fullName }}-registry-secret"
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.dump(config_data, f)
            config_path = Path(f.name)
        
        try:
            loader = ParameterLoader(config_path, resolve_references=True)
            result = loader.load()
            
            # Verify Kubernetes-style resolutions
            assert result["app"]["fullName"] == "my-app-prod-my-application"
            assert result["images"]["api"] == "registry.mycompany.com/my-application-api:v1.2.3"
            assert result["secrets"]["name"] == "my-app-prod-my-application-secrets"
            assert result["ingress"]["annotations"]["rewrite_target"] == "/my-application/"
            
        finally:
            config_path.unlink()