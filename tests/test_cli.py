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
