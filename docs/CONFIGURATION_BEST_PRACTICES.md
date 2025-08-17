# Configuration Best Practices Guide

## Self-Referencing YAML Values - Best Practices

Template Customizer's self-referencing feature allows you to build complex configurations from simpler values. This guide provides best practices for creating maintainable and reliable configurations.

## 1. Design Principles

### Start with Base Values

Always define your foundational values first, then build complex values from them:

```yaml
# ✅ Good: Clear base values
project:
  name: "ecommerce-api"
  version: "2.1.0"
  environment: "production"
  region: "us-east-1"

# Build complex values from base values
infrastructure:
  cluster_name: "{{ values.project.name }}-{{ values.project.environment }}"
  vpc_name: "{{ values.project.name }}-vpc-{{ values.project.region }}"
```

```yaml
# ❌ Avoid: Complex interdependent values without clear base
database:
  host: "{{ values.api.host }}-db"
api:
  host: "{{ values.project.name }}-{{ values.database.port }}"  # Circular potential
```

### Use Descriptive Names

Make your configuration self-documenting with clear, descriptive names:

```yaml
# ✅ Good: Self-explanatory names
deployment:
  environment: "production"
  aws_region: "us-east-1"
  cluster_name: "{{ values.deployment.environment }}-cluster"
  database_subnet_group: "{{ values.project.name }}-db-subnets-{{ values.deployment.aws_region }}"

# ❌ Avoid: Cryptic abbreviations
deploy:
  env: "prod"
  rgn: "use1"
  cn: "{{ values.deploy.env }}-c"
```

## 2. Organizational Patterns

### Group Related Values

Organize your configuration into logical groups:

```yaml
# Project metadata
project:
  name: "microservice-api"
  version: "1.2.0"
  description: "Customer API microservice"

# Environment configuration
environment:
  name: "production"
  short_name: "prod"
  debug: false

# Infrastructure configuration
infrastructure:
  aws_region: "us-east-1"
  vpc_id: "vpc-12345"
  availability_zones: ["us-east-1a", "us-east-1b", "us-east-1c"]

# Derived infrastructure values
computed_infrastructure:
  cluster_name: "{{ values.project.name }}-{{ values.environment.short_name }}"
  database_name: "{{ values.project.name | replace('-', '_') }}_{{ values.environment.name }}"
  
# Service definitions
services:
  api:
    name: "{{ values.project.name }}-api"
    image: "{{ values.docker.registry }}/{{ values.services.api.name }}:{{ values.project.version }}"
    url: "https://{{ values.services.api.name }}.{{ values.environment.name }}.example.com"

# Docker configuration
docker:
  registry: "123456789012.dkr.ecr.{{ values.infrastructure.aws_region }}.amazonaws.com"
```

### Separate Computed Values

Keep base values separate from computed/derived values for clarity:

```yaml
# Base configuration (manually configured)
base:
  project_name: "ecommerce"
  environment: "prod"
  domain: "example.com"
  version: "2.1.0"

# Computed values (derived from base)
computed:
  app_name: "{{ values.base.project_name }}-app"
  full_domain: "{{ values.base.project_name }}.{{ values.base.environment }}.{{ values.base.domain }}"
  docker_tag: "{{ values.base.version }}-{{ values.base.environment }}"

# Service configurations using computed values
services:
  frontend:
    url: "https://{{ values.computed.full_domain }}"
    image: "registry.com/{{ values.computed.app_name }}:{{ values.computed.docker_tag }}"
```

## 3. Reference Patterns

### Use Filters for Transformations

Leverage Jinja2 filters to transform values appropriately:

```yaml
project:
  name: "My-Awesome-API"
  description: "Customer API Service"

# Use filters for different naming conventions
docker:
  image_name: "{{ values.project.name | lower | replace(' ', '-') | replace('_', '-') }}"
  # Results in: "my-awesome-api"

database:
  name: "{{ values.project.name | lower | replace('-', '_') | replace(' ', '_') }}"
  # Results in: "my_awesome_api"

kubernetes:
  namespace: "{{ values.project.name | lower | replace(' ', '-') | replace('_', '-') | truncate(63) }}"
  # Results in: "my-awesome-api" (valid K8s namespace name)
```

### Chain References Logically

Build complex values step by step:

```yaml
# Step 1: Base values
base:
  domain: "example.com"
  project: "ecommerce"
  environment: "prod"

# Step 2: Intermediate values
intermediate:
  subdomain: "api"
  host: "{{ values.intermediate.subdomain }}.{{ values.base.domain }}"
  
# Step 3: Final values
endpoints:
  api_url: "https://{{ values.intermediate.host }}/v1"
  health_check: "{{ values.endpoints.api_url }}/health"
  metrics: "{{ values.endpoints.api_url }}/metrics"
```

