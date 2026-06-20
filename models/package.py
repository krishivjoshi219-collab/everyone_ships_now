from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class RequirementModel:
    """Blueprint representing extracted dependency boundaries and rules."""
    package: str
    specifiers: str = "any"
    extras: List[str] = field(default_factory=list)

@dataclass
class InstalledModel:
    """Blueprint representing a component currently deployed in the user's environment."""
    package: str
    version: str

@dataclass
class ConflictModel:
    """Blueprint capturing a verified mathematical mismatch between rules and reality."""
    package: str
    installed_version: str
    required_specifiers: str
    verdict: str

@dataclass
class MissingPackageModel:
    """Blueprint representing a mandatory dependency completely absent from the runtime environment."""
    package: str
    required_specifiers: str = "any"

@dataclass
class PipelineReportModel:
    """The master record passed smoothly from the backend engines down to the frontend UI or PDF generator."""
    status: str  # e.g., "clean", "conflict_detected", "os_error"
    domain: str = "python_package"  # Classified by the Sentinel
    detected_issues: List[str] = field(default_factory=list)
    conflicts: List[ConflictModel] = field(default_factory=list)
    missing_packages: List[MissingPackageModel] = field(default_factory=list)
    suggested_os_patches: List[str] = field(default_factory=list)
