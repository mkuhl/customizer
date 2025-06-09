"""Tests for version management functionality."""

import pytest
from pathlib import Path
import tempfile
import shutil

from template_customizer.utils.version import (
    SemanticVersion, 
    VersionParser, 
    VersionManager,
    get_version_info
)
from template_customizer.utils.version_bump import (
    VersionBumper,
    VersionCompatibilityChecker,
    get_version_changelog_entry
)


class TestSemanticVersion:
    """Test SemanticVersion class."""
    
    def test_create_version(self):
        """Test creating a semantic version."""
        version = SemanticVersion(1, 2, 3)
        assert version.major == 1
        assert version.minor == 2
        assert version.patch == 3
        assert version.prerelease is None
        assert version.build is None
    
    def test_create_version_with_prerelease(self):
        """Test creating a version with prerelease."""
        version = SemanticVersion(1, 0, 0, prerelease="alpha.1")
        assert version.prerelease == "alpha.1"
        assert str(version) == "1.0.0-alpha.1"
    
    def test_create_version_with_build(self):
        """Test creating a version with build metadata."""
        version = SemanticVersion(1, 0, 0, build="20230101")
        assert version.build == "20230101"
        assert str(version) == "1.0.0+20230101"
    
    def test_version_string_representation(self):
        """Test string representation of versions."""
        assert str(SemanticVersion(1, 2, 3)) == "1.2.3"
        assert str(SemanticVersion(1, 0, 0, prerelease="alpha")) == "1.0.0-alpha"
        assert str(SemanticVersion(1, 0, 0, build="123")) == "1.0.0+123"
        assert str(SemanticVersion(1, 0, 0, prerelease="alpha", build="123")) == "1.0.0-alpha+123"
    
    def test_version_equality(self):
        """Test version equality comparison."""
        v1 = SemanticVersion(1, 2, 3)
        v2 = SemanticVersion(1, 2, 3)
        v3 = SemanticVersion(1, 2, 4)
        
        assert v1 == v2
        assert v1 != v3
    
    def test_version_comparison(self):
        """Test version comparison operators."""
        v1 = SemanticVersion(1, 0, 0)
        v2 = SemanticVersion(1, 1, 0)
        v3 = SemanticVersion(2, 0, 0)
        
        assert v1 < v2
        assert v2 < v3
        assert v3 > v1
        assert v1 <= v2
        assert v3 >= v1
    
    def test_prerelease_comparison(self):
        """Test prerelease version comparison."""
        v1 = SemanticVersion(1, 0, 0, prerelease="alpha")
        v2 = SemanticVersion(1, 0, 0, prerelease="beta")
        v3 = SemanticVersion(1, 0, 0)
        
        assert v1 < v2
        assert v2 < v3  # Normal version > prerelease
    
    def test_compatibility_check(self):
        """Test version compatibility checking."""
        v1 = SemanticVersion(1, 2, 3)
        v2 = SemanticVersion(1, 3, 0)
        v3 = SemanticVersion(2, 0, 0)
        
        assert v1.is_compatible_with(v2)
        assert not v1.is_compatible_with(v3)
    
    def test_version_bumping(self):
        """Test version bumping methods."""
        version = SemanticVersion(1, 2, 3)
        
        major_bump = version.bump_major()
        assert major_bump == SemanticVersion(2, 0, 0)
        
        minor_bump = version.bump_minor()
        assert minor_bump == SemanticVersion(1, 3, 0)
        
        patch_bump = version.bump_patch()
        assert patch_bump == SemanticVersion(1, 2, 4)


class TestVersionParser:
    """Test VersionParser class."""
    
    def test_parse_valid_versions(self):
        """Test parsing valid version strings."""
        test_cases = [
            ("1.0.0", SemanticVersion(1, 0, 0)),
            ("1.2.3", SemanticVersion(1, 2, 3)),
            ("10.20.30", SemanticVersion(10, 20, 30)),
            ("1.0.0-alpha", SemanticVersion(1, 0, 0, prerelease="alpha")),
            ("1.0.0-alpha.1", SemanticVersion(1, 0, 0, prerelease="alpha.1")),
            ("1.0.0+build", SemanticVersion(1, 0, 0, build="build")),
            ("1.0.0-alpha+build", SemanticVersion(1, 0, 0, prerelease="alpha", build="build")),
        ]
        
        for version_string, expected in test_cases:
            result = VersionParser.parse(version_string)
            assert result == expected
    
    def test_parse_invalid_versions(self):
        """Test parsing invalid version strings."""
        invalid_versions = [
            "1.0",
            "1.0.0.0",
            "v1.0.0",
            "1.0.0-",
            "1.0.0+",
            "not.a.version",
            "",
            "1.2.3-alpha-",
        ]
        
        for invalid_version in invalid_versions:
            with pytest.raises(ValueError):
                VersionParser.parse(invalid_version)
    
    def test_is_valid(self):
        """Test version validation."""
        assert VersionParser.is_valid("1.0.0")
        assert VersionParser.is_valid("1.2.3-alpha.1")
        assert not VersionParser.is_valid("1.0")
        assert not VersionParser.is_valid("invalid")


