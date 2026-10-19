import os
from pathlib import Path
from typing import List


class Parser:
    SUPPORTED_EXTENSIONS = {".py", ".md", ".txt"}

    def __init__(self, repo_root: str | Path) -> None:
        self.repo_root = Path(repo_root).expanduser().resolve()
        if not self.repo_root.exists():
            raise FileNotFoundError(f"Repository not found: {self.repo_root}")
        if not self.repo_root.is_dir():
            raise NotADirectoryError(f"Not a repository directory: {self.repo_root}")

    def get_all_paths(self) -> List[str]:
        """Return sorted absolute paths of eligible files under repo_root."""

        paths: List[str] = []

        def on_walk_error(error: OSError) -> None:
            raise error

        for directory, dirnames, filenames in os.walk(
            self.repo_root, onerror=on_walk_error, followlinks=False
        ):
            # Do not follow symlinked directories into other repositories.
            dirnames[:] = [
                name for name in dirnames
                if not (Path(directory) / name).is_symlink()
            ]
            for filename in filenames:
                file_path = Path(directory) / filename
                if file_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
                    continue
                if file_path.is_symlink():
                    continue
                if file_path.is_file():
                    paths.append(str(file_path.resolve()))

        return sorted(paths)

    def read_file(self, raw_path: str | Path) -> tuple[str, str]:
        """Return (repo-relative path, original text) without changing newlines.

        A path outside repo_root is a configuration error, not a file to skip.
        """
        path = Path(raw_path).expanduser().resolve(strict=True)
        try:
            source_path = path.relative_to(self.repo_root).as_posix()
        except ValueError as exc:
            raise ValueError(
                f"File {path} is outside repo_root {self.repo_root}. "
                "Use the same repository root for discovery and chunking."
            ) from exc

        with path.open("r", encoding="utf-8", newline="") as file:
            original_text = file.read()
        return source_path, original_text


