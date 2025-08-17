# Migration Guide - Template Customizer v0.4.0

This guide helps existing Template Customizer users migrate to v0.4.0, which introduces **self-referencing configuration values**. All existing functionality remains compatible, but new features can significantly improve your configuration management.

## What's New in v0.4.0

### 🔗 Self-Referencing Configuration Values

The major new feature allows you to reference other values within your configuration files using `{{ values.path.to.value }}` syntax, enabling:

- **Elimination of duplication** - Define values once, reference everywhere
- **Dynamic value composition** - Build complex values from simpler components  
- **Consistent naming** - Maintain consistency across related configurations
- **Template-like configs** - Apply template logic within configuration files

## Compatibility Statement

### ✅ 100% Backward Compatible

**Your existing configurations and workflows will continue to work exactly as before.**

- All existing template markers continue to work unchanged
- All CLI options remain the same (new ones added)
- All file types and comment syntaxes remain supported
- No breaking changes to APIs or behavior

### 🆕 Opt-In Enhancement

Self-referencing is automatically enabled but can be disabled for compatibility:

```bash
# New behavior (default) - with self-reference resolution
customizer process --project ./template --config ./config.yml

# Legacy behavior - disable self-reference resolution  
customizer process --project ./template --config ./config.yml --no-resolve-refs
```

## Migration Strategies

### Strategy 1: No Migration Required (Continue As-Is)

**Best for**: Users satisfied with current functionality

**Approach**: Continue using Template Customizer exactly as before. The new features are optional and don't affect existing workflows.

**Example - Your existing config continues to work:**
```yaml
# config.yml (v0.3.x style - still works perfectly)
project:
  name: "MyApp"
  version: "1.2.0"

database:
  host: "prod-db.example.com"
  port: 5432

docker:
  registry: "ghcr.io"
  image_name: "myapp"
  tag: "latest"
```

### Strategy 2: Gradual Enhancement (Recommended)

**Best for**: Users who want to improve their configurations incrementally

**Approach**: Gradually add self-references to eliminate duplication and improve maintainability.

#### Step 1: Identify Duplication
```bash
# Find repeated values in your configuration
grep -o '"[^"]*"' config.yml | sort | uniq -c | sort -nr | head -10
```

#### Step 2: Extract Base Values
```yaml
# Before (v0.3.x style)
project:
  name: "ecommerce-api"
  version: "2.1.0"

database:
  name: "ecommerce_api_production"
  host: "ecommerce-api-prod.cluster.amazonaws.com"

docker:
  image: "ghcr.io/company/ecommerce-api:2.1.0"

api:
  base_url: "https://ecommerce-api.production.company.com"

# After (v0.4.0 with self-references)
project:
  name: "ecommerce-api"
  version: "2.1.0"
  environment: "production"

database:
  name: "{{ values.project.name | replace('-', '_') }}_{{ values.project.environment }}"
  host: "{{ values.project.name }}-{{ values.project.environment[:4] }}.cluster.amazonaws.com"

docker:
  registry: "ghcr.io/company"
  image: "{{ values.docker.registry }}/{{ values.project.name }}:{{ values.project.version }}"

api:
  base_url: "https://{{ values.project.name }}.{{ values.project.environment }}.company.com"
```

#### Step 3: Test Incrementally
```bash
# Test each addition
customizer process --config config.yml --verbose --dry-run

# Verify resolution works correctly
customizer process --config config.yml --dry-run | grep "Found.*changes"
```

### Strategy 3: Full Modernization

**Best for**: Users starting new projects or doing major configuration overhauls

**Approach**: Redesign configuration to fully leverage self-referencing capabilities.

