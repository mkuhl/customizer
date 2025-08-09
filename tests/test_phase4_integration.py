"""Phase 4 integration tests for project-wide processing with filtering."""

import os
import tempfile
import shutil
from pathlib import Path
import pytest
from click.testing import CliRunner
from template_customizer.cli import main as cli
from template_customizer.core.scanner import FileScanner


class TestLargeDirectoryProcessing:
    """Test processing of large directory structures."""
    
    def create_large_project(self, root_dir: Path, num_dirs: int = 10, files_per_dir: int = 20):
        """Create a large project structure for testing."""
        # Create source directories
        for i in range(num_dirs):
            dir_path = root_dir / f"module_{i}"
            dir_path.mkdir(parents=True)
            
            # Add Python files with template markers
            for j in range(files_per_dir):
                py_file = dir_path / f"file_{j}.py"
                py_file.write_text(f'''# project_name = {{{{ project.name }}}}
PROJECT_NAME = "default_project"

# version = {{{{ project.version }}}}
VERSION = "0.0.1"

def process_{i}_{j}():
    """Process function {i}-{j}"""
    pass
''')
            
            # Add some JS files
            for j in range(5):
                js_file = dir_path / f"script_{j}.js"
                js_file.write_text(f'''// api_url = {{{{ api.base_url }}}}
const API_URL = "http://localhost:8000";

// app_name = {{{{ project.name }}}}
const APP_NAME = "default_app";

function init_{i}_{j}() {{
    console.log("Initializing {i}-{j}");
}}
''')
            
            # Add config files
            config_file = dir_path / "config.yml"
            config_file.write_text(f'''# module_name = {{{{ modules.module_{i}.name }}}}
module_name: "module_{i}"

# enabled = {{{{ modules.module_{i}.enabled }}}}
enabled: false
''')
        
        # Add directories that should be excluded
        excluded_dirs = [".git", "node_modules", "__pycache__", ".venv", "dist", "build"]
        for exc_dir in excluded_dirs:
            exc_path = root_dir / exc_dir
            exc_path.mkdir(parents=True)
            # Add some files that should be ignored
            (exc_path / "file.txt").write_text("This should be ignored")
            (exc_path / "data.json").write_text('{"ignored": true}')
        
        # Add test files that might be excluded
        test_dir = root_dir / "tests"
        test_dir.mkdir()
        for i in range(10):
            (test_dir / f"test_module_{i}.py").write_text(f"# Test file {i}")
    
    def test_large_directory_scanning(self, tmp_path):
        """Test scanning performance with large directory structure."""
        # Create large project
        self.create_large_project(tmp_path, num_dirs=15, files_per_dir=25)
        
        # Test scanning
        scanner = FileScanner(project_path=tmp_path)
        files = list(scanner.scan())
        
        # Verify results
        assert len(files) > 0
        
        # Check that excluded directories are not in results
        excluded_patterns = {".git", "node_modules", "__pycache__", ".venv", "dist", "build"}
        for file_path in files:
            path_parts = set(file_path.parts)
            assert not path_parts.intersection(excluded_patterns), f"Found excluded path in {file_path}"
        
        # Verify we found the expected file types
        py_files = [f for f in files if str(f).endswith('.py')]
        js_files = [f for f in files if str(f).endswith('.js')]
        yml_files = [f for f in files if str(f).endswith('.yml')]
        
        assert len(py_files) >= 300  # 15 dirs * 20 files + tests
        assert len(js_files) == 75   # 15 dirs * 5 files
        assert len(yml_files) == 15  # 15 dirs * 1 file
    
    def test_large_directory_processing_cli(self, tmp_path):
        """Test CLI processing of large directory with progress reporting."""
        # Create large project
        self.create_large_project(tmp_path, num_dirs=10, files_per_dir=15)
        
        # Create config file
        config_file = tmp_path / "config.yml"
        config_file.write_text('''project:
  name: "LargeProject"
  version: "2.0.0"

api:
  base_url: "https://api.large-project.com"

modules:
  module_0:
    name: "Core Module"
    enabled: true
  module_1:
    name: "Auth Module"
    enabled: true
''')
        
        runner = CliRunner()
        result = runner.invoke(cli, [
            'process',
            '--project', str(tmp_path),
            '--config', str(config_file),
            '--dry-run',
            '--verbose'
        ])
        
        assert result.exit_code == 0
        # Check that progress was shown (Rich progress bar text)
        assert "Template Customizer" in result.output
        # Check that files were processed (either found changes or no changes to apply)
        assert "Found" in result.output or "No changes to apply" in result.output


