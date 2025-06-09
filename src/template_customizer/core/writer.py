"""File writing and backup module."""

import shutil
from pathlib import Path
from typing import List, Dict, NamedTuple
import tempfile
import os

from .parser import TemplateMarker


class FileChange(NamedTuple):
    """Represents a change to be made to a file."""
    file_path: Path
    line_number: int
    old_content: str
    new_content: str
    marker: TemplateMarker


class FileWriter:
    """Handles safe file writing with backup capabilities."""
    
    def __init__(self, backup_enabled: bool = True):
        """Initialize file writer.
        
        Args:
            backup_enabled: Whether to create backup files before modification
        """
        self.backup_enabled = backup_enabled
        self.backup_dir: Path = None
        self._backup_files: Dict[Path, Path] = {}
    
    def prepare_changes(
        self, 
        file_path: Path, 
        markers_and_values: List[tuple]
    ) -> List[FileChange]:
        """Prepare changes for a file based on template markers.
        
        Args:
            file_path: Path to file to modify
            markers_and_values: List of (marker, rendered_value) tuples
            
        Returns:
            List of FileChange objects representing planned modifications
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File does not exist: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            raise ValueError(f"Cannot read file as text: {file_path}")
        
        changes = []
        
        for marker, rendered_value in markers_and_values:
            if rendered_value.startswith("ERROR:"):
                # Skip markers that failed to render
                continue
                
            target_line_idx = marker.target_line_number
            
            if target_line_idx < len(lines):
                old_content = lines[target_line_idx].rstrip()
                
                # Extract the variable assignment pattern and replace the value
                new_content = self._generate_new_line(old_content, marker.variable_name, rendered_value)
                
                change = FileChange(
                    file_path=file_path,
                    line_number=target_line_idx,
                    old_content=old_content,
                    new_content=new_content,
                    marker=marker
                )
                changes.append(change)
        
        return changes
    
    def apply_changes(self, changes: List[FileChange], dry_run: bool = False) -> bool:
        """Apply changes to files.
        
        Args:
            changes: List of changes to apply
            dry_run: If True, don't actually modify files
            
        Returns:
            True if all changes were applied successfully
        """
        if dry_run:
            return True  # Dry run always "succeeds"
        
        # Group changes by file
        files_to_change = {}
        for change in changes:
            if change.file_path not in files_to_change:
                files_to_change[change.file_path] = []
            files_to_change[change.file_path].append(change)
        
        # Apply changes file by file
        success = True
        for file_path, file_changes in files_to_change.items():
            try:
                self._apply_file_changes(file_path, file_changes)
            except Exception as e:
                print(f"Error applying changes to {file_path}: {e}")
                success = False
        
        return success
    
    def create_backup(self, file_path: Path) -> Path:
        """Create backup of a file.
        
        Args:
            file_path: File to backup
            
        Returns:
            Path to backup file
        """
        if not self.backup_enabled:
            return None
        
        if self.backup_dir is None:
            self.backup_dir = Path(tempfile.mkdtemp(prefix="template_customizer_backup_"))
        
        backup_path = self.backup_dir / f"{file_path.name}.backup"
        shutil.copy2(file_path, backup_path)
        self._backup_files[file_path] = backup_path
        
        return backup_path
    
    def restore_backup(self, file_path: Path) -> bool:
        """Restore file from backup.
        
        Args:
            file_path: File to restore
            
        Returns:
            True if restore was successful
        """
        if file_path not in self._backup_files:
            return False
        
        backup_path = self._backup_files[file_path]
        if backup_path.exists():
            shutil.copy2(backup_path, file_path)
            return True
        
        return False
    
    def cleanup_backups(self):
        """Clean up all backup files."""
        if self.backup_dir and self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)
            self.backup_dir = None
            self._backup_files.clear()
    
    def _apply_file_changes(self, file_path: Path, changes: List[FileChange]):
        """Apply changes to a single file."""
        # Create backup first
        if self.backup_enabled:
            self.create_backup(file_path)
        
        # Read current file content
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Apply changes (in reverse order to maintain line numbers)
        for change in sorted(changes, key=lambda c: c.line_number, reverse=True):
            if change.line_number < len(lines):
                lines[change.line_number] = change.new_content + '\n'
        
        # Write modified content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
    
    def _generate_new_line(self, old_line: str, variable_name: str, new_value: str) -> str:
        """Generate new line content with updated value.
        
        Args:
            old_line: Original line content
            variable_name: Variable name to update
            new_value: New value to assign
            
        Returns:
            New line content with updated value
        """
        # Simple approach: look for variable_name = and replace everything after =
        # This could be made more sophisticated to handle various assignment patterns
        
        import re
        
        # Pattern to match variable assignment
        pattern = rf'({re.escape(variable_name)}\s*=\s*)[^#\n]*'
        
        def replace_value(match):
            return f"{match.group(1)}{new_value}"
        
        new_line = re.sub(pattern, replace_value, old_line)
        
        # If no substitution was made, append the assignment
        if new_line == old_line:
            # Fallback: try to replace everything after the first =
            if '=' in old_line:
                prefix = old_line.split('=', 1)[0] + '= '
                new_line = prefix + new_value
            else:
                new_line = f"{variable_name} = {new_value}"
        
        return new_line