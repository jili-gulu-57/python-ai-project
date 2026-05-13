"""Small utilities for organizing Python AI project folders."""

from dataclasses import dataclass
from pathlib import Path


IGNORED_DIRECTORIES = {".git", ".idea", ".venv", "__pycache__", "src", "tests"}


@dataclass(frozen=True)
class AIProject:
    """A top-level AI project directory."""

    name: str
    path: Path


@dataclass(frozen=True)
class PythonFile:
    """A Python source file discovered in an AI project."""

    path: Path
    project: str | None


class AIProjectLibrary:
    """Browse a directory that stores multiple Python AI projects."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).expanduser().resolve()

    def list_projects(self) -> list[AIProject]:
        """Return top-level project directories sorted by name."""
        if not self.root.exists():
            return []

        projects = []
        for path in sorted(self.root.iterdir()):
            if path.is_dir() and path.name not in IGNORED_DIRECTORIES:
                projects.append(AIProject(name=path.name, path=path))
        return projects

    def list_python_files(self, project: str | None = None) -> list[PythonFile]:
        """Return Python files from the whole library or one project."""
        search_root = self.root / project if project else self.root
        if not search_root.exists():
            return []

        ignored = {self.root / name for name in IGNORED_DIRECTORIES}
        files: list[PythonFile] = []
        for path in sorted(search_root.rglob("*.py")):
            if any(parent in ignored for parent in path.parents):
                continue

            relative = path.relative_to(self.root)
            project_name = relative.parts[0] if relative.parts else None
            files.append(PythonFile(path=path, project=project_name))
        return files