#### Modern Configuration Pattern
```yaml
# config.yml (v0.4.0 modern pattern)

# ============================================================================
# BASE CONFIGURATION (Define once)
# ============================================================================
meta:
  environment: "production"
  region: "us-east-1"
  company: "acme"

project:
  name: "ecommerce-platform"
  version: "3.2.1"
  description: "E-commerce microservices platform"

# ============================================================================  
# COMPUTED VALUES (Build from base)
# ============================================================================
computed:
  # Naming conventions
  env_short: "{{ values.meta.environment[:4] }}"  # "prod"
  app_prefix: "{{ values.project.name }}-{{ values.computed.env_short }}"
  
  # Infrastructure names
  cluster_name: "{{ values.computed.app_prefix }}-cluster"
  vpc_name: "{{ values.computed.app_prefix }}-vpc"

# ============================================================================
# INFRASTRUCTURE (Use computed values)
# ============================================================================
aws:
  account_id: "123456789012"
  region: "{{ values.meta.region }}"
  ecr_registry: "{{ values.aws.account_id }}.dkr.ecr.{{ values.aws.region }}.amazonaws.com"

# ============================================================================
# SERVICES (Dynamic configuration)
# ============================================================================
services:
  api:
    name: "{{ values.computed.app_prefix }}-api"
    port: 8080
    image: "{{ values.aws.ecr_registry }}/{{ values.services.api.name }}:{{ values.project.version }}"
    url: "https://{{ values.services.api.name }}.{{ values.meta.company }}.com"
    
  frontend:
    name: "{{ values.computed.app_prefix }}-web"
    port: 3000
    image: "{{ values.aws.ecr_registry }}/{{ values.services.frontend.name }}:{{ values.project.version }}"
    url: "https://{{ values.services.frontend.name }}.{{ values.meta.company }}.com"

# ============================================================================
# DATABASE (Consistent naming)
# ============================================================================
database:
  host: "{{ values.computed.app_prefix }}.cluster-xyz.{{ values.aws.region }}.rds.amazonaws.com"
  name: "{{ values.project.name | replace('-', '_') }}_{{ values.meta.environment }}"
  port: 5432

# ============================================================================
# MONITORING (Reference other services)
# ============================================================================
monitoring:
  namespace: "{{ values.project.name }}/{{ values.meta.environment }}"
  alerts:
    api_health: "{{ values.services.api.url }}/health"
    frontend_health: "{{ values.services.frontend.url }}/health"
```

## Common Migration Patterns

### Pattern 1: Environment-Specific Configurations

#### Before (Multiple Config Files)
```bash
# Separate files for each environment
config-dev.yml
config-staging.yml  
config-prod.yml

# Lots of duplication between files
```

#### After (Single Template Config)
```yaml
# config-template.yml
environment:
  name: "REPLACE_WITH_ENV"  # dev, staging, prod
  short: "REPLACE_WITH_SHORT"  # dev, stg, prod

project:
  name: "my-microservice"
  version: "1.2.0"

# Everything else builds from these base values
database:
  host: "{{ values.project.name }}-{{ values.environment.short }}.cluster.amazonaws.com"
  name: "{{ values.project.name | replace('-', '_') }}_{{ values.environment.name }}"

# Generate environment-specific configs
# sed 's/REPLACE_WITH_ENV/production/g; s/REPLACE_WITH_SHORT/prod/g' config-template.yml > config-prod.yml
```

### Pattern 2: Docker Compose Modernization

#### Before (Hardcoded Values)
```yaml
# docker-compose.yml template markers
services:
  api:
    # image_name = {{ values.docker.api_image }}
    image: "ghcr.io/company/myapp-api:latest"
    
  frontend:  
    # image_name = {{ values.docker.frontend_image }}
    image: "ghcr.io/company/myapp-frontend:latest"

# config.yml
docker:
  api_image: "ghcr.io/company/myapp-api:v1.2.0"
  frontend_image: "ghcr.io/company/myapp-frontend:v1.2.0"
```

#### After (Self-Referencing)
```yaml
# Same docker-compose.yml template markers (no change needed!)

# config.yml (much cleaner)
project:
  name: "myapp"
  version: "v1.2.0"

docker:
  registry: "ghcr.io/company"
  api_image: "{{ values.docker.registry }}/{{ values.project.name }}-api:{{ values.project.version }}"
  frontend_image: "{{ values.docker.registry }}/{{ values.project.name }}-frontend:{{ values.project.version }}"
```

