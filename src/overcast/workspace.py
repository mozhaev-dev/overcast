from dataclasses import dataclass
from pathlib import Path


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
    paths.database_path.parent.mkdir(parents=True, exist_ok=True)
    paths.episodes_dir.mkdir(parents=True, exist_ok=True)
