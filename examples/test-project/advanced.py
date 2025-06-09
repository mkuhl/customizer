"""Advanced Python file with various template marker styles."""

# app_name = {{ values.project.name | quote }}
APP_NAME = "DefaultApp"

# version: {{ values.project.version | quote }}  
VERSION = "0.1.0"

# "database_url" = {{ values.database.url | quote }}
DATABASE_URL = "sqlite:///default.db"

# Enable debug mode
# debug_enabled = {{ values.features.debug }}
DEBUG_ENABLED = True

class Config:
    # host = {{ values.server.host | quote }}
    HOST = "localhost"
    
    # port = {{ values.server.port }}
    PORT = 8000

# Test alternative syntax
# timeout: {{ values.settings.timeout }}
TIMEOUT = 30

def get_settings():
    return {
        "app": APP_NAME,
        "version": VERSION,
        "debug": DEBUG_ENABLED
    }