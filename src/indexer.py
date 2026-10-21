import json
from pathlib import Path
from typing import List
from models import MinimalSource
import bm25s


class Indexer:
    def __init__(
        self,
        chunks_path: str = "data/processed/chunked_data.json",
        save_directory: str = "data/processed/"
    ):
        self.chunks_path = Path(chunks_path)
        self.bm25 = bm25s.BM25()
        
        self.save_directory = save_directory

    def load_chunks(self) -> tuple[str, List]:
        with self.chunks_path.open("r", encoding="utf-8") as f:
            records = json.load(f)

        if not records:
            raise ValueError("No chunks found to index")

        corpus: str = [record["text"] for record in records]

        sources: List = [
            MinimalSource.model_validate(record["source"])
            for record in records
        ]

        return corpus, sources

    def index(self):
        
        corpus, sources = self.load_chunks()

        corpus_tokens = bm25s.tokenize(corpus)

        self.bm25.index(corpus_tokens)

        self.bm25.save(self.save_directory)