### Type-Aware References

Understand when values will be converted to strings vs. preserving types:

```yaml
# Base values with different types
settings:
  port: 3000              # integer
  debug: true             # boolean
  features: ["auth", "api"] # array
  timeout: 30.5           # float

# Pure references preserve types
server:
  port: "{{ values.settings.port }}"              # Remains integer: 3000
  debug_mode: "{{ values.settings.debug }}"       # Remains boolean: true
  features_list: "{{ values.settings.features }}" # Remains array: ["auth", "api"]

# String interpolation converts to strings
configuration:
  connection_string: "server:{{ values.settings.port }}"           # String: "server:3000"
  debug_message: "Debug mode: {{ values.settings.debug }}"         # String: "Debug mode: True"
  timeout_message: "Timeout: {{ values.settings.timeout }}s"      # String: "Timeout: 30.5s"
```

## 4. Error Prevention

### Avoid Circular References

Design your configuration to prevent circular dependencies:

```yaml
# ✅ Good: Clear dependency direction (base → intermediate → final)
base:
  name: "myapp"
  
intermediate:
  service_name: "{{ values.base.name }}-service"
  
final:
  url: "https://{{ values.intermediate.service_name }}.com"

# ❌ Avoid: Circular dependencies
bad_example:
  a: "{{ values.bad_example.b }}-suffix"
  b: "prefix-{{ values.bad_example.a }}"  # Circular!
```

### Validate Your Configuration

Always test your configuration thoroughly:

```bash
# Test reference resolution
customizer process --config config.yml --verbose --dry-run

# Check for missing references
customizer process --config config.yml --dry-run 2>&1 | grep -i "reference.*not found"

# Verify no circular dependencies
customizer process --config config.yml --dry-run 2>&1 | grep -i "circular"
```

### Use Meaningful Defaults

Provide sensible defaults that work out of the box:

```yaml
# ✅ Good: Sensible defaults
project:
  name: "my-application"
  version: "1.0.0"
  environment: "development"

database:
  host: "{{ values.project.name }}-db.{{ values.project.environment }}.local"
  port: 5432
  name: "{{ values.project.name | replace('-', '_') }}_{{ values.project.environment }}"

# ❌ Avoid: Placeholder values that will cause issues
bad_defaults:
  name: "CHANGE_ME"  # Will result in invalid references
  host: "{{ values.bad_defaults.name }}-server"  # Will be "CHANGE_ME-server"
```

## 5. Environment-Specific Patterns

### Multi-Environment Configuration

Design configurations that work across multiple environments:

```yaml
# Base configuration (environment-agnostic)
project:
  name: "ecommerce-api"
  version: "2.1.0"

# Environment-specific configuration
environment:
  name: "production"        # Change this per environment
  short_name: "prod"        # Change this per environment
  debug: false              # Change this per environment
  replica_count: 3          # Change this per environment

# Computed values (same across environments)
computed:
  cluster_name: "{{ values.project.name }}-{{ values.environment.short_name }}"
  image_tag: "{{ values.project.version }}-{{ values.environment.short_name }}"
  
services:
  api:
    name: "{{ values.project.name }}-api"
    replicas: "{{ values.environment.replica_count }}"
    image: "registry.com/{{ values.services.api.name }}:{{ values.computed.image_tag }}"
```

### Configuration Inheritance Pattern

Use a base configuration with environment overrides:

```yaml
# base-config.yml
project:
  name: "my-microservice"
  version: "1.2.0"

defaults:
  replicas: 1
  debug: true
  resource_limits:
    cpu: "100m"
    memory: "128Mi"

computed:
  service_name: "{{ values.project.name }}-service"
  image: "registry.com/{{ values.computed.service_name }}:{{ values.project.version }}"

# Override in environment-specific configs
deployment:
  replicas: "{{ values.defaults.replicas }}"  # Can be overridden per environment
  debug: "{{ values.defaults.debug }}"        # Can be overridden per environment
```

## 6. Performance Considerations

### Minimize Deep Nesting

While deep reference chains work, they can impact readability and performance:

```yaml
# ✅ Good: Reasonable depth
project:
  name: "myapp"
  
service:
  name: "{{ values.project.name }}-api"
  
endpoint:
  url: "https://{{ values.service.name }}.com"

# ⚠️ Acceptable but less ideal: Very deep chains
deep:
  level1: "base"
  level2: "{{ values.deep.level1 }}-l2"
  level3: "{{ values.deep.level2 }}-l3"
  level4: "{{ values.deep.level3 }}-l4"
  level5: "{{ values.deep.level4 }}-l5"  # Getting too complex
```

