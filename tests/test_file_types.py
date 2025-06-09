"""Test file type detection functionality."""

import pytest
from pathlib import Path
from template_customizer.utils.file_types import FileTypeDetector


class TestFileTypeDetector:
    """Test FileTypeDetector class."""
    
    def test_detect_comment_type_by_extension(self):
        """Test comment type detection by file extension."""
        detector = FileTypeDetector()
        
        # Python files
        assert detector.detect_comment_type(Path("test.py")) == "hash"
        assert detector.detect_comment_type(Path("test.pyi")) == "hash"
        
        # JavaScript/TypeScript files
        assert detector.detect_comment_type(Path("test.js")) == "double_slash"
        assert detector.detect_comment_type(Path("test.jsx")) == "double_slash"
        assert detector.detect_comment_type(Path("test.ts")) == "double_slash"
        assert detector.detect_comment_type(Path("test.tsx")) == "double_slash"
        assert detector.detect_comment_type(Path("test.mjs")) == "double_slash"
        
        # CSS files
        assert detector.detect_comment_type(Path("test.css")) == "css"
        assert detector.detect_comment_type(Path("test.scss")) == "css"
        assert detector.detect_comment_type(Path("test.sass")) == "css"
        assert detector.detect_comment_type(Path("test.less")) == "css"
        
        # HTML/XML files
        assert detector.detect_comment_type(Path("test.html")) == "html"
        assert detector.detect_comment_type(Path("test.htm")) == "html"
        assert detector.detect_comment_type(Path("test.xml")) == "html"
        assert detector.detect_comment_type(Path("test.svg")) == "html"
        
        # YAML files
        assert detector.detect_comment_type(Path("test.yml")) == "hash"
        assert detector.detect_comment_type(Path("test.yaml")) == "hash"
        
        # SQL files
        assert detector.detect_comment_type(Path("test.sql")) == "double_dash"
        
        # Shell files
        assert detector.detect_comment_type(Path("test.sh")) == "hash"
        assert detector.detect_comment_type(Path("test.bash")) == "hash"
        assert detector.detect_comment_type(Path("test.zsh")) == "hash"
        
        # Java/C/C++ files
        assert detector.detect_comment_type(Path("test.java")) == "double_slash"
        assert detector.detect_comment_type(Path("test.c")) == "double_slash"
        assert detector.detect_comment_type(Path("test.cpp")) == "double_slash"
        assert detector.detect_comment_type(Path("test.h")) == "double_slash"
        assert detector.detect_comment_type(Path("test.hpp")) == "double_slash"
        
        # Go/Rust/Swift files
        assert detector.detect_comment_type(Path("test.go")) == "double_slash"
        assert detector.detect_comment_type(Path("test.rs")) == "double_slash"
        assert detector.detect_comment_type(Path("test.swift")) == "double_slash"
        
        # Config files
        assert detector.detect_comment_type(Path("test.toml")) == "hash"
        assert detector.detect_comment_type(Path("test.cfg")) == "hash"
        assert detector.detect_comment_type(Path("test.conf")) == "hash"
        assert detector.detect_comment_type(Path("test.ini")) == "hash"
        
        # Lua files
        assert detector.detect_comment_type(Path("test.lua")) == "double_dash"
        
        # New languages added in Phase 2
        assert detector.detect_comment_type(Path("test.kt")) == "double_slash"  # Kotlin
        assert detector.detect_comment_type(Path("test.scala")) == "double_slash"  # Scala
        assert detector.detect_comment_type(Path("test.dart")) == "double_slash"  # Dart
        assert detector.detect_comment_type(Path("test.php")) == "double_slash"  # PHP
    
    def test_detect_comment_type_by_filename(self):
        """Test comment type detection by special filename patterns."""
        detector = FileTypeDetector()
        
        # Docker files
        assert detector.detect_comment_type(Path("Dockerfile")) == "hash"
        assert detector.detect_comment_type(Path("dockerfile")) == "hash"
        
        # Make files
        assert detector.detect_comment_type(Path("Makefile")) == "hash"
        assert detector.detect_comment_type(Path("makefile")) == "hash"
        
        # Ruby files
        assert detector.detect_comment_type(Path("Rakefile")) == "hash"
        assert detector.detect_comment_type(Path("Gemfile")) == "hash"
        assert detector.detect_comment_type(Path("Gemfile.lock")) == "hash"
        
        # Python packaging
        assert detector.detect_comment_type(Path("Pipfile")) == "hash"
        assert detector.detect_comment_type(Path("Pipfile.lock")) == "hash"
        assert detector.detect_comment_type(Path("requirements.txt")) == "hash"
        assert detector.detect_comment_type(Path("requirements-dev.txt")) == "hash"
        assert detector.detect_comment_type(Path("pyproject.toml")) == "hash"
        assert detector.detect_comment_type(Path("poetry.lock")) == "hash"
        
        # Git files
        assert detector.detect_comment_type(Path(".gitignore")) == "hash"
        assert detector.detect_comment_type(Path(".dockerignore")) == "hash"
        
        # Environment files
        assert detector.detect_comment_type(Path(".env")) == "hash"
        assert detector.detect_comment_type(Path(".env.local")) == "hash"
        assert detector.detect_comment_type(Path(".env.example")) == "hash"
        assert detector.detect_comment_type(Path(".env.development")) == "hash"
        assert detector.detect_comment_type(Path(".env.production")) == "hash"
        assert detector.detect_comment_type(Path(".env.test")) == "hash"
        
        # Rust files
        assert detector.detect_comment_type(Path("Cargo.toml")) == "hash"
        assert detector.detect_comment_type(Path("Cargo.lock")) == "hash"
        
        # Go files
        assert detector.detect_comment_type(Path("go.mod")) == "double_slash"
        assert detector.detect_comment_type(Path("go.sum")) == "double_slash"
    
    def test_detect_comment_type_multiple_extensions(self):
        """Test detection for files with multiple extensions."""
        detector = FileTypeDetector()
        
        # Environment files with multiple extensions
        assert detector.detect_comment_type(Path("config.env.local")) == "hash"
        assert detector.detect_comment_type(Path("app.config.yml")) == "hash"
        assert detector.detect_comment_type(Path("test.spec.ts")) == "double_slash"
        assert detector.detect_comment_type(Path("component.test.js")) == "double_slash"
    
    def test_detect_comment_type_unsupported(self):
        """Test detection for unsupported file types."""
        detector = FileTypeDetector()
        
        # Unsupported extensions
        assert detector.detect_comment_type(Path("test.unknown")) is None
        assert detector.detect_comment_type(Path("test.bin")) is None
        assert detector.detect_comment_type(Path("test.exe")) is None
        assert detector.detect_comment_type(Path("test.pdf")) is None
        
        # Unknown filenames
        assert detector.detect_comment_type(Path("unknown_file")) is None
    
    def test_detect_by_content_shebang(self, temp_dir):
        """Test content-based detection using shebang."""
        detector = FileTypeDetector()
        
        # Bash script
        bash_script = temp_dir / "script"
        bash_script.write_text("#!/bin/bash\necho 'hello'")
        assert detector.detect_comment_type(bash_script) == "hash"
        
        # Python script
        python_script = temp_dir / "script2"
        python_script.write_text("#!/usr/bin/env python3\nprint('hello')")
        assert detector.detect_comment_type(python_script) == "hash"
        
        # Node.js script
        node_script = temp_dir / "script3"
        node_script.write_text("#!/usr/bin/env node\nconsole.log('hello')")
        assert detector.detect_comment_type(node_script) == "double_slash"
        
        # Zsh script
        zsh_script = temp_dir / "script4"
        zsh_script.write_text("#!/bin/zsh\necho 'hello'")
        assert detector.detect_comment_type(zsh_script) == "hash"
    
    def test_detect_by_content_keywords(self, temp_dir):
        """Test content-based detection using language keywords."""
        detector = FileTypeDetector()
        
        # Python-like content
        python_file = temp_dir / "script"
        python_file.write_text("import os\nfrom pathlib import Path\nclass MyClass:\n    pass")
        assert detector.detect_comment_type(python_file) == "hash"
        
        # JavaScript-like content
        js_file = temp_dir / "script2"
        js_file.write_text("const name = 'test';\nlet value = 42;\nfunction hello() {}")
        assert detector.detect_comment_type(js_file) == "double_slash"
        
        # File with no clear indicators
        unclear_file = temp_dir / "script3"
        unclear_file.write_text("some random text\nwith no keywords")
        assert detector.detect_comment_type(unclear_file) is None
    
    def test_detect_by_content_binary_file(self, temp_dir):
        """Test content-based detection with binary file."""
        detector = FileTypeDetector()
        
        # Binary file
        binary_file = temp_dir / "binary"
        binary_file.write_bytes(b'\x00\x01\x02\x03\xff\xfe\xfd')
        assert detector.detect_comment_type(binary_file) is None
    
    def test_detect_by_content_nonexistent_file(self):
        """Test content-based detection with non-existent file."""
        detector = FileTypeDetector()
        
        # Non-existent file with no extension should return None
        assert detector.detect_comment_type(Path("nonexistent")) is None
    
    def test_is_supported_file(self):
        """Test checking if file is supported."""
        detector = FileTypeDetector()
        
        # Supported files
        assert detector.is_supported_file(Path("test.py")) is True
        assert detector.is_supported_file(Path("test.js")) is True
        assert detector.is_supported_file(Path("Dockerfile")) is True
        assert detector.is_supported_file(Path("test.css")) is True
        
        # Unsupported files
        assert detector.is_supported_file(Path("test.unknown")) is False
        assert detector.is_supported_file(Path("test.bin")) is False
    
    def test_get_supported_extensions(self):
        """Test getting list of supported extensions."""
        detector = FileTypeDetector()
        
        extensions = detector.get_supported_extensions()
        
        # Should contain all the extensions we defined
        assert ".py" in extensions
        assert ".js" in extensions
        assert ".css" in extensions
        assert ".html" in extensions
        assert ".yml" in extensions
        assert ".sql" in extensions
        assert ".kt" in extensions  # New in Phase 2
        assert ".dart" in extensions  # New in Phase 2
        
        # Should be a reasonable number of extensions
        assert len(extensions) > 30  # We have many extensions
    
    def test_get_comment_syntax_info(self):
        """Test getting comment syntax information."""
        detector = FileTypeDetector()
        
        # Hash comments
        info = detector.get_comment_syntax_info("hash")
        assert info['single_line'] == "#"
        assert "Python" in info['description']
        assert "{{ expression }}" in info['example']
        
        # Double slash comments
        info = detector.get_comment_syntax_info("double_slash")
        assert info['single_line'] == "//"
        assert "JavaScript" in info['description']
        
        # CSS comments
        info = detector.get_comment_syntax_info("css")
        assert info['single_line'] == "/* */"
        assert "CSS" in info['description']
        
        # HTML comments
        info = detector.get_comment_syntax_info("html")
        assert info['single_line'] == "<!-- -->"
        assert "HTML" in info['description']
        
        # Double dash comments
        info = detector.get_comment_syntax_info("double_dash")
        assert info['single_line'] == "--"
        assert "SQL" in info['description']
        
        # Unknown comment type
        info = detector.get_comment_syntax_info("unknown")
        assert info == {}
    
    def test_case_insensitive_detection(self):
        """Test that filename detection is case insensitive."""
        detector = FileTypeDetector()
        
        # Different cases should work
        assert detector.detect_comment_type(Path("DOCKERFILE")) == "hash"
        assert detector.detect_comment_type(Path("DockerFile")) == "hash"
        assert detector.detect_comment_type(Path("makefile")) == "hash"
        assert detector.detect_comment_type(Path("MAKEFILE")) == "hash"
        
        # Extensions should still be case sensitive in paths but normalized
        assert detector.detect_comment_type(Path("test.PY")) == "hash"
        assert detector.detect_comment_type(Path("test.JS")) == "double_slash"