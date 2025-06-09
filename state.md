# Template Customizer - Project State

## Last Updated
2025-01-06

## Project Overview
- **Project**: Template Customizer - standalone Python tool for customizing project templates
- **Status**: Initial setup phase
- **Language**: Python 3.8+
- **Package Manager**: uv

## Current Session State

### Completed Tasks
- [x] Read CLAUDE.md to understand project requirements
- [x] Initialized git repository
- [x] Verified tests are passing (46 tests, 78% coverage)
- [x] Fixed -o (output) option to properly copy files to output directory

### Project Structure Status
- Core directories and files exist as per directory structure
- Main modules present:
  - `src/template_customizer/cli.py` - CLI entry point
  - `src/template_customizer/core/` - Core processing modules
  - `src/template_customizer/utils/` - Utility modules
  - `tests/` - Test suite

### Dependencies Status
- Virtual environment exists at .venv/
- All dependencies installed and working
- Required: jinja2, pyyaml, click, rich

### Key Features Status
- [x] Click-based CLI (implemented, needs rich enhancement)
- [x] Template marker parsing (comment-based) - Phase 2 complete
- [x] File type detection and comment syntax support - Phase 2 complete
- [x] Output directory (-o) option - Now working correctly
- [ ] Jinja2 template processing - Phase 3 in progress
- [ ] Dry-run mode with preview - Phase 3 todo
- [ ] Backup creation before modifications - Phase 3 todo
- [ ] Rich progress bars and colored output - Phase 4 todo

### Testing Status
- All 46 tests passing
- Test coverage: 78% overall
- Coverage breakdown:
  - parser.py: 96% coverage
  - file_types.py: 89% coverage
  - cli.py: 81% coverage
  - writer.py: 75% coverage
  - processor.py: 67% coverage (needs Phase 3 implementation)
  - scanner.py: 66% coverage
  - validation.py: 54% coverage

### Wrapper Script Status
- `./customize` wrapper script works correctly
- Activates .venv and runs template-customizer command

### Current Phase: Phase 3 - Template Processing Core
According to TODOS.md, we're currently on Phase 3. Phases 1 & 2 are complete.

### Phase 3 Tasks (from TODOS.md)
- [ ] Implement ParameterLoader class for YAML/JSON configuration files
- [ ] Create TemplateProcessor class with Jinja2 environment setup
- [ ] Implement template rendering with error handling for missing variables
- [ ] Create FileProcessor class to handle line-by-line file processing
- [ ] Implement dry-run mode to preview changes without modifying files
- [ ] Add file backup and restore capabilities for safety
- [ ] Test Phase 3: Process sample files with template markers using test config

### Next Steps
1. Review existing Phase 1 & 2 implementations
2. Check if dependencies are installed with uv
3. Begin Phase 3 implementation starting with ParameterLoader class

## Important Notes
- This is a standalone project (no py-ang dependencies)
- Must use Click (not argparse) for CLI
- Must integrate Rich for beautiful terminal output
- Git commits should be short and concise (no co-authored comments)

## Pending Actions
- Fix file ownership issue (many files owned by root instead of vscode)
- Create initial git commit once ownership is fixed