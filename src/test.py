# from .models import MinimalSource
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter, Language
from chunker import Chunker
from parser import Parser


p = Parser
c = Chunker(max_chunk_size=2000)

paths = p.get_all_paths("/home/lsebar/work/RAG-against-the-machine/vllm-0.10.1")
c.chunk(paths)






