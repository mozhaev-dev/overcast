class AppError(Exception):
    """Base application exception"""


class WorkspaceError(AppError):
    """Workspace exception"""


class StorageError(AppError):
    """Storage exception"""
