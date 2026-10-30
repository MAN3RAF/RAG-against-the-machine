# from .models import MinimalSource
from parser import Parser
from chunker import Chunker
from ragbm25 import RagBm25
from ragbm25 import RagBm25
import bm25s


repo_root = "/home/lsebar/work/RAG-against-the-machine/vllm-0.10.1"

parser = Parser(repo_root)
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

# hits = rag.retrieve_hits("Who is Lachen Sebar?")

# for hit in hits:
#     print(hit["score"])
#     print(hit["text"])
#     print(hit["source"].model_dump())

results = rag.retrieve(
    "Who is Lahcen Sebar?",
    k=5,
)

for source in results:
    print(source.model_dump())

# print(corpus_tokens)




