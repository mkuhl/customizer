"""Sample configuration file with template markers."""

# app_name = {{ values.project.name | quote }}
app_name = "DefaultApp"

# version = {{ values.project.version | quote }}  
version = "0.1.0"

# api_base_url = {{ values.api.base_url | quote }}
api_base_url = "http://localhost:3000"

# debug_mode = {{ values.features.debug }}
debug_mode = True

def get_config():
    """Get application configuration."""
    return {
        "name": app_name,
        "version": version,
        "api_url": api_base_url,
        "debug": debug_mode
    }