### Pattern 3: Kubernetes Values Modernization

#### Before (Helm-style with Duplication)
```yaml
# values.yml
global:
  imageTag: "v1.2.3"
  namespace: "myapp-prod"

api:
  name: "myapp-api"
  image: "registry.com/myapp-api:v1.2.3"
  namespace: "myapp-prod"

frontend:
  name: "myapp-frontend" 
  image: "registry.com/myapp-frontend:v1.2.3"
  namespace: "myapp-prod"
```

#### After (DRY with Self-References)
```yaml
# values.yml
global:
  imageRegistry: "registry.com"
  imageTag: "v1.2.3"
  namespace: "myapp-prod"

app:
  name: "myapp"

api:
  name: "{{ values.app.name }}-api"
  image: "{{ values.global.imageRegistry }}/{{ values.api.name }}:{{ values.global.imageTag }}"
  namespace: "{{ values.global.namespace }}"

frontend:
  name: "{{ values.app.name }}-frontend"
  image: "{{ values.global.imageRegistry }}/{{ values.frontend.name }}:{{ values.global.imageTag }}"
  namespace: "{{ values.global.namespace }}"
```

## Migration Checklist

### Pre-Migration Assessment

- [ ] **Backup existing configurations** - Always backup before changes
- [ ] **Identify duplication** - Find repeated values across configurations
- [ ] **Map dependencies** - Understand relationships between values
- [ ] **Test current setup** - Ensure existing setup works before migration

### Migration Process

- [ ] **Install v0.4.0** - Upgrade Template Customizer
- [ ] **Test compatibility** - Run existing configs to ensure they still work
- [ ] **Start small** - Begin with simple references in non-critical configs
- [ ] **Add incrementally** - Gradually add self-references to reduce duplication
- [ ] **Validate each step** - Test with `--dry-run` after each change
- [ ] **Document changes** - Keep track of what was changed and why

### Post-Migration Validation

- [ ] **Test all environments** - Ensure configs work in dev, staging, prod
- [ ] **Verify output** - Compare generated files before/after migration
- [ ] **Performance check** - Ensure resolution doesn't impact performance
- [ ] **Team training** - Educate team on new configuration patterns

## Troubleshooting Migration Issues

### Issue: References Not Resolving

**Problem**: Template markers show unresolved references
```bash
# Output shows: {{ values.project.name }} instead of resolved value
```

**Solutions**:
1. Check reference syntax: `{{ values.path.to.value }}`
2. Verify referenced values exist in configuration
3. Test with verbose mode: `--verbose --dry-run`

### Issue: Circular Dependencies

**Problem**: Configuration has circular references
```bash
❌ Circular dependency detected: a → b → c → a
```

**Solutions**:
1. Identify the cycle in your configuration
2. Break the cycle by making one value independent
3. Restructure to create a clear dependency hierarchy

### Issue: Performance Degradation

**Problem**: Processing takes longer than before

**Solutions**:
1. Simplify reference chains (keep under 5 levels)
2. Use intermediate computed values for complex expressions
3. Consider disabling resolution for very large configs: `--no-resolve-refs`

## Best Practices for Migration

### 1. Start with High-Value Targets

Focus migration efforts on configurations with:
- High duplication (same values repeated)
- Frequent changes (versions, environments)
- Error-prone manual updates

### 2. Create Migration Branches

```bash
# Create feature branch for migration
git checkout -b feature/config-self-references

# Make incremental commits
git commit -m "Add self-references to project metadata"
git commit -m "Convert docker configuration to use references"
git commit -m "Update database config with computed values"
```

### 3. Document New Patterns

