"""Tests for external replacements functionality."""

import json
import tempfile
from pathlib import Path
from typing import Dict, Any

import pytest
import yaml

from template_customizer.core.external_replacements import (
    ExternalReplacementConfig,
    ExternalReplacementError,
)
from template_customizer.core.replacers.json_replacer import JSONReplacer
from template_customizer.core.replacers.markdown_replacer import MarkdownReplacer


class TestExternalReplacementConfig:
    """Tests for parsing and validating external replacement configuration."""
    
    def test_parse_empty_config(self):
        """Test handling of config without replacements section."""
        config = {"project": {"name": "test"}}
        ext_config = ExternalReplacementConfig(config)
        
        assert ext_config.get_json_replacements() == {}
        assert ext_config.get_markdown_replacements() == {}
        assert ext_config.has_replacements() is False
    
    def test_parse_json_replacements(self):
        """Test parsing JSON replacement rules."""
        config = {
            "replacements": {
                "json": {
                    "package.json": {
                        "$.name": "{{ values.project.name }}",
                        "$.version": "{{ values.version }}",
                        "$.config.port": "{{ values.port }}"
                    },
                    "tsconfig.json": {
                        "$.compilerOptions.outDir": "./build"
                    }
                }
            }
        }
        
        ext_config = ExternalReplacementConfig(config)
        json_rules = ext_config.get_json_replacements()
        
        assert "package.json" in json_rules
        assert "tsconfig.json" in json_rules
        assert json_rules["package.json"]["$.name"] == "{{ values.project.name }}"
        assert json_rules["package.json"]["$.config.port"] == "{{ values.port }}"
        assert ext_config.has_replacements() is True
    
    def test_parse_markdown_replacements(self):
        """Test parsing Markdown replacement rules."""
        config = {
            "replacements": {
                "markdown": {
                    "README.md": {
                        "pattern: # Project": "# {{ values.name }}",
                        "pattern: Version: .*": "Version: {{ values.version }}"
                    },
                    "CONTRIBUTING.md": {
                        "pattern: email@example.com": "{{ values.email }}"
                    }
                }
            }
        }
        
        ext_config = ExternalReplacementConfig(config)
        md_rules = ext_config.get_markdown_replacements()
        
        assert "README.md" in md_rules
        assert "CONTRIBUTING.md" in md_rules
        assert md_rules["README.md"]["pattern: # Project"] == "# {{ values.name }}"
        assert ext_config.has_replacements() is True
    
    def test_parse_mixed_replacements(self):
        """Test parsing both JSON and Markdown replacements."""
        config = {
            "replacements": {
                "json": {
                    "package.json": {"$.name": "test"}
                },
                "markdown": {
                    "README.md": {"pattern: test": "value"}
                }
            }
        }
        
        ext_config = ExternalReplacementConfig(config)
        
        assert len(ext_config.get_json_replacements()) == 1
        assert len(ext_config.get_markdown_replacements()) == 1
        assert ext_config.has_replacements() is True
    
    def test_get_files_to_process(self):
        """Test getting list of all files that have replacements."""
        config = {
            "replacements": {
                "json": {
                    "package.json": {"$.name": "test"},
                    "composer.json": {"$.name": "test"}
                },
                "markdown": {
                    "README.md": {"pattern: test": "value"}
                }
            }
        }
        
        ext_config = ExternalReplacementConfig(config)
        files = ext_config.get_files_to_process()
        
        assert len(files) == 3
        assert Path("package.json") in files
        assert Path("composer.json") in files
        assert Path("README.md") in files
    
    def test_get_file_type(self):
        """Test determining file type for a given file."""
        config = {
            "replacements": {
                "json": {"package.json": {"$.name": "test"}},
                "markdown": {"README.md": {"pattern: test": "value"}}
            }
        }
        
        ext_config = ExternalReplacementConfig(config)
        
        assert ext_config.get_file_type(Path("package.json")) == "json"
        assert ext_config.get_file_type(Path("README.md")) == "markdown"
        assert ext_config.get_file_type(Path("unknown.txt")) is None


