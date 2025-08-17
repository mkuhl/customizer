# Template Customizer - Limitations and Constraints

This document outlines the current limitations and constraints of Template Customizer, especially regarding the self-referencing YAML values feature introduced in v0.4.0.

## Self-Referencing Configuration Limitations (v0.4.0+)

### 1. Reference Resolution Constraints

#### Maximum Recursion Depth
- **Limit**: 10 levels of nested references by default
- **Behavior**: Prevents infinite recursion and stack overflow
- **Workaround**: Flatten reference chains or use intermediate computed values

```yaml
# ❌ Will fail - too deep
level_10: "{{ values.level_9 }}-suffix"
level_9: "{{ values.level_8 }}-suffix"
# ... (10+ levels)

# ✅ Better approach
base:
  prefix: "myapp"
computed:
  service_name: "{{ values.base.prefix }}-service"
services:
  api: "{{ values.computed.service_name }}-api"
  worker: "{{ values.computed.service_name }}-worker"
```

#### Circular Dependency Detection
- **Constraint**: No circular references allowed
- **Detection**: Comprehensive cycle detection using DFS
- **Error**: Clear error messages with dependency path

```yaml
# ❌ Circular dependency - will fail
service_a: "{{ values.service_b }}-api"
service_b: "{{ values.service_c }}-backend"
service_c: "{{ values.service_a }}-frontend"

# ✅ Linear dependency chain
base: "myapp"
api: "{{ values.base }}-api"
frontend: "{{ values.base }}-frontend"
```

### 2. Template Syntax Limitations

#### Jinja2 Compatibility
- **Constraint**: Only standard Jinja2 features are supported
- **Limitation**: Custom Jinja2 extensions are not available
- **Available Filters**: Built-in Jinja2 filters only (lower, upper, replace, etc.)

```yaml
# ✅ Supported
name: "{{ values.project.title | lower | replace(' ', '-') }}"

# ❌ Custom filters not available
name: "{{ values.project.title | custom_filter }}"
```

#### Template Context
- **Constraint**: Only `values` namespace is available in references
- **Limitation**: No access to environment variables or external data
- **Scope**: References can only access other configuration values

```yaml
# ✅ Supported - referencing config values
api_url: "{{ values.project.name }}.example.com"

# ❌ Not supported - environment variables
api_url: "{{ env.API_HOST | default('localhost') }}"

# ❌ Not supported - external functions
timestamp: "{{ now() }}"
```

### 3. Data Type Constraints

#### Type Preservation
- **Pure References**: Types preserved (strings, numbers, booleans, lists)
- **String Interpolation**: Always converts to string
- **Mixed Types**: Complex objects (dicts) cannot be directly referenced

```yaml
settings:
  port: 3000              # integer
  debug: true             # boolean
  features: ["auth", "api"] # array

# ✅ Type preserved
server_port: "{{ values.settings.port }}"        # Remains integer: 3000
debug_mode: "{{ values.settings.debug }}"        # Remains boolean: true

# ✅ Converts to string
connection: "Port: {{ values.settings.port }}"   # String: "Port: 3000"

# ❌ Cannot reference complex objects directly
config: "{{ values.settings }}"  # Will fail - cannot reference entire dict
```

#### Nested Object Access
- **Constraint**: Can only access leaf values (strings, numbers, booleans, arrays)
- **Limitation**: Cannot reference intermediate dictionary objects
- **Workaround**: Reference specific fields within nested objects

```yaml
database:
  connection:
    host: "localhost"
    port: 5432
    credentials:
      username: "user"
      password: "pass"

# ✅ Accessing leaf values
db_host: "{{ values.database.connection.host }}"
db_user: "{{ values.database.connection.credentials.username }}"

# ❌ Cannot reference intermediate objects
db_config: "{{ values.database.connection }}"        # Will fail
credentials: "{{ values.database.connection.credentials }}"  # Will fail
```

### 4. Performance Limitations

#### Configuration Size
- **Practical Limit**: ~1000 configuration keys with references
- **Performance Impact**: Linear scaling with number of references
- **Memory Usage**: All references resolved in memory

#### Reference Complexity
- **Dependency Graph**: O(n²) worst-case for dependency analysis
- **Resolution Time**: Increases with reference chain depth
- **Recommendation**: Keep reference chains under 5 levels deep

```yaml
# ✅ Efficient - simple reference structure
project: { name: "app", version: "1.0" }
docker: { image: "{{ values.project.name }}:{{ values.project.version }}" }

# ⚠️ Less efficient - complex dependency web
computed_a: "{{ values.base_a }}-{{ values.base_b }}"
computed_b: "{{ values.computed_a }}-{{ values.base_c }}"
computed_c: "{{ values.computed_b }}-{{ values.computed_a }}"
# ... (many cross-references)
```

## Template Processing Limitations

### 1. File Format Constraints

#### Supported Comment Syntax
- **Limitation**: Only predefined comment styles supported
- **File Types**: Python, JavaScript, CSS, HTML, YAML, Dockerfile, Shell
- **Custom Syntax**: Cannot define custom comment patterns

```python
# ✅ Supported - Python style
# variable = {{ values.expression }}
value = "default"

# ❌ Not supported - custom syntax
/* variable = {{ values.expression }} */  # In Python file
```

#### Binary File Limitation
- **Constraint**: Only text files are processed
- **Excluded**: Images, executables, archives, databases
- **Workaround**: Use external tools for binary file customization

### 2. Template Marker Constraints

