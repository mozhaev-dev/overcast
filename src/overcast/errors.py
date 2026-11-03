from dataclasses import dataclass


class AppError(Exception):
    """Base application exception"""


class WorkspaceError(AppError):
    """Workspace exception"""


class StorageError(AppError):
    """Storage exception"""


@dataclass(frozen=True)
class FieldIssue:
    field: str
    message: str


class ValidationError(AppError):
    """Data objects validation exception"""

    issues: tuple[FieldIssue, ...]

    def __init__(self, issues: tuple[FieldIssue, ...]) -> None:
        self.issues = issues
        message = "\n".join(f"  {issue.field}: {issue.message}" for issue in issues)
        super().__init__(f"Invalid input:\n{message}")
