"""Test comment parser functionality."""

import pytest
from pathlib import Path
from template_customizer.core.parser import CommentParser, TemplateMarker
from template_customizer.utils.file_types import FileTypeDetector


class TestCommentParser:
    """Test CommentParser class."""
    
    def test_extract_comment_content_hash(self):
        """Test hash comment extraction."""
        parser = CommentParser()
        
        # Standard hash comments
        assert parser._extract_comment_content("# test comment") == "test comment"
        assert parser._extract_comment_content("  # indented comment  ") == "indented comment  "
        assert parser._extract_comment_content("#no space") == "no space"
        
        # Not comments
        assert parser._extract_comment_content("not a comment") is None
        assert parser._extract_comment_content("text # not at start") is None
    
    def test_extract_comment_content_double_slash(self):
        """Test double slash comment extraction."""
        parser = CommentParser()
        
        # Standard double slash comments
        assert parser._extract_comment_content("// test comment") == "test comment"
        assert parser._extract_comment_content("  // indented") == "indented"
        assert parser._extract_comment_content("//no space") == "no space"
        
        # Not comments
        assert parser._extract_comment_content("not // a comment") is None
    
    def test_extract_comment_content_css(self):
        """Test CSS-style comment extraction."""
        parser = CommentParser()
        
        # CSS comments
        assert parser._extract_comment_content("/* test comment */") == "test comment"
        assert parser._extract_comment_content("  /* indented */  ") == "indented"
        assert parser._extract_comment_content("/*no spaces*/") == "no spaces"
        
        # Multi-line (not supported in single line form)
        assert parser._extract_comment_content("/* start") is None
        assert parser._extract_comment_content("end */") is None
    
    def test_extract_comment_content_html(self):
        """Test HTML comment extraction."""
        parser = CommentParser()
        
        # HTML comments
        assert parser._extract_comment_content("<!-- test comment -->") == "test comment"
        assert parser._extract_comment_content("  <!-- indented -->  ") == "indented"
        assert parser._extract_comment_content("<!--no spaces-->") == "no spaces"
    
    def test_extract_comment_content_double_dash(self):
        """Test double dash comment extraction."""
        parser = CommentParser()
        
        # SQL/Lua style comments
        assert parser._extract_comment_content("-- test comment") == "test comment"
        assert parser._extract_comment_content("  -- indented") == "indented"
        assert parser._extract_comment_content("--no space") == "no space"
    
    def test_extract_template_marker_basic(self):
        """Test basic template marker extraction."""
        parser = CommentParser()
        
        # Valid markers
        result = parser._extract_template_marker("var_name = {{ expression }}")
        assert result == ("var_name", "expression")
        
        result = parser._extract_template_marker("app_name = {{ values.name }}")
        assert result == ("app_name", "values.name")
        
        result = parser._extract_template_marker("version = {{ values.version | quote }}")
        assert result == ("version", "values.version | quote")
        
        # Invalid markers
        assert parser._extract_template_marker("not a marker") is None
        assert parser._extract_template_marker("var = not jinja") is None
        assert parser._extract_template_marker("var = {{ }}") is None  # Empty expression
    
    def test_extract_template_marker_alternative_patterns(self):
        """Test alternative template marker patterns."""
        parser = CommentParser()
        
        # YAML style with colons
        result = parser._extract_template_marker("var_name: {{ expression }}")
        assert result == ("var_name", "expression")
        
        # Quoted variable names
        result = parser._extract_template_marker('"var_name" = {{ expression }}')
        assert result == ("var_name", "expression")
        
        result = parser._extract_template_marker("'var_name' = {{ expression }}")
        assert result == ("var_name", "expression")
        
        # Spaced braces
        result = parser._extract_template_marker("var_name = { { expression } }")
        assert result == ("var_name", "expression")
    
    def test_is_valid_variable_name(self):
        """Test variable name validation."""
        parser = CommentParser()
        
        # Valid names
        assert parser._is_valid_variable_name("app_name") is True
        assert parser._is_valid_variable_name("version") is True
        assert parser._is_valid_variable_name("api_url") is True
        assert parser._is_valid_variable_name("DATABASE_URL") is True
        assert parser._is_valid_variable_name("config2") is True
        
        # Invalid names
        assert parser._is_valid_variable_name("_private") is False  # Starts with underscore
        assert parser._is_valid_variable_name("2invalid") is False  # Starts with number
        assert parser._is_valid_variable_name("app-name") is False  # Contains hyphen
        assert parser._is_valid_variable_name("app.name") is False  # Contains dot
        assert parser._is_valid_variable_name("") is False  # Empty
        assert parser._is_valid_variable_name("def") is False  # Python keyword
    
    def test_is_valid_expression(self):
        """Test expression validation."""
        parser = CommentParser()
        
        # Valid expressions
        assert parser._is_valid_expression("values.name") is True
        assert parser._is_valid_expression("values.version | quote") is True
        assert parser._is_valid_expression("config.database.host") is True
        assert parser._is_valid_expression("values.debug | lower") is True
        
        # Invalid expressions
        assert parser._is_valid_expression("") is False
        assert parser._is_valid_expression("  ") is False
        assert parser._is_valid_expression("values.name {{ invalid }}") is False
        assert parser._is_valid_expression("{{ nested }}") is False
    
    def test_parse_file_with_markers(self, temp_dir):
        """Test parsing file with template markers."""
        file_detector = FileTypeDetector()
        parser = CommentParser(file_detector)
        
        # Create test file
        test_file = temp_dir / "test.py"
        content = '''"""Sample Python file."""

# app_name = {{ values.project.name | quote }}
app_name = "DefaultApp"

# version = {{ values.project.version | quote }}
version = "0.1.0"

# Not a template marker
regular_comment = "value"

# api_url = {{ values.api.base_url | quote }}
api_url = "http://localhost:3000"

def function():
    pass
'''
        test_file.write_text(content)
        
        markers = parser.parse_file(test_file)
        
        assert len(markers) == 3
        
        # Check first marker
        marker = markers[0]
        assert marker.variable_name == "app_name"
        assert marker.template_expression == "values.project.name | quote"
        assert marker.line_number == 2
        assert marker.target_line_number == 3
        assert marker.comment_type == "hash"
        assert marker.file_path == test_file
        
        # Check second marker
        marker = markers[1]
        assert marker.variable_name == "version"
        assert marker.template_expression == "values.project.version | quote"
        
        # Check third marker
        marker = markers[2]
        assert marker.variable_name == "api_url"
        assert marker.template_expression == "values.api.base_url | quote"
    
    def test_parse_file_different_comment_types(self, temp_dir):
        """Test parsing files with different comment types."""
        file_detector = FileTypeDetector()
        parser = CommentParser(file_detector)
        
        # JavaScript file
        js_file = temp_dir / "test.js"
        js_content = '''// app_name = {{ values.name | quote }}
const appName = 'default';

// version = {{ values.version }}
const version = '1.0.0';
'''
        js_file.write_text(js_content)
        
        markers = parser.parse_file(js_file)
        assert len(markers) == 2
        assert all(m.comment_type == "double_slash" for m in markers)
        
        # CSS file
        css_file = temp_dir / "test.css"
        css_content = '''/* theme_color = {{ values.theme.primary }} */
.primary { color: #blue; }

/* font_size = {{ values.theme.font_size }} */
body { font-size: 16px; }
'''
        css_file.write_text(css_content)
        
        markers = parser.parse_file(css_file)
        assert len(markers) == 2
        assert all(m.comment_type == "css" for m in markers)
        
        # HTML file
        html_file = temp_dir / "test.html"
        html_content = '''<!DOCTYPE html>
<!-- title = {{ values.app.title | quote }} -->
<title>Default Title</title>

<!-- description = {{ values.app.description | quote }} -->
<meta name="description" content="Default description">
'''
        html_file.write_text(html_content)
        
        markers = parser.parse_file(html_file)
        assert len(markers) == 2
        assert all(m.comment_type == "html" for m in markers)
    
    def test_parse_file_no_markers(self, temp_dir):
        """Test parsing file with no template markers."""
        file_detector = FileTypeDetector()
        parser = CommentParser(file_detector)
        
        test_file = temp_dir / "test.py"
        content = '''"""Regular Python file."""

# Just a regular comment
value = "something"

# Another comment
def function():
    # Comment inside function
    pass
'''
        test_file.write_text(content)
        
        markers = parser.parse_file(test_file)
        assert len(markers) == 0
    
    def test_parse_file_binary_file(self, temp_dir):
        """Test parsing binary file."""
        parser = CommentParser()
        
        # Create binary file
        binary_file = temp_dir / "test.bin"
        binary_file.write_bytes(b'\x00\x01\x02\x03\xff\xfe\xfd')
        
        markers = parser.parse_file(binary_file)
        assert len(markers) == 0
    
    def test_parse_file_not_exists(self):
        """Test parsing non-existent file."""
        parser = CommentParser()
        
        with pytest.raises(FileNotFoundError):
            parser.parse_file(Path("nonexistent.py"))
    
    def test_validate_template_syntax(self):
        """Test Jinja2 template syntax validation."""
        parser = CommentParser()
        
        # Valid syntax
        assert parser.validate_template_syntax("values.name") is True
        assert parser.validate_template_syntax("values.name | quote") is True
        assert parser.validate_template_syntax("values.config.debug | lower") is True
        assert parser.validate_template_syntax("'literal string'") is True
        
        # Invalid syntax
        assert parser.validate_template_syntax("values.name |") is False  # Incomplete filter
        assert parser.validate_template_syntax("{{ nested }}") is False  # Nested braces
        assert parser.validate_template_syntax("values[") is False  # Incomplete bracket
    
    def test_validate_template_syntax_detailed(self):
        """Test detailed template syntax validation."""
        parser = CommentParser()
        
        # Valid syntax
        valid, error = parser.validate_template_syntax_detailed("values.name")
        assert valid is True
        assert error is None
        
        # Invalid syntax
        valid, error = parser.validate_template_syntax_detailed("values.name |")
        assert valid is False
        assert error is not None
        assert "error" in error.lower()
    
    def test_get_marker_statistics(self):
        """Test marker statistics generation."""
        parser = CommentParser()
        
        # Create mock markers
        markers = [
            TemplateMarker(0, "var1", "expr1", "# comment", 1, "hash", None),
            TemplateMarker(2, "var2", "expr2", "// comment", 3, "double_slash", None),
            TemplateMarker(4, "var1", "expr3", "# comment", 5, "hash", None),  # Duplicate var
            TemplateMarker(6, "var3", "expr4", "/* comment */", 7, "css", None),
        ]
        
        stats = parser.get_marker_statistics(markers)
        
        assert stats['total_markers'] == 4
        assert stats['unique_variables'] == 3  # var1, var2, var3
        assert stats['comment_types']['hash'] == 2
        assert stats['comment_types']['double_slash'] == 1
        assert stats['comment_types']['css'] == 1
    
    def test_validate_all_markers(self):
        """Test validation of all markers."""
        parser = CommentParser()
        
        # Create markers with valid and invalid syntax
        markers = [
            TemplateMarker(0, "var1", "values.name", "# comment", 1, "hash", Path("test.py")),
            TemplateMarker(2, "var2", "values.name |", "# comment", 3, "hash", Path("test.py")),  # Invalid
            TemplateMarker(4, "var3", "values.config.debug", "# comment", 5, "hash", Path("test.py")),
        ]
        
        results = parser.validate_all_markers(markers)
        
        assert len(results['valid']) == 2
        assert len(results['invalid']) == 1
        
        # Check valid markers
        assert results['valid'][0]['variable'] == "var1"
        assert results['valid'][1]['variable'] == "var3"
        
        # Check invalid marker
        assert results['invalid'][0]['variable'] == "var2"
        assert 'error' in results['invalid'][0]
    
    def test_comment_type_detection_integration(self, temp_dir):
        """Test integration with FileTypeDetector."""
        file_detector = FileTypeDetector()
        parser = CommentParser(file_detector)
        
        # Test with special filename (Dockerfile)
        dockerfile = temp_dir / "Dockerfile"
        content = '''# base_image = {{ values.docker.base_image }}
FROM ubuntu:20.04

# app_port = {{ values.app.port }}
EXPOSE 8080
'''
        dockerfile.write_text(content)
        
        markers = parser.parse_file(dockerfile)
        assert len(markers) == 2
        assert all(m.comment_type == "hash" for m in markers)
        
        # Test content-based detection for file without extension
        script_file = temp_dir / "script"
        content = '''#!/bin/bash
# script_name = {{ values.script.name }}
SCRIPT_NAME="default"
'''
        script_file.write_text(content)
        
        markers = parser.parse_file(script_file)
        assert len(markers) == 1
        assert markers[0].comment_type == "hash"