#### Line-Based Processing
- **Constraint**: Markers must be on separate lines
- **Limitation**: Cannot have multiple markers per line
- **Requirement**: Marker comment must immediately precede target line

```python
# ✅ Correct format
# app_name = {{ values.project.name }}
app_name = "default"

# ❌ Not supported - same line
app_name = "default"  # app_name = {{ values.project.name }}

# ❌ Not supported - separated lines
# app_name = {{ values.project.name }}

app_name = "default"  # Empty line breaks association
```

#### Variable Name Matching
- **Constraint**: Variable names must match exactly
- **Case Sensitive**: Names are case-sensitive
- **Special Characters**: Limited to alphanumeric and underscore

```python
# ✅ Exact match
# app_name = {{ values.project.name }}
app_name = "default"

# ❌ Case mismatch
# app_name = {{ values.project.name }}
App_Name = "default"  # Won't match

# ❌ Special characters
# app-name = {{ values.project.name }}  # Hyphen not supported in variable names
```

### 3. External Replacements Limitations

#### JSONPath Constraints
- **Library Dependency**: Uses jsonpath-ng implementation
- **Feature Subset**: Not all JSONPath features may be available
- **Error Handling**: Invalid JSONPath expressions cause processing failure

```yaml
# ✅ Standard JSONPath
replacements:
  json:
    "package.json":
      "$.name": "{{ values.project.name }}"
      "$.dependencies.react": "^18.0.0"

# ⚠️ Advanced features may not work
replacements:
  json:
    "package.json":
      "$..name": "value"  # Recursive descent - may not work as expected
```

#### Markdown Pattern Limitations
- **Regex Engine**: Uses Python's re module
- **Performance**: Complex patterns can be slow on large files
- **Error Handling**: Invalid regex patterns cause processing failure

## Configuration File Limitations

### 1. File Format Support
- **YAML**: Fully supported (recommended)
- **JSON**: Fully supported
- **Other Formats**: TOML, XML, INI not supported

### 2. Configuration Size
- **Memory Limitation**: Entire configuration loaded into memory
- **File Size**: Practical limit ~10MB for YAML files
- **Parsing**: Large files may impact startup performance

### 3. Encoding Support
- **UTF-8**: Fully supported
- **Other Encodings**: Limited support, may cause issues
- **BOM**: Byte Order Mark not supported

## Platform and Environment Limitations

### 1. Operating System Support
- **Native Binary**: Linux x86_64 only
- **GLIBC Requirement**: GLIBC 2.31+ required
- **Docker Fallback**: Available for other platforms

### 2. Python Version Requirements
- **Minimum**: Python 3.8+
- **Testing**: Tested on Python 3.8, 3.9, 3.10, 3.11
- **Dependencies**: Specific version requirements for Jinja2, PyYAML, Click

### 3. File System Limitations
- **Path Length**: Limited by OS (typically 260 chars on Windows, 4096 on Linux)
- **Special Characters**: Some special characters in filenames may cause issues
- **Symbolic Links**: May not handle symbolic links correctly in all cases

## Performance Considerations

### 1. Processing Speed
- **Small Projects**: < 100 files - Very fast (< 1 second)
- **Medium Projects**: 100-1000 files - Fast (1-5 seconds)
- **Large Projects**: > 1000 files - May be slower (5-30 seconds)

### 2. Memory Usage
- **Base Memory**: ~50MB for the application
- **Per File**: ~1KB additional memory per processed file
- **Configuration**: Additional memory proportional to config size

### 3. Disk I/O
- **Backup Files**: Creates .bak files unless disabled
- **Temporary Files**: May create temporary files during processing
- **Concurrent Access**: Not designed for concurrent processing

## Security Limitations

### 1. Template Execution
- **Sandboxing**: Limited Jinja2 sandboxing in place
- **Code Execution**: Templates cannot execute arbitrary code
- **File Access**: Templates cannot access file system

### 2. Configuration Validation
- **Input Validation**: Basic validation of configuration structure
- **Content Validation**: Limited validation of configuration values
- **Injection Prevention**: Basic protection against template injection

## Workarounds and Alternatives

### 1. For Unsupported File Types
- **External Tools**: Use sed, awk, or other text processing tools
- **Preprocessing**: Convert files to supported formats
- **Custom Scripts**: Write custom processing scripts

### 2. For Complex References
- **Intermediate Values**: Use computed intermediate values
- **Multiple Passes**: Run customizer multiple times
- **External Processing**: Use external template engines for complex logic

### 3. For Performance Issues
- **File Filtering**: Use --include/--exclude patterns
- **Batch Processing**: Process files in smaller batches
- **Caching**: Cache resolved configurations for repeated use

## Future Improvements

### Planned Enhancements
- Support for additional file formats (TOML, XML)
- Enhanced JSONPath feature support
- Improved performance for large projects
- Cross-platform native binaries
- Advanced template features

### Community Contributions
- Feature requests welcome via GitHub Issues
- Performance improvements and optimizations
- Additional file type support
- Documentation improvements

## Getting Help

If you encounter limitations not documented here:

1. **Check GitHub Issues**: [https://github.com/mkuhl/customizer/issues](https://github.com/mkuhl/customizer/issues)
2. **Review Documentation**: Check docs/ directory for additional information
3. **Create Feature Request**: For new functionality needs
4. **Community Discussion**: For workarounds and alternative approaches

## Version History

- **v0.4.0**: Self-referencing configuration values
- **v0.3.0**: External replacements (JSON/Markdown)
- **v0.2.0**: Enhanced CLI and file type support
- **v0.1.0**: Initial release with basic template processing