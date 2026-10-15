import os
from typing import List
from pathlib import Path


class Parser:
    def __init__(self):
        pass


    def get_all_paths(self, file_path: str) -> List[str]:

        paths = []

        for p in Path(file_path).rglob("*"):
            if p.is_file() and p.suffix in (".py", ".txt", ".md"):
                paths.append(os.path.relpath(p))

        # paths = [os.path.relpath(p) for p in Path(file_path).rglob("*") if p.is_file() and p.suffix in (".py", ".txt", ".md")]

        return paths 

        



