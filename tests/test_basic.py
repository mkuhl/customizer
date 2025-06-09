"""Basic smoke tests for template customizer."""

import pytest
from pathlib import Path

def test_imports():
    """Test that all main modules can be imported."""
    # Core modules
    from template_customizer.core import scanner
    from template_customizer.core import parser
    from template_customizer.core import processor
    from template_customizer.core import writer
    
    # Utils modules
    from template_customizer.utils import file_types
    from template_customizer.utils import validation
    
    # CLI module
    from template_customizer import cli
    
    # Check that main classes exist
    assert hasattr(scanner, 'FileScanner')
    assert hasattr(parser, 'CommentParser')
    assert hasattr(processor, 'TemplateProcessor')
    assert hasattr(processor, 'ParameterLoader')
    assert hasattr(writer, 'FileWriter')
    assert hasattr(file_types, 'FileTypeDetector')
    assert hasattr(validation, 'ParameterValidator')


def test_package_version():
    """Test that package version is accessible."""
    import template_customizer
    assert hasattr(template_customizer, '__version__')
    assert template_customizer.__version__ == "0.1.0"


def test_file_scanner_basic(temp_dir):
    """Test basic FileScanner functionality."""
    from template_customizer.core.scanner import FileScanner
    
    # Create test files
    (temp_dir / "test.py").write_text("print('hello')")
    (temp_dir / "test.js").write_text("console.log('hello');")
    (temp_dir / "README.md").write_text("# Test")
    
    scanner = FileScanner(temp_dir)
    files = list(scanner.scan())
    
    assert len(files) == 3
    assert all(isinstance(f, Path) for f in files)


def test_comment_parser_basic():
    """Test basic CommentParser functionality."""
    from template_customizer.core.parser import CommentParser
    
    parser = CommentParser()
    
    # Test comment pattern detection
    assert parser._extract_comment_content("# test comment") == "test comment"
    assert parser._extract_comment_content("// test comment") == "test comment"
    assert parser._extract_comment_content("/* test comment */") == "test comment"
    assert parser._extract_comment_content("<!-- test comment -->") == "test comment"
    assert parser._extract_comment_content("regular line") is None


def test_parameter_loader_basic(temp_dir, sample_config):
    """Test basic ParameterLoader functionality."""
    from template_customizer.core.processor import ParameterLoader
    import yaml
    
    # Create test config file
    config_file = temp_dir / "config.yml"
    with open(config_file, 'w') as f:
        yaml.dump(sample_config, f)
    
    loader = ParameterLoader(config_file)
    loaded_config = loader.load()
    
    assert loaded_config == sample_config
    assert loaded_config["project"]["name"] == "TestApp"


def test_file_type_detector_basic():
    """Test basic FileTypeDetector functionality."""
    from template_customizer.utils.file_types import FileTypeDetector
    
    detector = FileTypeDetector()
    
    # Test common file types
    assert detector.detect_comment_type(Path("test.py")) == "hash"
    assert detector.detect_comment_type(Path("test.js")) == "double_slash"
    assert detector.detect_comment_type(Path("test.css")) == "css"
    assert detector.detect_comment_type(Path("test.html")) == "html"
    assert detector.detect_comment_type(Path("Dockerfile")) == "hash"
    
    # Test unsupported file
    assert detector.detect_comment_type(Path("test.unknown")) is None


def test_template_processor_basic(sample_config):
    """Test basic TemplateProcessor functionality."""
    from template_customizer.core.processor import TemplateProcessor
    
    processor = TemplateProcessor(sample_config)
    
    # Test simple template rendering
    result = processor.render_template("values.project.name")
    assert result == "TestApp"
    
    # Test template with filter
    result = processor.render_template("values.project.name | quote")
    assert result == '"TestApp"'


def test_cli_help(temp_dir):
    """Test that CLI help works."""
    from click.testing import CliRunner
    from template_customizer.cli import main
    
    runner = CliRunner()
    
    # Test main help
    result = runner.invoke(main, ['--help'])
    assert result.exit_code == 0
    assert "Template Customizer" in result.output
    
    # Test process command help
    result = runner.invoke(main, ['process', '--help'])
    assert result.exit_code == 0
    assert "Process template markers" in result.output
    
    # Test info command
    result = runner.invoke(main, ['info'])
    assert result.exit_code == 0
    assert "Supported File Types" in result.output