### Cache Frequently Used Values

For complex computations used multiple times, compute once and reference:

```yaml
# ✅ Good: Compute once, reference multiple times
computed:
  full_service_name: "{{ values.project.name }}-{{ values.environment.name }}-service"
  
services:
  api:
    name: "{{ values.computed.full_service_name }}-api"
    image: "registry.com/{{ values.computed.full_service_name }}-api:latest"
    
  worker:
    name: "{{ values.computed.full_service_name }}-worker"
    image: "registry.com/{{ values.computed.full_service_name }}-worker:latest"

# ❌ Avoid: Repeating complex computations
bad_services:
  api:
    name: "{{ values.project.name }}-{{ values.environment.name }}-service-api"
    image: "registry.com/{{ values.project.name }}-{{ values.environment.name }}-service-api:latest"
    
  worker:
    name: "{{ values.project.name }}-{{ values.environment.name }}-service-worker"
    image: "registry.com/{{ values.project.name }}-{{ values.environment.name }}-service-worker:latest"
```

## 7. Common Anti-Patterns

### Avoid These Mistakes

#### 1. Circular Dependencies
```yaml
# ❌ Don't do this
a: "{{ values.b }}-suffix"
b: "prefix-{{ values.a }}"
```

#### 2. Overly Complex Filters
```yaml
# ❌ Too complex
name: "{{ values.project.title | lower | replace(' ', '-') | replace('_', '-') | truncate(50) | trim('-') | default('fallback') }}"

# ✅ Better: Break into steps
intermediate:
  clean_name: "{{ values.project.title | lower | replace(' ', '-') | replace('_', '-') }}"
  truncated_name: "{{ values.intermediate.clean_name | truncate(50) }}"

final:
  name: "{{ values.intermediate.truncated_name | trim('-') | default('fallback') }}"
```

#### 3. Missing Base Values
```yaml
# ❌ References without bases
service:
  url: "https://{{ values.api.host }}/{{ values.api.path }}"
# Missing: Where are api.host and api.path defined?

# ✅ Clear base values
api:
  host: "api.example.com"
  path: "v1"
  
service:
  url: "https://{{ values.api.host }}/{{ values.api.path }}"
```

## 8. Debugging and Troubleshooting

### Use Verbose Mode

Enable verbose output to see resolution details:

```bash
customizer process --config config.yml --verbose --dry-run
```

Output will show:
```
🔄 Resolving self-references in configuration...
  📊 Built dependency graph with 12 nodes
     services.api.image depends on: docker.registry, services.api.name, project.version
     services.api.name depends on: project.name
  📋 Resolution order: project.name → docker.registry → services.api.name → services.api.image
  ✅ Resolution completed in 2 iteration(s)
```

### Test Incrementally

Build your configuration incrementally and test at each step:

```yaml
# Step 1: Test basic values
project:
  name: "myapp"
# Test: customizer process --dry-run

# Step 2: Add simple references
docker:
  image: "{{ values.project.name }}:latest"
# Test: customizer process --dry-run

# Step 3: Add complex references
service:
  url: "https://{{ values.project.name }}.example.com"
# Test: customizer process --dry-run
```

### Validate Syntax

Use tools to validate your YAML and template syntax:

```bash
# Validate YAML syntax
python3 -c "import yaml; yaml.safe_load(open('config.yml'))"

# Validate Jinja2 templates
python3 -c "
import yaml
from jinja2 import Template
config = yaml.safe_load(open('config.yml'))

def validate_templates(obj, path=''):
    if isinstance(obj, dict):
        for k, v in obj.items():
            validate_templates(v, f'{path}.{k}' if path else k)
    elif isinstance(obj, str) and '{{' in obj:
        try:
            Template(obj)
            print(f'✓ {path}: {obj}')
        except Exception as e:
            print(f'✗ {path}: {obj} - ERROR: {e}')

validate_templates(config)
"
```

## 9. Migration Strategy

### Converting Existing Configurations

When adding self-references to existing configurations:

1. **Identify Repeated Values**:
   ```bash
   # Find duplicate values in your config
   grep -o '"[^"]*"' config.yml | sort | uniq -c | sort -nr | head -10
   ```