class TestJSONReplacer:
    """Tests for JSON file replacements."""
    
    @pytest.fixture
    def sample_json(self):
        """Sample JSON content for testing."""
        return {
            "name": "old-name",
            "version": "1.0.0",
            "description": "Old description",
            "config": {
                "port": 3000,
                "debug": False,
                "database": {
                    "host": "localhost",
                    "port": 5432
                }
            },
            "keywords": ["old", "template"],
            "numbers": [1, 2, 3]
        }
    
    @pytest.fixture
    def parameters(self):
        """Sample parameters for template rendering."""
        return {
            "project": {
                "name": "new-name",
                "version": "2.0.0",
                "description": "New description"
            },
            "config": {
                "port": 8080,
                "debug": True,
                "db_host": "db.example.com"
            }
        }
    
    def test_simple_string_replacement(self, sample_json, parameters):
        """Test replacing simple string values."""
        replacer = JSONReplacer(parameters)
        replacements = {
            "$.name": "{{ values.project.name }}",
            "$.description": "{{ values.project.description }}"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_json, f, indent=2)
            temp_path = Path(f.name)
        
        try:
            result = replacer.replace(temp_path, replacements)
            result_data = json.loads(result)
            
            assert result_data["name"] == "new-name"
            assert result_data["description"] == "New description"
            assert result_data["version"] == "1.0.0"  # Unchanged
        finally:
            temp_path.unlink()
    
    def test_nested_path_replacement(self, sample_json, parameters):
        """Test replacing values in nested objects."""
        replacer = JSONReplacer(parameters)
        replacements = {
            "$.config.port": "{{ values.config.port }}",
            "$.config.database.host": "{{ values.config.db_host }}"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_json, f, indent=2)
            temp_path = Path(f.name)
        
        try:
            result = replacer.replace(temp_path, replacements)
            result_data = json.loads(result)
            
            assert result_data["config"]["port"] == 8080
            assert result_data["config"]["database"]["host"] == "db.example.com"
            assert result_data["config"]["database"]["port"] == 5432  # Unchanged
        finally:
            temp_path.unlink()
    
    def test_boolean_replacement(self, sample_json, parameters):
        """Test replacing boolean values."""
        replacer = JSONReplacer(parameters)
        replacements = {
            "$.config.debug": "{{ values.config.debug }}"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_json, f, indent=2)
            temp_path = Path(f.name)
        
        try:
            result = replacer.replace(temp_path, replacements)
            result_data = json.loads(result)
            
            assert result_data["config"]["debug"] is True
            assert isinstance(result_data["config"]["debug"], bool)
        finally:
            temp_path.unlink()
    
    def test_array_element_replacement(self, sample_json, parameters):
        """Test replacing array elements."""
        replacer = JSONReplacer(parameters)
        replacements = {
            "$.keywords[0]": "{{ values.project.name }}",
            "$.numbers[1]": "42"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_json, f, indent=2)
            temp_path = Path(f.name)
        
        try:
            result = replacer.replace(temp_path, replacements)
            result_data = json.loads(result)
            
            assert result_data["keywords"][0] == "new-name"
            assert result_data["keywords"][1] == "template"  # Unchanged
            assert result_data["numbers"][1] == 42
            assert isinstance(result_data["numbers"][1], int)
        finally:
            temp_path.unlink()
    
    def test_preserve_json_formatting(self, sample_json, parameters):
        """Test that JSON formatting is preserved."""
        replacer = JSONReplacer(parameters)
        replacements = {
            "$.name": "{{ values.project.name }}"
        }
        
        # Create JSON with specific formatting
        json_content = '{\n  "name": "old",\n  "nested": {\n    "value": true\n  }\n}'
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(json_content)
            temp_path = Path(f.name)
        
        try:
            result = replacer.replace(temp_path, replacements)
            
            # Check that indentation is preserved
            assert '  "name"' in result
            assert '  "nested"' in result
            assert '    "value"' in result
            
            # Verify it's valid JSON
            json.loads(result)
        finally:
            temp_path.unlink()
    
    def test_invalid_jsonpath(self, sample_json, parameters):
        """Test handling of invalid JSONPath expressions."""
        replacer = JSONReplacer(parameters)
        replacements = {
            "$.[invalid syntax]": "value"  # Invalid JSONPath syntax
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_json, f)
            temp_path = Path(f.name)
        
        try:
            with pytest.raises(ExternalReplacementError):
                replacer.replace(temp_path, replacements)
        finally:
            temp_path.unlink()
    
    def test_nonexistent_path(self, sample_json, parameters):
        """Test replacing non-existent path creates new value."""
        replacer = JSONReplacer(parameters)
        replacements = {
            "$.newField": "{{ values.project.name }}",
            "$.config.newNested": "new-value"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_json, f)
            temp_path = Path(f.name)
        
        try:
            result = replacer.replace(temp_path, replacements)
            result_data = json.loads(result)
            
            assert result_data["newField"] == "new-name"
            assert result_data["config"]["newNested"] == "new-value"
        finally:
            temp_path.unlink()


