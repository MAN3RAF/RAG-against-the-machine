import inspect
import json
from typing import get_type_hints
from parser import Parser
from chunker import Chunker
from ragbm25 import RagBm25
from typing import List


class CLI:
    """Dispatch terminal commands to methods with matching names."""

    def __init__(self, cli: List[str]):
        self.cli = cli

    def index(self, target_path: str = "vllm-0.10.1", max_chunk_size: int = 2000):
        """Parse, chunk and index the vLLM repository."""

        parser = Parser(target_path)
        paths = parser.get_all_paths()

        chunker = Chunker(max_chunk_size=max_chunk_size)
        chunker.chunk(paths)

        rag = RagBm25()
        count = rag.index()

        print(f"Indexed {count} chunks.")

    def search(self, query: str, k: int = 5):
        """Search the existing BM25 index."""

        rag = RagBm25()
        hits = rag.retrieve_hits(query, k=k)

        results = [
            {
                "text": hit["text"],
                "source": hit["source"].model_dump(),
                "score": hit["score"],
            }
            for hit in hits
        ]

        print(json.dumps(results, indent=2, ensure_ascii=False))

    def process_cli(self):
        """Convert terminal arguments into a method call."""

        if not self.cli:
            raise ValueError(
                "Usage: python -m src <index|search> [arguments]"
            )

        command, *arguments = self.cli

        # Only expose implemented commands.
        allowed_commands = {"index", "search"}

        if command not in allowed_commands:
            raise ValueError(f"Unknown command: {command}")

        method = getattr(self, command)
        method_signature = inspect.signature(method)
        method_types = get_type_hints(method)

        positional = []
        keyword = {}

        i = 0

        while i < len(arguments):
            argument = arguments[i]

            if argument.startswith("--"):
                name = argument[2:].replace("-", "_")

                if name not in method_signature.parameters:
                    raise ValueError(f"Unknown option: {argument}")

                if (
                    i + 1 >= len(arguments)
                    or arguments[i + 1].startswith("--")
                ):
                    raise ValueError(f"Missing value for {argument}")

                if name in keyword:
                    raise ValueError(f"Duplicate option: {argument}")

                keyword[name] = arguments[i + 1]
                i += 2
            else:
                positional.append(argument)
                i += 1

        # Check which arguments the method accepts.
        bound = method_signature.bind(*positional, **keyword)

        # Terminal arguments are strings; convert typed parameters.
        for name, value in bound.arguments.items():
            expected_type = method_types.get(name)

            if expected_type is int:
                try:
                    bound.arguments[name] = int(value)
                except ValueError as exc:
                    raise ValueError(
                        f"{name} must be an integer"
                    ) from exc

        return method(*bound.args, **bound.kwargs)