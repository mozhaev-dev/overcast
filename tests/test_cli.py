import shutil
import subprocess
from pathlib import Path

from overcast.workspace import WorkspacePaths


def test_cli_init(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace_paths = WorkspacePaths(workspace)
    executable = shutil.which("overcast")

    assert executable is not None

    subprocess.run(
        [executable, "init", str(workspace)],
        check=True,
        text=True,
        capture_output=True,
        timeout=10,
    )

    assert workspace_paths.episodes_dir.is_dir()
    assert workspace_paths.database_path.parent.is_dir()


def test_cli_init_reports_file_conflict(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace_paths = WorkspacePaths(workspace)
    executable = shutil.which("overcast")
    file_content = "Keep me"
    workspace_paths.root.mkdir()
    workspace_paths.episodes_dir.write_text(data=file_content, encoding="utf-8")

    assert executable is not None

    result = subprocess.run(
        [executable, "init", str(workspace)],
        check=False,
        text=True,
        capture_output=True,
        timeout=10,
    )

    assert workspace_paths.episodes_dir.read_text(encoding="utf-8") == file_content
    assert result.returncode == 1
    assert "Can't initialize workspace" in result.stderr
    assert str(workspace) in result.stderr
    assert "Traceback" not in result.stderr
