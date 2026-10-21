# from .models import MinimalSource
from parser import Parser
from chunker import Chunker
from indexer import Indexer
from indexer import Indexer
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

indexer = Indexer(f"{save_directory}/chunked_data.json")
# print(indexer.load_chunks())

# indexer = Indexer(f"{save_directory}/chunked_data.json")

indexer.index()


# print(corpus_tokens)




