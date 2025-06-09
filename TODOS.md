# Template Customizer Implementation TODOs

## Phase 1: Foundation & Project Setup
**Goal:** Create standalone customizer package with basic structure

- [x] 1.1 Create customizer directory structure with basic Python package layout - DONE
- [x] 1.2 Set up pyproject.toml with dependencies (jinja2, pyyaml, click, rich) - DONE
- [x] 1.3 Create core module structure: scanner.py, parser.py, processor.py, writer.py - DONE
- [x] 1.4 Implement basic CLI entry point with click framework - DONE
- [x] 1.5 Create CLAUDE.md with customizer-specific instructions and context - DONE
- [x] 1.6 Create initial test structure and basic smoke tests - DONE
- [x] 1.7 **Test Phase 1:** Verify package imports and CLI help works - DONE

## Phase 2: Comment Parser Engine
**Goal:** Detect and extract template markers from comments

- [x] 2.1 Implement FileTypeDetector class to map extensions to comment syntax - DONE
- [x] 2.2 Create CommentParser class with regex patterns for each comment type - DONE
- [x] 2.3 Implement template marker extraction (varName = {{ expression }}) - DONE
- [x] 2.4 Add Jinja2 syntax validation for extracted template expressions - DONE
- [x] 2.5 Create unit tests for comment parsing across all supported file types - DONE
- [x] 2.6 **Test Phase 2:** Verify comment parser extracts templates from sample files - DONE

## Phase 3: Template Processing Core
**Goal:** Render templates and process individual files safely

- [ ] 3.1 Implement ParameterLoader class for YAML/JSON configuration files
- [ ] 3.2 Create TemplateProcessor class with Jinja2 environment setup
- [ ] 3.3 Implement template rendering with error handling for missing variables
- [ ] 3.4 Create FileProcessor class to handle line-by-line file processing
- [ ] 3.5 Implement dry-run mode to preview changes without modifying files
- [ ] 3.6 Add file backup and restore capabilities for safety
- [ ] 3.7 **Test Phase 3:** Process sample files with template markers using test config

## Phase 4: Project-Wide Processing
**Goal:** Orchestrate processing across entire project directories

- [ ] 4.1 Implement FileScanner class with include/exclude pattern support
- [ ] 4.2 Add directory traversal with filtering for common exclusions
- [ ] 4.3 Create project-wide processing orchestrator
- [ ] 4.4 Implement comprehensive CLI with all options (--dry-run, --verbose, etc)
- [ ] 4.5 Add rich-based progress reporting, colors, and formatted change summary output
- [ ] 4.6 **Test Phase 4:** Process entire directory structure with filtering

## Phase 5: Testing & Quality Assurance
**Goal:** Comprehensive testing and error handling

- [ ] 5.1 Create comprehensive unit test suite for all core components
- [ ] 5.2 Implement integration tests with sample project structure
- [ ] 5.3 Add error handling tests (malformed templates, missing files, etc)
- [ ] 5.4 Create performance tests for large project processing
- [ ] 5.5 **Test Phase 5:** Run full test suite and validate all functionality

## Phase 6: Real-World Validation
**Goal:** Validate with actual py-ang project and create documentation

- [ ] 6.1 Add template markers to key py-ang project files for validation
- [ ] 6.2 Create example configuration file for py-ang template customization
- [ ] 6.3 Test customizer tool on actual py-ang project with real config
- [ ] 6.4 Verify that customized project still builds and runs correctly
- [ ] 6.5 Create documentation: README, CLI usage with rich output examples, and best practices
- [ ] 6.6 **Test Phase 6:** End-to-end validation with py-ang as template source

---

**Progress Legend:**
- [ ] Pending
- [x] DONE

**Testing Strategy:** Each phase concludes with comprehensive testing to ensure functionality before proceeding. This allows for early detection of issues and ensures each component works independently and integrates properly.

**Dependencies:** Each phase builds upon the previous phase's deliverables, ensuring incremental progress and reducing risk of major architectural issues.