class TestMarkdownReplacer:
    """Tests for Markdown file replacements."""
    
    @pytest.fixture
    def sample_markdown(self):
        """Sample Markdown content for testing."""
        return """# Old Project

Version: 1.0.0

## Installation

```bash
npm install old-project
```

## Docker

Pull the image:
```bash
docker pull docker.io/old-project:latest
```

## Configuration

The app runs on port 3000.

API endpoint: https://api.old.com/v1

## License

Copyright (c) 2023 Old Author
"""
    
    @pytest.fixture
    def parameters(self):
        """Sample parameters for template rendering."""
        return {
            "project": {
                "name": "new-project",
                "version": "2.0.0",
                "author": "New Author"
            },
            "docker": {
                "registry": "ghcr.io/company",
                "image": "new-project",
                "tag": "2.0.0"
            },
            "config": {
                "port": 8080,
                "api": "https://api.new.com/v2"
            }
        }
    
    def test_simple_pattern_replacement(self, sample_markdown, parameters):
        """Test simple pattern replacements."""
        replacer = MarkdownReplacer(parameters)
        replacements = {
            "pattern: # Old Project": "# {{ values.project.name | title }}",
            "pattern: Version: .*": "Version: {{ values.project.version }}"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(sample_markdown)
            temp_path = Path(f.name)
        
        try:
            result = replacer.replace(temp_path, replacements)
            
            assert "# New-Project" in result
            assert "Version: 2.0.0" in result
            assert "Old Project" not in result
            assert "Version: 1.0.0" not in result
        finally:
            temp_path.unlink()
    
    def test_regex_pattern_replacement(self, sample_markdown, parameters):
        """Test regex pattern replacements."""
        replacer = MarkdownReplacer(parameters)
        replacements = {
            "pattern: docker pull .*:latest": "docker pull {{ values.docker.registry }}/{{ values.docker.image }}:{{ values.docker.tag }}",
            "pattern: port \\d+": "port {{ values.config.port }}"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(sample_markdown)
            temp_path = Path(f.name)
        
        try:
            result = replacer.replace(temp_path, replacements)
            
            assert "docker pull ghcr.io/company/new-project:2.0.0" in result
            assert "port 8080" in result
            assert "port 3000" not in result
        finally:
            temp_path.unlink()
    
    def test_preserve_code_blocks(self, sample_markdown, parameters):
        """Test that code blocks are handled correctly."""
        replacer = MarkdownReplacer(parameters)
        replacements = {
            "pattern: npm install old-project": "npm install {{ values.project.name }}"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(sample_markdown)
            temp_path = Path(f.name)
        
        try:
            result = replacer.replace(temp_path, replacements)
            
            assert "```bash" in result
            assert "npm install new-project" in result
            assert "```" in result
            # Verify code block structure is preserved
            assert result.count("```") == 4  # Two code blocks
        finally:
            temp_path.unlink()
    
    def test_multiple_occurrences(self, parameters):
        """Test replacing multiple occurrences of a pattern."""
        content = """# Project

The old-name project is great.
Install old-name with npm.
Run old-name locally.
"""
        replacer = MarkdownReplacer(parameters)
        replacements = {
            "pattern: old-name": "{{ values.project.name }}"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            temp_path = Path(f.name)
        
        try:
            result = replacer.replace(temp_path, replacements)
            
            assert "old-name" not in result
            assert result.count("new-project") == 3
        finally:
            temp_path.unlink()
    
    def test_capture_groups(self, sample_markdown, parameters):
        """Test patterns with capture groups."""
        replacer = MarkdownReplacer(parameters)
        replacements = {
            "pattern: Copyright \\(c\\) (\\d+) .*": "Copyright (c) \\1 {{ values.project.author }}"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(sample_markdown)
            temp_path = Path(f.name)
        
        try:
            result = replacer.replace(temp_path, replacements)
            
            assert "Copyright (c) 2023 New Author" in result
            assert "Old Author" not in result
        finally:
            temp_path.unlink()
    
    def test_literal_pattern_flag(self, parameters):
        """Test literal (non-regex) pattern matching."""
        content = "Replace [special] characters (literally)."
        replacer = MarkdownReplacer(parameters)
        replacements = {
            "literal: [special]": "{{ values.project.name }}"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            temp_path = Path(f.name)
        
        try:
            result = replacer.replace(temp_path, replacements)
            
            assert "Replace new-project characters" in result
            assert "[special]" not in result
        finally:
            temp_path.unlink()
    
    def test_invalid_regex(self, parameters):
        """Test handling of invalid regex patterns."""
        replacer = MarkdownReplacer(parameters)
        replacements = {
            "pattern: [invalid(": "value"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("test content")
            temp_path = Path(f.name)
        
        try:
            with pytest.raises(ExternalReplacementError):
                replacer.replace(temp_path, replacements)
        finally:
            temp_path.unlink()


class TestBackwardCompatibility:
    """Tests to ensure backward compatibility with existing configs."""
    
    def test_config_without_replacements_section(self):
        """Test that configs without replacements section still work."""
        config = {
            "project": {
                "name": "test-project",
                "version": "1.0.0"
            },
            "server": {
                "port": 8080
            }
        }
        
        ext_config = ExternalReplacementConfig(config)
        
        # Should work without errors
        assert not ext_config.has_replacements()
        assert ext_config.get_json_replacements() == {}
        assert ext_config.get_markdown_replacements() == {}
        assert ext_config.get_files_to_process() == []
    
    def test_empty_replacements_section(self):
        """Test that empty replacements section is handled gracefully."""
        config = {
            "project": {"name": "test"},
            "replacements": {}
        }
        
        ext_config = ExternalReplacementConfig(config)
        assert not ext_config.has_replacements()
    
    def test_partial_replacements_section(self):
        """Test config with only JSON or only Markdown replacements."""
        # Only JSON
        config_json_only = {
            "replacements": {
                "json": {
                    "test.json": {"$.name": "value"}
                }
            }
        }
        ext_config = ExternalReplacementConfig(config_json_only)
        assert ext_config.has_replacements()
        assert len(ext_config.get_json_replacements()) == 1
        assert len(ext_config.get_markdown_replacements()) == 0
        
        # Only Markdown
        config_md_only = {
            "replacements": {
                "markdown": {
                    "test.md": {"pattern: test": "value"}
                }
            }
        }
        ext_config = ExternalReplacementConfig(config_md_only)
        assert ext_config.has_replacements()
        assert len(ext_config.get_json_replacements()) == 0
        assert len(ext_config.get_markdown_replacements()) == 1


class TestIntegration:
    """Integration tests for the complete external replacement flow."""
    
    def test_load_and_process_config_file(self):
        """Test loading config file with replacements and processing files."""
        config_path = Path("tests/fixtures/external/config_with_replacements.yml")
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        ext_config = ExternalReplacementConfig(config)
        
        # Verify config loaded correctly
        assert ext_config.has_replacements()
        
        json_rules = ext_config.get_json_replacements()
        assert "package.json" in json_rules
        assert "tsconfig.json" in json_rules
        
        md_rules = ext_config.get_markdown_replacements()
        assert "README.md" in md_rules
    
    def test_process_json_with_real_config(self):
        """Test processing actual JSON file with config."""
        config_path = Path("tests/fixtures/external/config_with_replacements.yml")
        json_path = Path("tests/fixtures/external/package.json")
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        ext_config = ExternalReplacementConfig(config)
        replacer = JSONReplacer(config)  # Pass full config for parameters
        
        json_rules = ext_config.get_json_replacements()["package.json"]
        
        # Create a temp copy to test
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(json_path.read_text())
            temp_path = Path(f.name)
        
        try:
            result = replacer.replace(temp_path, json_rules)
            result_data = json.loads(result)
            
            assert result_data["name"] == "my-awesome-app"
            assert result_data["version"] == "2.0.0"
            assert result_data["description"] == "An awesome application built from template"
            assert result_data["author"] == "Jane Developer"
            assert result_data["config"]["port"] == 8080
            assert result_data["config"]["debug"] is True
        finally:
            temp_path.unlink()
    
    def test_process_markdown_with_real_config(self):
        """Test processing actual Markdown file with config."""
        config_path = Path("tests/fixtures/external/config_with_replacements.yml")
        md_path = Path("tests/fixtures/external/README.md")
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        ext_config = ExternalReplacementConfig(config)
        replacer = MarkdownReplacer(config)
        
        md_rules = ext_config.get_markdown_replacements()["README.md"]
        
        # Create a temp copy to test
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(md_path.read_text())
            temp_path = Path(f.name)
        
        try:
            result = replacer.replace(temp_path, md_rules)
            
            assert "# My-Awesome-App" in result
            assert "Version: 2.0.0" in result
            assert "npm install my-awesome-app" in result
            assert "docker pull ghcr.io/mycompany/my-awesome-app:2.0.0" in result
            assert "port 8080" in result
            assert "https://api.mycompany.com/v2" in result
            assert "Copyright (c) 2024 Jane Developer" in result
        finally:
            temp_path.unlink()