from .models import MinimalSource
from typing import List


class Chunker:
    def __init__(self):
        pass



    def mark_down_chunker(self, file_path: str) -> MinimalSource:
        pass

    def text_chunker(self, file_path: str) -> MinimalSource:
        pass

    def python_chunker(self, file_path: str) -> MinimalSource:
        pass

    def chunk(self, paths: List[str]) -> MinimalSource:

        for path in paths:
            if path.suffix == ".py":
                self.python_chunker(path)
            elif path.suffix == ".md":
                self.mark_down_chunker(path)
            elif path.suffix == ".txt":
                self.text_chunker(path)