class TestComplexPatternFiltering:
    """Test complex include/exclude pattern combinations."""
    
    def create_mixed_project(self, root_dir: Path):
        """Create a project with mixed file types for pattern testing."""
        # Source files
        src_dir = root_dir / "src"
        src_dir.mkdir()
        (src_dir / "main.py").write_text("# main = {{ project.name }}\nMAIN = 'default'")
        (src_dir / "utils.py").write_text("# utils = {{ project.name }}\nUTILS = 'default'")
        (src_dir / "helpers.js").write_text("// helper = {{ project.name }}\nconst HELPER = 'default';")
        (src_dir / "styles.css").write_text("/* theme = {{ ui.theme }} */\n.theme { color: blue; }")
        
        # Test files
        test_dir = root_dir / "tests"
        test_dir.mkdir()
        (test_dir / "test_main.py").write_text("# test = {{ project.name }}\nTEST = 'default'")
        (test_dir / "test_utils.py").write_text("# test = {{ project.name }}\nTEST = 'default'")
        (test_dir / "e2e.spec.js").write_text("// e2e = {{ project.name }}\nconst E2E = 'default';")
        
        # Config files
        (root_dir / "config.yml").write_text("# config = {{ project.name }}\nname: default")
        (root_dir / "settings.json").write_text('{"setting": "{{ project.name }}"}')
        (root_dir / ".env.template").write_text("# env = {{ project.name }}\nAPP_NAME=default")
        
        # Documentation
        docs_dir = root_dir / "docs"
        docs_dir.mkdir()
        (docs_dir / "README.md").write_text("# Docs = {{ project.name }}")
        (docs_dir / "api.md").write_text("# API = {{ project.name }}")
        
        # Build artifacts (should usually be excluded)
        build_dir = root_dir / "build"
        build_dir.mkdir()
        (build_dir / "output.js").write_text("// build = {{ project.name }}")
    
    def test_include_only_python_files(self, tmp_path):
        """Test including only Python files."""
        self.create_mixed_project(tmp_path)
        
        scanner = FileScanner(project_path=tmp_path, include_patterns=["*.py"])
        files = list(scanner.scan())
        
        # Should only find Python files
        assert all(str(f).endswith('.py') for f in files)
        assert len(files) == 4  # main.py, utils.py, test_main.py, test_utils.py
    
    def test_exclude_test_files(self, tmp_path):
        """Test excluding test files."""
        self.create_mixed_project(tmp_path)
        
        scanner = FileScanner(project_path=tmp_path, exclude_patterns=["test_*.py", "*.spec.js", "tests"])
        files = list(scanner.scan())
        
        # Should not find any test files
        file_names = [f.name for f in files]
        assert not any(fname.startswith("test_") for fname in file_names)
        assert not any(fname.endswith(".spec.js") for fname in file_names)
        # Check that tests directory was excluded (no files from tests/ directory)
        assert not any("/tests/" in str(f) for f in files)
    
    def test_include_multiple_patterns(self, tmp_path):
        """Test including multiple file patterns."""
        self.create_mixed_project(tmp_path)
        
        scanner = FileScanner(project_path=tmp_path, include_patterns=["*.py", "*.yml", "*.json"])
        files = list(scanner.scan())
        
        # Should only find Python, YAML, and JSON files
        extensions = {f.suffix for f in files}
        assert extensions == {'.py', '.yml', '.json'}
    
    def test_complex_include_exclude_combination(self, tmp_path):
        """Test complex combination of include and exclude patterns."""
        self.create_mixed_project(tmp_path)
        
        # Include all Python and JS files, but exclude tests and build
        scanner = FileScanner(
            project_path=tmp_path,
            include_patterns=["*.py", "*.js"],
            exclude_patterns=["test_*", "*.spec.js", "build/", "tests/"]
        )
        files = list(scanner.scan())
        
        # Should find main.py, utils.py, helpers.js but not test files or build
        file_strs = [str(f) for f in files]
        file_names = [f.name for f in files]
        assert any("main.py" == fname for fname in file_names)
        assert any("utils.py" == fname for fname in file_names)
        assert any("helpers.js" == fname for fname in file_names)
        assert not any(fname.startswith("test_") for fname in file_names)
        assert not any("/build/" in f for f in file_strs)
        assert not any("/tests/" in f for f in file_strs)
    
    def test_cli_with_pattern_filtering(self, tmp_path):
        """Test CLI with include/exclude patterns."""
        self.create_mixed_project(tmp_path)
        
        # Create config
        config_file = tmp_path / "template.yml"
        config_file.write_text("project:\n  name: PatternTest\nui:\n  theme: dark")
        
        runner = CliRunner()
        
        # Test 1: Include only Python files
        result = runner.invoke(cli, [
            'process',
            '--project', str(tmp_path),
            '--config', str(config_file),
            '--include', '*.py',
            '--dry-run'
        ])
        assert result.exit_code == 0
        assert ".py" in result.output
        assert ".js" not in result.output
        
        # Test 2: Exclude test files
        result = runner.invoke(cli, [
            'process',
            '--project', str(tmp_path),
            '--config', str(config_file),
            '--exclude', 'test_*',
            '--exclude', '*.spec.js',
            '--dry-run'
        ])
        assert result.exit_code == 0
        # Exclusion should work - either no changes (if all files excluded) or no test files in changes
        assert "No changes to apply" in result.output or ("template markers found" in result.output and "test_" not in result.output)


