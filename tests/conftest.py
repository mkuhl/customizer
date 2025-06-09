"""Test configuration and fixtures."""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_config():
    """Sample configuration parameters for testing."""
    return {
        "project": {
            "name": "TestApp",
            "version": "1.0.0",
            "description": "A test application"
        },
        "api": {
            "base_url": "https://api.testapp.com",
            "version": "v1"
        },
        "docker": {
            "registry": "testregistry.com",
            "image_name": "testapp"
        }
    }


@pytest.fixture
def sample_python_file():
    """Sample Python file content with template markers."""
    return '''"""Sample Python module."""

# app_name = {{ values.project.name | quote }}
app_name = "DefaultApp"

# version = {{ values.project.version | quote }}
version = "0.0.1"

# api_url = {{ values.api.base_url | quote }}
api_url = "http://localhost:3000"

def get_config():
    return {
        "name": app_name,
        "version": version,
        "api_url": api_url
    }
'''


@pytest.fixture
def sample_js_file():
    """Sample JavaScript file content with template markers."""
    return '''// Sample JavaScript module

// appName = {{ values.project.name | quote }}
const appName = 'DefaultApp';

// apiUrl = {{ values.api.base_url | quote }}
const apiUrl = 'http://localhost:3000';

export { appName, apiUrl };
'''


@pytest.fixture
def sample_yaml_file():
    """Sample YAML file content with template markers."""
    return '''# Sample configuration file

# name: {{ values.project.name | quote }}
name: "DefaultApp"

# version: {{ values.project.version | quote }}
version: "0.0.1"

api:
  # base_url: {{ values.api.base_url | quote }}
  base_url: "http://localhost:3000"
'''