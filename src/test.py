# from .models import MinimalSource
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter, Language
from chunker import Chunker




c = Chunker()

c.chunk(["/home/lsebar/work/RAG-against-the-machine/README.md", "src/parser.py", "text.txt"])