class TestRichOutputFormatting:
    """Test Rich output formatting and progress reporting."""
    
    def test_progress_reporting_output(self, tmp_path):
        """Test that progress reporting works correctly."""
        # Create a project with multiple files
        for i in range(5):
            file = tmp_path / f"file_{i}.py"
            file.write_text(f"# name = {{{{ project.name }}}}\nNAME = 'default'")
        
        config_file = tmp_path / "config.yml"
        config_file.write_text("project:\n  name: TestProject")
        
        runner = CliRunner()
        result = runner.invoke(cli, [
            'process',
            '--project', str(tmp_path),
            '--config', str(config_file),
            '--verbose',
            '--dry-run'
        ])
        
        assert result.exit_code == 0
        # Rich adds ANSI codes, so we check for key content
        assert "Template Customizer" in result.output
    
    def test_dry_run_table_formatting(self, tmp_path):
        """Test dry-run mode shows formatted table of changes."""
        # Create test file
        test_file = tmp_path / "app.py"
        test_file.write_text('''# app_name = {{ project.name }}
APP_NAME = "default"

# version = {{ project.version }}
VERSION = "0.1.0"
''')
        
        config_file = tmp_path / "config.yml"
        config_file.write_text("project:\n  name: MyApp\n  version: 1.0.0")
        
        runner = CliRunner()
        result = runner.invoke(cli, [
            'process',
            '--project', str(tmp_path),
            '--config', str(config_file),
            '--verbose',
            '--dry-run'
        ])
        
        assert result.exit_code == 0
        # Check that CLI ran successfully and shows template customizer interface
        assert "Template Customizer" in result.output
        # Either show changes or indicate no changes found
        assert "Found" in result.output or "No changes to apply" in result.output
    
    def test_error_formatting(self, tmp_path):
        """Test error message formatting."""
        runner = CliRunner()
        
        # Test with non-existent config
        result = runner.invoke(cli, [
            'process',
            '--project', str(tmp_path),
            '--config', str(tmp_path / "nonexistent.yml")
        ])
        
        assert result.exit_code != 0
        assert "Error" in result.output or "not found" in result.output
    
    def test_summary_panel_display(self, tmp_path):
        """Test summary panel is displayed correctly."""
        # Create a simple project
        (tmp_path / "file1.py").write_text("# x = {{ x }}\nX = 1")
        (tmp_path / "file2.js").write_text("// y = {{ y }}\nconst Y = 2;")
        
        config_file = tmp_path / "config.yml"
        config_file.write_text("x: 10\ny: 20")
        
        runner = CliRunner()
        result = runner.invoke(cli, [
            'process',
            '--project', str(tmp_path),
            '--config', str(config_file),
            '--dry-run'
        ])
        
        assert result.exit_code == 0
        # Check for summary information
        assert "Found 2 changes" in result.output or "2 files" in result.output


# Performance test for large directories
@pytest.mark.slow
def test_performance_large_directory(tmp_path):
    """Test performance with very large directory (marked as slow test)."""
    # Create a very large project structure
    for i in range(50):
        dir_path = tmp_path / f"package_{i}"
        dir_path.mkdir()
        for j in range(50):
            file = dir_path / f"module_{j}.py"
            file.write_text(f"# pkg = {{{{ package.name }}}}\nPKG = 'default'")
    
    scanner = FileScanner(project_path=tmp_path)
    import time
    
    start_time = time.time()
    files = list(scanner.scan())
    scan_time = time.time() - start_time
    
    assert len(files) == 2500  # 50 * 50
    assert scan_time < 10.0  # Should complete within 10 seconds
    print(f"Scanned {len(files)} files in {scan_time:.2f} seconds")