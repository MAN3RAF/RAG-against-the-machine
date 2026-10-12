from .models import MinimalSource
from typing import List


class Chunker:
    def __init__(self):
        pass



    def mark_down_chunker(self, path: str) -> List[MinimalSource]:
        
        with open(path, "r") as f:
            pass

    def text_chunker(self, path: str) -> List[MinimalSource]:
        
        with open(path, "r") as f:
            pass

    def python_chunker(self, path: str) -> List[MinimalSource]:
        
        with open(path, "r") as f:
            pass

    def chunk(self, paths: List[str]) -> List[MinimalSource]:

        try:
            for path in paths:
                if path.endswith(".py"):
                    self.python_chunker(path)
                elif path.endswith(".md"):
                    self.mark_down_chunker(path)
                elif path.endswith(".txt"):
                    self.text_chunker(path)

        except Exception as e: 
            print(e)