class TestVersionManager:
    """Test VersionManager class."""
    
    def test_compare_versions(self):
        """Test version comparison."""
        assert VersionManager.compare_versions("1.0.0", "1.0.1") == -1
        assert VersionManager.compare_versions("1.0.1", "1.0.0") == 1
        assert VersionManager.compare_versions("1.0.0", "1.0.0") == 0
    
    def test_is_compatible(self):
        """Test compatibility checking."""
        assert VersionManager.is_compatible("1.0.0", "1.2.3")
        assert not VersionManager.is_compatible("1.0.0", "2.0.0")
    
    def test_get_next_version(self):
        """Test getting next version."""
        assert VersionManager.get_next_version("1.2.3", "major") == "2.0.0"
        assert VersionManager.get_next_version("1.2.3", "minor") == "1.3.0"
        assert VersionManager.get_next_version("1.2.3", "patch") == "1.2.4"
        
        with pytest.raises(ValueError):
            VersionManager.get_next_version("1.2.3", "invalid")


class TestVersionBumper:
    """Test VersionBumper class."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.project_root = self.temp_dir
        
        # Create directory structure
        src_dir = self.project_root / "src" / "template_customizer"
        src_dir.mkdir(parents=True)
        
        # Create __init__.py with version
        init_file = src_dir / "__init__.py"
        init_content = '''"""Template Customizer - Comment-based template processing tool."""

__version__ = "0.1.0"
__author__ = "Template Customizer"
__description__ = "A tool for customizing project templates using comment-based markers"
'''
        init_file.write_text(init_content)
        
        # Create pyproject.toml
        pyproject_file = self.project_root / "pyproject.toml"
        pyproject_content = '''[project]
name = "template-customizer"
version = "0.1.0"
description = "Test project"
'''
        pyproject_file.write_text(pyproject_content)
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_get_current_version(self):
        """Test getting current version."""
        bumper = VersionBumper(self.project_root)
        version = bumper.get_current_version()
        assert version == "0.1.0"
    
    def test_bump_version_dry_run(self):
        """Test version bumping in dry run mode."""
        bumper = VersionBumper(self.project_root)
        
        new_version = bumper.bump_version("minor", dry_run=True)
        assert new_version == "0.2.0"
        
        # File should not be modified
        current_version = bumper.get_current_version()
        assert current_version == "0.1.0"
    
    def test_bump_version_live(self):
        """Test actual version bumping."""
        bumper = VersionBumper(self.project_root)
        
        new_version = bumper.bump_version("patch", dry_run=False)
        assert new_version == "0.1.1"
        
        # File should be modified
        current_version = bumper.get_current_version()
        assert current_version == "0.1.1"
    
    def test_bump_major_version(self):
        """Test major version bump."""
        bumper = VersionBumper(self.project_root)
        
        new_version = bumper.bump_version("major", dry_run=False)
        assert new_version == "1.0.0"
        
        current_version = bumper.get_current_version()
        assert current_version == "1.0.0"


class TestVersionCompatibilityChecker:
    """Test VersionCompatibilityChecker class."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_compatible_config(self):
        """Test checking compatible config."""
        config_file = self.temp_dir / "config.yml"
        config_content = """
project:
  name: test
customizer_version: "1.2.0"
"""
        config_file.write_text(config_content)
        
        is_compatible, warning = VersionCompatibilityChecker.check_config_compatibility(
            config_file, "1.3.0"
        )
        
        assert is_compatible
        assert warning is None
    
    def test_incompatible_config(self):
        """Test checking incompatible config."""
        config_file = self.temp_dir / "config.yml"
        config_content = """
project:
  name: test
customizer_version: "2.0.0"
"""
        config_file.write_text(config_content)
        
        is_compatible, warning = VersionCompatibilityChecker.check_config_compatibility(
            config_file, "1.3.0"
        )
        
        assert not is_compatible
        assert warning is not None
        assert "compatibility issues" in warning
    
    def test_config_without_version(self):
        """Test config file without version information."""
        config_file = self.temp_dir / "config.yml"
        config_content = """
project:
  name: test
  description: A test project
"""
        config_file.write_text(config_content)
        
        is_compatible, warning = VersionCompatibilityChecker.check_config_compatibility(
            config_file, "1.0.0"
        )
        
        assert is_compatible
        assert warning is None


def test_get_version_changelog_entry():
    """Test changelog entry generation."""
    changes = ["Add new feature", "Fix bug in parser", "Update dependencies"]
    entry = get_version_changelog_entry("1.2.0", changes)
    
    assert "## [1.2.0]" in entry
    assert "- Add new feature" in entry
    assert "- Fix bug in parser" in entry
    assert "- Update dependencies" in entry


def test_get_version_info():
    """Test getting version info from package."""
    version_string, version_obj = get_version_info()
    
    assert isinstance(version_string, str)
    assert isinstance(version_obj, SemanticVersion)
    assert str(version_obj) == version_string