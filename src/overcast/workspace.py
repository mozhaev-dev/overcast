from dataclasses import dataclass
from pathlib import Path

from overcast.errors import WorkspaceError
from overcast.storage import initialize_database


@dataclass
class WorkspacePaths:
    root: Path

    @property
    def database_path(self) -> Path:
        return self.root / "data" / "app.sqlite"

    @property
    def episodes_dir(self) -> Path:
        return self.root / "episodes"


def initialize_workspace(paths: WorkspacePaths) -> None:
    try:
        paths.database_path.parent.mkdir(parents=True, exist_ok=True)
        paths.episodes_dir.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        raise WorkspaceError(
            f"Can't create directory {error.filename}: {error.strerror}"
        ) from error

    initialize_database(paths.database_path)
