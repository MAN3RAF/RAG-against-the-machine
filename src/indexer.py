import json
from pathlib import Path
import bm25s
from models import MinimalSource
from typing import List


class Indexer:
    def __init__(
        self,
        chunks_path: str = "data/processed/chunked_data.json",
        save_directory: str = "data/processed/bm25_index",
    ) -> None:

        self.chunks_path = Path(chunks_path)
        self.save_directory = Path(save_directory)
        self.bm25 = bm25s.BM25()

    def load_chunks(self) -> tuple[List[str], List[MinimalSource]]:
        """Load and validate chunks and their source metadata."""

        with self.chunks_path.open("r", encoding="utf-8") as f:
            records = json.load(f)

        if not isinstance(records, List) or not records:
            raise ValueError("Chunk data must be a non-empty JSON list.")

        corpus: List[str] = []
        sources: List[MinimalSource] = []

        for i, record in enumerate(records):
            if not isinstance(record, dict):
                raise ValueError(f"Chunk {i} is not an object.")

            text = record.get("text")

            if not isinstance(text, str) or not text.strip():
                raise ValueError(f"Chunk {i} has no valid text.")

            if len(text) > 2000:
                raise ValueError(f"Chunk {i} exceeds 2,000 characters.")

            source = MinimalSource.model_validate(record.get("source"))

            start = source.first_character_index
            end = source.last_character_index

            if start < 0 or end <= start or end - start != len(text):
                raise ValueError(
                    f"Chunk {i} has invalid character offsets."
                )

            corpus.append(text)
            sources.append(source)

        return corpus, sources

    def index(self) -> int:
        """Build and save the BM25 index with its source metadata."""

        corpus, sources = self.load_chunks()

        corpus_tokens = bm25s.tokenize(corpus, stopwords=None)

        self.bm25.index(corpus_tokens)

        saved_corpus = [
            {"text": text, "source": source.model_dump()}
            for text, source in zip(corpus, sources)
        ]

        self.save_directory.mkdir(parents=True, exist_ok=True)

        self.bm25.save(
            str(self.save_directory),
            corpus=saved_corpus,
        )

        return len(corpus)

    def load_index(self) -> None:
        """Load the saved BM25 index and chunk metadata."""

        if not self.save_directory.is_dir():
            raise FileNotFoundError(
                f"BM25 index directory not found: {self.save_directory}"
            )

        self.bm25 = bm25s.BM25.load(
            str(self.save_directory),
            load_corpus=True,
        )

