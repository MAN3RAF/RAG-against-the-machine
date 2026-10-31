
import json
from math import isfinite
from pathlib import Path
import bm25s
from .models import MinimalSource
from typing import List, Dict


class RagBm25:
    def __init__(
        self,
        chunks_path: str = "data/processed/chunked_data.json",
        save_directory: str = "data/processed/bm25_index"
    ) -> None:

        self.chunks_path = Path(chunks_path)
        self.save_directory = Path(save_directory)
        self.bm25 = bm25s.BM25()
        self._loaded = False

    def load_chunks(self) -> tuple[List[str], List[MinimalSource]]:
        """Load and validate chunks and their source metadata."""

        with self.chunks_path.open("r", encoding="utf-8") as f:
            records = json.load(f)

        if not isinstance(records, List) or not records:
            raise ValueError("Chunk data must be a non-empty JSON List.")

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

            source = MinimalSource.model_validate(
                record.get("source")
            )

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
        """Build and save the BM25 index with source metadata."""

        corpus, sources = self.load_chunks()

        corpus_tokens = bm25s.tokenize(
            corpus,
            stopwords=None
        )

        self.bm25 = bm25s.BM25()
        self._loaded = False
        self.bm25.index(corpus_tokens)

        saved_corpus = [
            {
                "text": text,
                "source": source.model_dump()
            }
            for text, source in zip(corpus, sources)
        ]

        self.save_directory.mkdir(parents=True, exist_ok=True)

        self.bm25.save(
            str(self.save_directory),
            corpus=saved_corpus
        )

        return len(corpus)

    def load_saved_corpus(self) -> bm25s.BM25:
        """Load the saved BM25 index and its chunk records."""

        if not self.save_directory.is_dir():
            raise FileNotFoundError(
                f"BM25 index directory not found: {self.save_directory}"
            )

        self.bm25 = bm25s.BM25.load(
            str(self.save_directory),
            load_corpus=True
        )

        if self.bm25.corpus is None or len(self.bm25.corpus) == 0:
            raise ValueError("Saved BM25 index has no chunk corpus.")

        self._loaded = True

        return self.bm25

    def retrieve_hits(self, user_question: str, k: int = 5) -> List[Dict]:
        """Retrieve chunk text, source metadata and scores."""

        if not isinstance(user_question, str):
            raise TypeError("user_question must be a string")

        if type(k) is not int or k < 1:
            raise ValueError("k must be a positive integer")

        if not user_question.strip():
            return []

        if not self._loaded:
            self.load_saved_corpus()

        query_tokens = bm25s.tokenize(
            [user_question],
            stopwords=None
        )

        actual_k = min(k, len(self.bm25.corpus))

        documents, scores = self.bm25.retrieve(
            query_tokens,
            k=actual_k,
            sorted=True,
            show_progress=False
        )

        # print(zip(documents[0], scores[0]))

        hits = []
        seen_sources = set()

        for record, raw_score in zip(documents[0], scores[0]):
            score = float(raw_score)

            if not isfinite(score) or score <= 0:
                continue

            if not isinstance(record, dict):
                raise ValueError(
                    "Saved corpus entries must be dictionaries."
                )

            text = record.get("text")
            if not isinstance(text, str) or not text:
                raise ValueError("Retrieved chunk has invalid text.")

            source = MinimalSource.model_validate(
                record.get("source")
            )

            key = (
                source.file_path,
                source.first_character_index,
                source.last_character_index
            )

            if key in seen_sources:
                continue

            seen_sources.add(key)

            hits.append({
                "text": text,
                "source": source,
                "score": score
            })
        
        # print(hit["source"] for hit in hits)

        return hits

    def retrieve(self, user_question: str, k: int = 5) -> List[MinimalSource]:
        """Return the relevant source locations."""

        return [
            hit["source"]
            for hit in self.retrieve_hits(user_question, k)
        ]


    def search_dataset(
        self,
        dataset_path: str,
        save_directory: str = "data/output/search_results",
        k: int = 5) -> Path:
        """Search every question and save the results for evaluation."""

        if type(k) is not int or k < 1:
            raise ValueError("k must be a positive integer")

        dataset_file = Path(dataset_path)

        with dataset_file.open("r", encoding="utf-8") as f:
            dataset = json.load(f)

        if not isinstance(dataset, dict):
            raise ValueError("Dataset must be a JSON object.")

        questions = dataset.get("rag_questions")

        if not isinstance(questions, List):
            raise ValueError("'rag_questions' must be a list.")

        results = []

        for item in questions:
            question_id = item["question_id"]
            question = item["question"]

            sources = self.retrieve(question, k=k)

            results.append({
                "question_id": question_id,
                "question": question,
                "retrieved_sources": [
                    {
                        **source.model_dump(),
                        "file_path": "data/raw/" + source.file_path,
                    }
                    for source in sources
                ]
            })

        output_dir = Path(save_directory)
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / dataset_file.name

        output_data = {
            "search_results": results,
            "k": k
        }

        with output_file.open("w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        return output_file



