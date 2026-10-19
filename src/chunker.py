import json
from pathlib import Path
from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import Language, RecursiveCharacterTextSplitter
from tqdm import tqdm

from models import MinimalSource


class Chunker:
    """Prepare source chunks and their exact character ranges for indexing."""

    def __init__(self, max_chunk_size: int = 2000) -> None:

        if (
            type(max_chunk_size) is not int
            or not 1 <= max_chunk_size <= 2000
        ):
            raise ValueError("max_chunk_size must be between 1 and 2000")

        self.max_chunk_size = max_chunk_size
        overlap = min(max_chunk_size - 1, max_chunk_size // 20)
        settings = {
            "chunk_size": max_chunk_size,
            "chunk_overlap": overlap,
            "add_start_index": True
        }

        python_splitter = RecursiveCharacterTextSplitter.from_language(
            language=Language.PYTHON, **settings
        )
        markdown_splitter = RecursiveCharacterTextSplitter.from_language(
            language=Language.MARKDOWN, **settings
        )
        text_splitter = RecursiveCharacterTextSplitter(**settings)

        self.splitters: dict[str, RecursiveCharacterTextSplitter] = {
            ".py": python_splitter,
            ".md": markdown_splitter,
            ".txt": text_splitter
        }

    def make_minimal_source(
        self,
        file_path: str,
        original_text: str,
        chunks: List[Document],
    ) -> List[MinimalSource]:
        """Locate chunks in the original text and validate their ranges."""

        minimal_sources: List[MinimalSource] = []
        previous_start = -1
        previous_content: str | None = None

        for chunk in chunks:
            content = chunk.page_content
            if not content or len(content) > self.max_chunk_size:
                raise ValueError(f"Invalid chunk length in {file_path}")

            start = chunk.metadata.get("start_index")
            valid_start = (
                type(start) is int
                and start >= previous_start
                and start >= 0
                and original_text[start:start + len(content)] == content
                and not (
                    content == previous_content and start == previous_start
                )
            )

            if not valid_start:
                # Forward matching repairs missing/incorrect start indices,
                # including equal chunks pointing to the same occurrence.
                search_from = max(0, previous_start)
                if content == previous_content:
                    search_from += 1
                start = original_text.find(content, search_from)

            if start == -1:
                raise ValueError(f"Cannot locate chunk in {file_path}")

            end = start + len(content)
            minimal_sources.append(
                MinimalSource(
                    file_path=file_path,
                    first_character_index=start,
                    last_character_index=end,
                )
            )
            previous_start = start
            previous_content = content

        return minimal_sources

    def chunk(
        self, paths: List[str],
        save_directory: str = "data/processed") -> None:
        """Persist chunk texts and validated locations as JSON."""

        output_path = Path(save_directory) / "chunked_data.json"
        temporary_path = output_path.with_suffix(".json.tmp")
        project_root = Path.cwd().resolve()
        total_chunks = 0

        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with temporary_path.open("w", encoding="utf-8") as output:

                output.write("[\n")

                for raw_path in tqdm(
                    paths, desc="Chunking files", unit="file"):

                    path = Path(raw_path)
                    splitter = self.splitters.get(path.suffix.lower())
                    if splitter is None:
                        continue

                    try:
                        file_path = path.resolve().relative_to(
                            project_root).as_posix()

                        # newline="" preserves original CRLF character offsets.
                        with path.open(
                            "r", encoding="utf-8", newline="") as f:
                            original_text = f.read()

                        if not original_text.strip():
                            continue

                        chunks = [
                            doc
                            for doc in splitter.create_documents(
                                [original_text]
                            )
                            if doc.page_content
                        ]
                        sources = self.make_minimal_source(
                            file_path, original_text, chunks
                        )

                        for doc, source in zip(chunks, sources):
                            if total_chunks:
                                output.write(",\n")
                            json.dump(
                                {"text": doc.page_content,
                                 "source": source.model_dump()},
                                output,
                                ensure_ascii=False,
                            )
                            total_chunks += 1

                    except (OSError, UnicodeError, ValueError) as exc:
                        tqdm.write(f"Skipping {raw_path}: {exc}")

                output.write("\n]\n")
            temporary_path.replace(output_path)
            tqdm.write(f"Saved {total_chunks} chunks to {output_path}")
        except OSError as exc:
            tqdm.write(f"Could not write chunk data: {exc}")