```yaml
# Add comments to explain new patterns
# config.yml

# Base project metadata - defined once
project:
  name: "ecommerce-api"    # Used throughout configuration
  version: "2.1.0"         # Single source of truth for version

# Computed infrastructure names - built from base values
computed:
  app_prefix: "{{ values.project.name }}-{{ values.environment.short }}"
  # Used as: ecommerce-api-prod, ecommerce-api-dev, etc.
```

### 4. Validate with Team

- Share updated configurations with team members
- Ensure everyone understands new patterns
- Document any team-specific conventions
- Provide training on troubleshooting reference issues

## Getting Help During Migration

### Resources
- **[Configuration Best Practices](CONFIGURATION_BEST_PRACTICES.md)** - Patterns and recommendations
- **[Troubleshooting Guide](TROUBLESHOOTING.md)** - Common issues and solutions
- **[Usage Examples](USAGE.md)** - Detailed examples and use cases

### Community Support
- **GitHub Issues**: [https://github.com/mkuhl/customizer/issues](https://github.com/mkuhl/customizer/issues)
- **Feature Requests**: For additional migration tools or features
- **Questions**: Tag issues with "migration" for migration-specific help

### Migration Tools

#### Duplication Finder Script
```bash
#!/bin/bash
# find-duplicates.sh - Find potential candidates for self-references

echo "Finding repeated values in configuration:"
echo "========================================"

# Find quoted strings that appear multiple times
grep -o '"[^"]*"' config.yml | sort | uniq -c | sort -nr | awk '$1 > 1 {print $1 " times: " $2}'

echo ""
echo "Finding potential base values:"
echo "============================"

# Find simple key-value pairs that could be base values
grep -E '^[[:space:]]*[a-zA-Z_][a-zA-Z0-9_]*:[[:space:]]*"[^"]*"[[:space:]]*$' config.yml
```

#### Reference Converter Script
```python
#!/usr/bin/env python3
# convert-references.py - Semi-automated reference conversion

import yaml
import sys

def find_potential_references(config, base_path=""):
    """Find values that could be converted to references."""
    suggestions = []
    
    if isinstance(config, dict):
        for key, value in config.items():
            current_path = f"{base_path}.{key}" if base_path else key
            
            if isinstance(value, str) and len(value.split()) <= 3:
                # Look for this value elsewhere in the config
                suggestions.extend(find_potential_references(value, current_path))
            elif isinstance(value, dict):
                suggestions.extend(find_potential_references(value, current_path))
                
    return suggestions

# Usage: python3 convert-references.py config.yml
```

## Version-Specific Notes

### Upgrading from v0.3.x to v0.4.0

- **New CLI flag**: `--no-resolve-refs` added for compatibility
- **New verbose output**: Resolution details shown with `--verbose`
- **Performance**: May be slightly slower due to reference resolution
- **Memory usage**: Slightly higher memory usage for configuration processing

### Upgrading from v0.2.x to v0.4.0

- All v0.3.x features included (external replacements for JSON/Markdown)
- Consider migrating external replacements to use self-references where applicable
- Review external replacement patterns for potential simplification

### Upgrading from v0.1.x to v0.4.0

- Significant new functionality available
- Consider comprehensive configuration review
- May benefit from full modernization approach
- Review all CLI options as many have been added

## Success Stories and Examples

### Example 1: Microservices Platform

**Before**: 15 separate configuration files with 60% duplication
**After**: Single template with environment-specific overrides
**Benefit**: 80% reduction in configuration maintenance, zero deployment errors

### Example 2: Multi-Environment Deployment

**Before**: Manual find/replace for environment deployments
**After**: Self-referencing configuration with environment variables
**Benefit**: Automated deployments, consistent naming across environments

### Example 3: Docker-Compose Stack

**Before**: Hardcoded image names and versions in multiple places
**After**: Single version definition referenced throughout
**Benefit**: One-line version updates, consistent image tagging

---

**Ready to migrate?** Start with Strategy 2 (Gradual Enhancement) for the best balance of risk and benefit. Remember: your existing configurations continue to work, so you can migrate at your own pace!