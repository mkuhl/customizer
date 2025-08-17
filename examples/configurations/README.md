# Template Customizer Configuration Examples

This directory contains example configuration files demonstrating the self-referencing YAML values feature introduced in Template Customizer v0.4.0.

## Available Examples

### 1. Basic Example (`basic-example.yml`)

**Best for**: Learning the fundamentals of self-referencing values

**Features demonstrated**:
- Simple references using `{{ values.path.to.value }}`
- Jinja2 filters (upper, lower, replace, title)
- Type preservation vs string interpolation
- Chained references
- External replacements for JSON/Markdown

**Use case**: Small projects, learning, simple applications

### 2. Microservice Configuration (`microservice-config.yml`)

**Best for**: Production microservice deployments

**Features demonstrated**:
- Complex dependency graphs
- AWS infrastructure naming patterns
- Service discovery and networking
- Environment-specific configurations
- Monitoring and observability setup
- Security and IAM configurations

**Use case**: Production microservices, cloud deployments, enterprise applications

### 3. Kubernetes/Helm Configuration (`kubernetes-config.yml`)

**Best for**: Kubernetes and Helm chart deployments

**Features demonstrated**:
- Helm-style values organization
- Kubernetes resource naming conventions
- Service mesh integration (Istio)
- Persistent volumes and storage
- Network policies and security
- Autoscaling configuration

**Use case**: Kubernetes deployments, Helm charts, container orchestration

### 4. Docker Compose Configuration (`docker-compose-config.yml`)

**Best for**: Local development with Docker Compose

**Features demonstrated**:
- Multi-service application setup
- Container networking and communication
- Volume and storage management
- Environment-specific configurations
- Health checks and monitoring
- Development workflow optimization

**Use case**: Local development, Docker Compose stacks, development environments

## How to Use These Examples

### 1. Copy and Customize

```bash
# Copy an example to your project
cp examples/configurations/basic-example.yml my-project/config.yml

# Edit the configuration for your needs
vim my-project/config.yml

# Test the configuration
customizer process --project my-project --config my-project/config.yml --dry-run
```

### 2. Test Reference Resolution

```bash
# See how references are resolved
customizer process --config basic-example.yml --verbose --dry-run

# Check for circular dependencies
customizer process --config microservice-config.yml --dry-run 2>&1 | grep -i "circular"

# Disable reference resolution for comparison
customizer process --config kubernetes-config.yml --no-resolve-refs --dry-run
```

### 3. Validate Configuration

```bash
# Validate YAML syntax
python3 -c "import yaml; yaml.safe_load(open('basic-example.yml'))"

# Validate Jinja2 templates in references
python3 -c "
import yaml
from jinja2 import Template
config = yaml.safe_load(open('basic-example.yml'))

def check_templates(obj, path=''):
    if isinstance(obj, dict):
        for k, v in obj.items():
            check_templates(v, f'{path}.{k}' if path else k)
    elif isinstance(obj, str) and '{{' in obj:
        try:
            Template(obj)
            print(f'✓ {path}: {obj}')
        except Exception as e:
            print(f'✗ {path}: {obj} - ERROR: {e}')

check_templates(config)
"
```

## Configuration Patterns Explained

### Pattern 1: Base + Computed Values

```yaml
# Define base values once
project:
  name: "my-app"
  version: "1.0.0"

# Build complex values from base
computed:
  full_name: "{{ values.project.name }}-{{ values.project.version }}"
  db_name: "{{ values.project.name | replace('-', '_') }}_db"
```

**Benefits**: Single source of truth, consistent naming, easy updates

### Pattern 2: Environment-Specific References

```yaml
# Environment configuration
environment:
  name: "production"
  short: "prod"

# Resources using environment
database:
  host: "{{ values.project.name }}-{{ values.environment.short }}.cluster.amazonaws.com"
  name: "{{ values.project.name | replace('-', '_') }}_{{ values.environment.name }}"
```

**Benefits**: Easy environment switching, consistent resource naming

### Pattern 3: Service Discovery

```yaml
# Service definitions
services:
  api:
    name: "my-app-api"
    port: 8080
  frontend:
    name: "my-app-frontend" 
    port: 3000

# Inter-service communication
frontend:
  api_url: "http://{{ values.services.api.name }}:{{ values.services.api.port }}"
```

**Benefits**: Centralized service configuration, automatic URL generation

### Pattern 4: Infrastructure as Code

```yaml
# AWS account and region
aws:
  account_id: "123456789012"
  region: "us-east-1"

# Computed AWS resources
infrastructure:
  ecr_registry: "{{ values.aws.account_id }}.dkr.ecr.{{ values.aws.region }}.amazonaws.com"
  vpc_name: "{{ values.project.name }}-vpc"
  cluster_name: "{{ values.project.name }}-cluster"
```

**Benefits**: Consistent AWS resource naming, region-aware configurations

## Best Practices Demonstrated

### 1. Logical Organization

- **Base values first**: Define foundational values at the top
- **Computed values**: Group derived values in dedicated sections
- **Clear naming**: Use descriptive names for all configuration keys

### 2. Type Awareness

```yaml
settings:
  port: 3000              # Number
  debug: true             # Boolean
  
server:
  port: "{{ values.settings.port }}"        # Preserves number type
  status: "Port: {{ values.settings.port }}" # Becomes string
```

### 3. Error Prevention

- **Avoid circular references**: Design clear dependency hierarchies
- **Use meaningful defaults**: Provide sensible fallback values
- **Test incrementally**: Add references gradually and test each step

### 4. Documentation

- **Comment complex references**: Explain non-obvious transformations
- **Group related values**: Organize configuration logically
- **Show expected results**: Include comments showing resolved values

## Troubleshooting Examples

### Common Issues and Solutions

#### Issue: Circular Dependency

```yaml
# ❌ This creates a circular dependency
service_a: "{{ values.service_b }}-api"
service_b: "{{ values.service_a }}-backend"

# ✅ Fix by making one value independent
base_name: "myapp"
service_a: "{{ values.base_name }}-api"
service_b: "{{ values.base_name }}-backend"
```

#### Issue: Missing Reference

```yaml
# ❌ This references a non-existent value
api_url: "{{ values.missing.reference }}"

# ✅ Fix by adding the missing section
missing:
  reference: "https://api.example.com"
api_url: "{{ values.missing.reference }}"
```

#### Issue: Complex Filter Chain

```yaml
# ❌ Too complex in one step
name: "{{ values.project.title | lower | replace(' ', '-') | replace('_', '-') | truncate(50) }}"

# ✅ Break into multiple steps
intermediate:
  clean_name: "{{ values.project.title | lower | replace(' ', '-') | replace('_', '-') }}"
final:
  name: "{{ values.intermediate.clean_name | truncate(50) }}"
```

## Next Steps

1. **Start with basic-example.yml** to understand the fundamentals
2. **Choose the example** that best matches your use case
3. **Customize gradually** - add references incrementally
4. **Test frequently** with `--dry-run` and `--verbose` flags
5. **Validate regularly** using the validation scripts above

For more information:
- **[Configuration Best Practices](../CONFIGURATION_BEST_PRACTICES.md)** - Detailed patterns and recommendations
- **[Troubleshooting Guide](../TROUBLESHOOTING.md)** - Common issues and solutions
- **[Migration Guide](../MIGRATION.md)** - Upgrading from older versions
- **[Usage Guide](../USAGE.md)** - Detailed usage examples