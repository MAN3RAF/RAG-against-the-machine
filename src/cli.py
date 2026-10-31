
import json
from pathlib import Path
from .parser import Parser
from .chunker import Chunker
from .ragbm25 import RagBm25


class Cli:
    """Commands for indexing and searching the Rag project."""

    def index(
        self,
        max_chunk_size: int = 2000) -> None:
        """Parse, chunk, and build the BM25 index."""

        parser = Parser("data/raw/vllm-0.10.1")
        paths = parser.get_all_paths()

        chunker = Chunker(max_chunk_size=max_chunk_size)
        chunker.chunk(paths)

        rag = RagBm25()
        count = rag.index()

        print(f"Indexed {count} chunks.")

    def search(self, query: str, k: int = 5) -> None:
        """Search the saved BM25 index."""

        if type(k) is not int or k < 1:
            raise ValueError("k must be a positive integer")

        if not query.strip():
            print("[]")
            return

        rag = RagBm25()

        if not rag.save_directory.is_dir():
            print("BM25 index not found. Building it...")
            self.index()

        hits = rag.retrieve_hits(query, k=k)

        results = [
            {
                "text": hit["text"],
                "source": hit["source"].model_dump(),
                "score": hit["score"]
            }
            for hit in hits
        ]

        print(json.dumps(
            results,
            indent=2,
            ensure_ascii=False
        ))

    def search_dataset(
        self,
        dataset_path: str,
        k: int = 5,
        save_directory: str = "data/output/search_results") -> None:
        """Retrieve sources for all questions in a dataset."""

        if not Path(dataset_path).is_file():
            raise FileNotFoundError(
                f"Dataset not found: {dataset_path}"
            )

        rag = RagBm25()

        if not rag.save_directory.is_dir():
            print("BM25 index not found. Building it...")
            self.index()

        output_file = rag.search_dataset(
            dataset_path=dataset_path,
            save_directory=save_directory,
            k=k
        )

        print(f"Search results saved to: {output_file}")
