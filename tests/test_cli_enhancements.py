"""Test CLI enhancements: auto-config detection and --yes flag."""

import pytest
from pathlib import Path
from click.testing import CliRunner
import yaml

from template_customizer.cli import main


def test_auto_config_detection(temp_dir, sample_config):
    """Test automatic configuration file detection."""
    runner = CliRunner()
    
    # Create project structure
    project_dir = temp_dir / "test_project"
    project_dir.mkdir()
    
    # Create a simple file with template markers
    test_file = project_dir / "test.py"
    test_file.write_text('''# app_name = {{ values.project.name | quote }}
app_name = "DefaultApp"
''')
    
    # Create config file in project root
    config_file = project_dir / "config.yml"
    with open(config_file, 'w') as f:
        yaml.dump(sample_config, f)
    
    # Test auto-detection with dry run
    result = runner.invoke(main, [
        'process', 
        '--project', str(project_dir),
        '--dry-run'
    ])
    
    assert result.exit_code == 0
    assert "Using config file: config.yml" in result.output
    assert "TestApp" in result.output


def test_auto_config_detection_verbose(temp_dir, sample_config):
    """Test automatic configuration file detection with verbose output."""
    runner = CliRunner()
    
    # Create project structure
    project_dir = temp_dir / "test_project"
    project_dir.mkdir()
    
    # Create a simple file with template markers
    test_file = project_dir / "test.py"
    test_file.write_text('''# app_name = {{ values.project.name | quote }}
app_name = "DefaultApp"
''')
    
    # Create config file in project root with alternative name
    config_file = project_dir / "template-config.yml"
    with open(config_file, 'w') as f:
        yaml.dump(sample_config, f)
    
    # Test auto-detection with verbose
    result = runner.invoke(main, [
        'process', 
        '--project', str(project_dir),
        '--dry-run', 
        '--verbose'
    ])
    
    assert result.exit_code == 0
    assert "Found configuration file:" in result.output
    assert "template-config.yml" in result.output


def test_no_config_file_found(temp_dir):
    """Test error when no configuration file is found."""
    runner = CliRunner()
    
    # Create project structure without config file
    project_dir = temp_dir / "test_project"
    project_dir.mkdir()
    
    # Create a simple file
    test_file = project_dir / "test.py"
    test_file.write_text("print('hello')")
    
    # Test error when no config found
    result = runner.invoke(main, [
        'process', 
        '--project', str(project_dir),
        '--dry-run'
    ])
    
    assert result.exit_code == 1
    assert "No configuration file specified and none found" in result.output
    assert "Expected files:" in result.output


def test_config_file_priority(temp_dir, sample_config):
    """Test configuration file priority order."""
    runner = CliRunner()
    
    # Create project structure
    project_dir = temp_dir / "test_project"
    project_dir.mkdir()
    
    # Create a simple file with template markers
    test_file = project_dir / "test.py"
    test_file.write_text('''# app_name = {{ values.project.name | quote }}
app_name = "DefaultApp"
''')
    
    # Create multiple config files (config.yml should have priority)
    config1 = project_dir / "config.yml"
    config2 = project_dir / "template-config.yml"
    
    with open(config1, 'w') as f:
        yaml.dump(sample_config, f)
        
    # Different config for the second file
    alt_config = {"project": {"name": "AltApp", "version": "2.0.0"}}
    with open(config2, 'w') as f:
        yaml.dump(alt_config, f)
    
    # Test that config.yml takes priority
    result = runner.invoke(main, [
        'process', 
        '--project', str(project_dir),
        '--dry-run'
    ])
    
    assert result.exit_code == 0
    assert "Using config file: config.yml" in result.output
    assert "TestApp" in result.output  # From sample_config, not alt_config


def test_explicit_config_overrides_auto_detection(temp_dir, sample_config):
    """Test that explicit --config overrides auto-detection."""
    runner = CliRunner()
    
    # Create project structure
    project_dir = temp_dir / "test_project"
    project_dir.mkdir()
    
    # Create a simple file with template markers
    test_file = project_dir / "test.py"
    test_file.write_text('''# app_name = {{ values.project.name | quote }}
app_name = "DefaultApp"
''')
    
    # Create config file in project root
    auto_config = project_dir / "config.yml"
    with open(auto_config, 'w') as f:
        yaml.dump({"project": {"name": "AutoApp"}}, f)
    
    # Create explicit config file
    explicit_config = temp_dir / "explicit.yml"
    with open(explicit_config, 'w') as f:
        yaml.dump(sample_config, f)
    
    # Test that explicit config is used
    result = runner.invoke(main, [
        'process', 
        '--project', str(project_dir),
        '--config', str(explicit_config),
        '--dry-run'
    ])
    
    assert result.exit_code == 0
    assert "TestApp" in result.output  # From explicit config
    assert "AutoApp" not in result.output  # Not from auto-detected config


def test_yes_flag_functionality(temp_dir, sample_config):
    """Test --yes flag bypasses confirmation."""
    runner = CliRunner()
    
    # Create project structure
    project_dir = temp_dir / "test_project"
    project_dir.mkdir()
    
    # Create a simple file with template markers
    test_file = project_dir / "test.py"
    test_file.write_text('''# app_name = {{ values.project.name | quote }}
app_name = "DefaultApp"
''')
    
    # Create config file
    config_file = project_dir / "config.yml"
    with open(config_file, 'w') as f:
        yaml.dump(sample_config, f)
    
    # Test --yes flag (should not prompt)
    result = runner.invoke(main, [
        'process', 
        '--project', str(project_dir),
        '--yes'
    ])
    
    assert result.exit_code == 0
    assert "Apply these changes?" not in result.output
    assert "All changes applied successfully!" in result.output
    
    # Verify the change was made
    updated_content = test_file.read_text()
    assert 'app_name = "TestApp"' in updated_content


def test_confirmation_prompt_without_yes_flag(temp_dir, sample_config):
    """Test that confirmation prompt appears without --yes flag."""
    runner = CliRunner()
    
    # Create project structure
    project_dir = temp_dir / "test_project"
    project_dir.mkdir()
    
    # Create a simple file with template markers
    test_file = project_dir / "test.py"
    test_file.write_text('''# app_name = {{ values.project.name | quote }}
app_name = "DefaultApp"
''')
    
    # Create config file
    config_file = project_dir / "config.yml"
    with open(config_file, 'w') as f:
        yaml.dump(sample_config, f)
    
    # Test without --yes flag, answer 'n' to confirmation
    result = runner.invoke(main, [
        'process', 
        '--project', str(project_dir)
    ], input='n\n')
    
    assert result.exit_code == 0
    assert "Apply these changes?" in result.output
    assert "Changes cancelled by user" in result.output
    
    # Verify no changes were made
    original_content = test_file.read_text()
    assert 'app_name = "DefaultApp"' in original_content