2. **Extract to Base Values**:
   ```yaml
   # Before
   services:
     api:
       image: "myapp:v1.2.0"
     worker:
       image: "myapp:v1.2.0"
   
   # After
   project:
     name: "myapp"
     version: "v1.2.0"
   
   services:
     api:
       image: "{{ values.project.name }}:{{ values.project.version }}"
     worker:
       image: "{{ values.project.name }}:{{ values.project.version }}"
   ```

3. **Test Thoroughly**:
   ```bash
   # Test old config works
   cp config.yml config.yml.backup
   customizer process --config config.yml.backup --dry-run
   
   # Test new config produces same results
   customizer process --config config.yml --dry-run
   
   # Compare outputs
   diff output_old output_new
   ```

## 10. Example: Complete Production Configuration

Here's a complete example following all best practices:

```yaml
# Production-ready configuration with self-references
# File: production-config.yml

# ============================================================================
# BASE CONFIGURATION (manually set per environment)
# ============================================================================
meta:
  config_version: "1.0"
  environment: "production"

project:
  name: "ecommerce-platform"
  version: "2.1.0"
  description: "E-commerce microservices platform"

deployment:
  environment: "production"
  short_env: "prod"
  region: "us-east-1"
  domain: "ecommerce.company.com"

# ============================================================================
# COMPUTED VALUES (derived from base configuration)
# ============================================================================
computed:
  # Naming conventions
  app_prefix: "{{ values.project.name }}-{{ values.deployment.short_env }}"
  db_name: "{{ values.project.name | replace('-', '_') }}_{{ values.deployment.environment }}"
  
  # Infrastructure names
  cluster_name: "{{ values.computed.app_prefix }}-cluster"
  vpc_name: "{{ values.computed.app_prefix }}-vpc"
  
  # Image tagging
  image_tag: "{{ values.project.version }}-{{ values.deployment.short_env }}"

# ============================================================================
# INFRASTRUCTURE CONFIGURATION
# ============================================================================
aws:
  account_id: "123456789012"
  region: "{{ values.deployment.region }}"
  
infrastructure:
  vpc_id: "vpc-12345"
  cluster_name: "{{ values.computed.cluster_name }}"
  ecr_registry: "{{ values.aws.account_id }}.dkr.ecr.{{ values.aws.region }}.amazonaws.com"

# ============================================================================
# SERVICE DEFINITIONS
# ============================================================================
services:
  api:
    name: "{{ values.computed.app_prefix }}-api"
    port: 8080
    replicas: 3
    image: "{{ values.infrastructure.ecr_registry }}/{{ values.services.api.name }}:{{ values.computed.image_tag }}"
    url: "https://api.{{ values.deployment.domain }}"
    health_check: "{{ values.services.api.url }}/health"
    
  frontend:
    name: "{{ values.computed.app_prefix }}-web"
    port: 3000
    replicas: 2
    image: "{{ values.infrastructure.ecr_registry }}/{{ values.services.frontend.name }}:{{ values.computed.image_tag }}"
    url: "https://{{ values.deployment.domain }}"
    
  worker:
    name: "{{ values.computed.app_prefix }}-worker"
    replicas: 2
    image: "{{ values.infrastructure.ecr_registry }}/{{ values.services.worker.name }}:{{ values.computed.image_tag }}"

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================
database:
  host: "{{ values.computed.app_prefix }}.cluster-xyz.{{ values.aws.region }}.rds.amazonaws.com"
  name: "{{ values.computed.db_name }}"
  port: 5432
  connection_string: "postgresql://app:secret@{{ values.database.host }}:{{ values.database.port }}/{{ values.database.name }}"

# ============================================================================
# MONITORING AND OBSERVABILITY
# ============================================================================
monitoring:
  namespace: "{{ values.project.name }}/{{ values.deployment.environment }}"
  
  alerts:
    api_health: "{{ values.services.api.health_check }}"
    frontend_health: "{{ values.services.frontend.url }}/health"
    
  dashboards:
    api_metrics: "{{ values.services.api.url }}/metrics"
    cluster_status: "https://monitoring.{{ values.deployment.domain }}/cluster/{{ values.infrastructure.cluster_name }}"

# ============================================================================
# EXTERNAL INTEGRATIONS
# ============================================================================
external:
  cdn:
    url: "https://cdn.{{ values.deployment.domain }}"
    static_assets: "{{ values.external.cdn.url }}/static/{{ values.project.version }}"
    
  backup:
    bucket: "{{ values.computed.app_prefix }}-backups"
    path: "database/{{ values.database.name }}"
```

This configuration demonstrates all the best practices:
- Clear separation of base and computed values
- Logical grouping and organization
- Consistent naming conventions
- No circular dependencies
- Meaningful defaults
- Comprehensive but not overly complex