from pathlib import Path

from pytest import raises

from overcast.errors import WorkspaceError
from overcast.workspace import WorkspacePaths, initialize_workspace


def test_workspace_paths() -> None:
    root = Path("test-workspace")
    workspace_paths = WorkspacePaths(root)
    assert workspace_paths.database_path == root / "data" / "app.sqlite"
    assert workspace_paths.episodes_dir == root / "episodes"


def test_initialize_workspace(tmp_path: Path) -> None:
    root = tmp_path / "workspace"
    workspace_paths = WorkspacePaths(root)
    initialize_workspace(workspace_paths)
    initialize_workspace(workspace_paths)

    assert workspace_paths.database_path.parent.is_dir()
    assert workspace_paths.database_path.exists()
    assert workspace_paths.episodes_dir.is_dir()


def test_initialize_workspace_rejects_file_at_episodes_path(tmp_path: Path) -> None:
    root = tmp_path / "workspace"
    root.mkdir(parents=True)
    workspace_paths = WorkspacePaths(root)
    file_content = "Keep me"
    workspace_paths.episodes_dir.write_text(data=file_content, encoding="utf-8")

    with raises(WorkspaceError):
        initialize_workspace(workspace_paths)

    assert workspace_paths.episodes_dir.read_text(encoding="utf-8") == file_content
