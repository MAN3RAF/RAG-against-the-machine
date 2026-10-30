# from .models import MinimalSource
from parser import Parser
from chunker import Chunker
from ragbm25 import RagBm25
from ragbm25 import RagBm25
import bm25s
from sys import argv


repo_root = "/home/lsebar/work/RAG-against-the-machine/vllm-0.10.1"

parser = Parser(repo_root)
key, input = parser.parse_input(argv[1:])

paths = parser.get_all_paths()
save_directory = "data/processed"

print(f"Found {len(paths)} files")

chunker = Chunker(max_chunk_size=2000)
chunker.chunk(
    paths=paths,
    save_directory=save_directory
)

rag = RagBm25(f"{save_directory}/chunked_data.json")
# print(indexer.load_chunks())

# indexer = Indexer(f"{save_directory}/chunked_data.json")

rag.index()

# hits = rag.retrieve_hits("What is Cmake?")

# for hit in hits:
#     print(hit["score"])
#     print(hit["text"])
#     print(hit["source"].model_dump())

# results = rag.retrieve(
#     "Hwo to use Cmake?",
#     k=5,
# )

# for source in results:
#     print(source.model_dump())

# print(corpus_tokens)


# code_output = rag.search_dataset(
#     dataset_path="datasets_public/public/UnansweredQuestions/dataset_code_public.json",
#     k=5,
# )

# print("Code results:", code_output)

# docs_output = rag.search_dataset(
#     dataset_path="datasets_public/public/UnansweredQuestions/dataset_docs_public.json",
#     k=5,
# )

# print("Documentation results:", docs_output)
