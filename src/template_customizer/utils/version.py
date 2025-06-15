"""Version management utilities for template customizer."""

import re
from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class SemanticVersion:
    """Semantic version representation following semver.org specification."""
    
    major: int
    minor: int
    patch: int
    prerelease: Optional[str] = None
    build: Optional[str] = None
    
    def __str__(self) -> str:
        """Return string representation of version."""
        version = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            version += f"-{self.prerelease}"
        if self.build:
            version += f"+{self.build}"
        return version
    
    def __eq__(self, other) -> bool:
        """Check if two versions are equal."""
        if not isinstance(other, SemanticVersion):
            return False
        return (
            self.major == other.major
            and self.minor == other.minor
            and self.patch == other.patch
            and self.prerelease == other.prerelease
        )
    
    def __lt__(self, other) -> bool:
        """Check if this version is less than another."""
        if not isinstance(other, SemanticVersion):
            return NotImplemented
        
        # Compare major.minor.patch
        if (self.major, self.minor, self.patch) != (other.major, other.minor, other.patch):
            return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)
        
        # Handle prerelease versions
        if self.prerelease is None and other.prerelease is None:
            return False
        if self.prerelease is None:
            return False  # Normal version > prerelease
        if other.prerelease is None:
            return True  # Prerelease < normal version
        
        return self.prerelease < other.prerelease
    
    def __le__(self, other) -> bool:
        """Check if this version is less than or equal to another."""
        return self == other or self < other
    
    def __gt__(self, other) -> bool:
        """Check if this version is greater than another."""
        return not self <= other
    
    def __ge__(self, other) -> bool:
        """Check if this version is greater than or equal to another."""
        return not self < other
    
    def is_compatible_with(self, other: "SemanticVersion") -> bool:
        """Check if this version is compatible with another (same major version)."""
        return self.major == other.major
    
    def bump_major(self) -> "SemanticVersion":
        """Return new version with major version incremented."""
        return SemanticVersion(
            major=self.major + 1,
            minor=0,
            patch=0,
            prerelease=None,
            build=None
        )
    
    def bump_minor(self) -> "SemanticVersion":
        """Return new version with minor version incremented."""
        return SemanticVersion(
            major=self.major,
            minor=self.minor + 1,
            patch=0,
            prerelease=None,
            build=None
        )
    
    def bump_patch(self) -> "SemanticVersion":
        """Return new version with patch version incremented."""
        return SemanticVersion(
            major=self.major,
            minor=self.minor,
            patch=self.patch + 1,
            prerelease=None,
            build=None
        )


class VersionParser:
    """Parser for semantic version strings."""
    
    # Regex pattern for semantic versioning (simplified)
    VERSION_PATTERN = re.compile(
        r"^(?P<major>0|[1-9]\d*)"
        r"\.(?P<minor>0|[1-9]\d*)"
        r"\.(?P<patch>0|[1-9]\d*)"
        r"(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z][0-9a-zA-Z-]*)"
        r"(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z][0-9a-zA-Z-]*))*))"
        r"?(?:\+(?P<build>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
    )
    
    @classmethod
    def parse(cls, version_string: str) -> SemanticVersion:
        """Parse a version string into a SemanticVersion object.
        
        Args:
            version_string: Version string to parse (e.g., "1.2.3", "1.0.0-alpha.1")
            
        Returns:
            SemanticVersion object
            
        Raises:
            ValueError: If version string is invalid
        """
        version_string = version_string.strip()
        
        # Additional validation for common invalid patterns
        if (version_string.endswith('-') or version_string.endswith('+') or
            version_string.startswith('v') or not version_string):
            raise ValueError(f"Invalid version string: {version_string}")
        
        match = cls.VERSION_PATTERN.match(version_string)
        if not match:
            raise ValueError(f"Invalid version string: {version_string}")
        
        groups = match.groupdict()
        
        return SemanticVersion(
            major=int(groups["major"]),
            minor=int(groups["minor"]),
            patch=int(groups["patch"]),
            prerelease=groups["prerelease"],
            build=groups["build"]
        )
    
    @classmethod
    def is_valid(cls, version_string: str) -> bool:
        """Check if a version string is valid.
        
        Args:
            version_string: Version string to check
            
        Returns:
            True if valid, False otherwise
        """
        try:
            cls.parse(version_string)
            return True
        except ValueError:
            return False


class VersionManager:
    """Version management utilities."""
    
    @staticmethod
    def compare_versions(version1: str, version2: str) -> int:
        """Compare two version strings.
        
        Args:
            version1: First version string
            version2: Second version string
            
        Returns:
            -1 if version1 < version2
             0 if version1 == version2
             1 if version1 > version2
             
        Raises:
            ValueError: If either version string is invalid
        """
        v1 = VersionParser.parse(version1)
        v2 = VersionParser.parse(version2)
        
        if v1 < v2:
            return -1
        elif v1 > v2:
            return 1
        else:
            return 0
    
    @staticmethod
    def is_compatible(version1: str, version2: str) -> bool:
        """Check if two versions are compatible (same major version).
        
        Args:
            version1: First version string
            version2: Second version string
            
        Returns:
            True if compatible, False otherwise
            
        Raises:
            ValueError: If either version string is invalid
        """
        v1 = VersionParser.parse(version1)
        v2 = VersionParser.parse(version2)
        
        return v1.is_compatible_with(v2)
    
    @staticmethod
    def get_next_version(current_version: str, bump_type: str) -> str:
        """Get next version based on bump type.
        
        Args:
            current_version: Current version string
            bump_type: Type of bump ('major', 'minor', 'patch')
            
        Returns:
            Next version string
            
        Raises:
            ValueError: If version string is invalid or bump_type is unknown
        """
        version = VersionParser.parse(current_version)
        
        if bump_type == "major":
            next_version = version.bump_major()
        elif bump_type == "minor":
            next_version = version.bump_minor()
        elif bump_type == "patch":
            next_version = version.bump_patch()
        else:
            raise ValueError(f"Unknown bump type: {bump_type}")
        
        return str(next_version)


def get_version_info() -> Tuple[str, SemanticVersion]:
    """Get current version information from package.
    
    Returns:
        Tuple of (version_string, SemanticVersion_object)
    """
    from .. import __version__
    
    version_obj = VersionParser.parse(__version__)
    return __version__, version_obj