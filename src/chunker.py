from models import MinimalSource
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter, Language
from langchain_core.documents import Document


class Chunker:
    def __init__(self, max_chunk_size):
        
        self.max_chunk_size = max_chunk_size


    def make_minimal_source(self, file_path: str, chunks: list[Document]) -> list[MinimalSource]:
        minimal_sources = []

        for chunk in chunks:
            content = chunk.page_content

            first_char_index = chunk.metadata.get("start_index", 0)
            last_char_index = first_char_index + len(content)

            # print(f"--- Chunk {i+1} ---")
            # print("Character Boundaries:"
            # f"[{first_char_index} to {last_char_index}]")
            # print(f"Excerpt: {content[:60]}...")

            minimal_sources.append(
                MinimalSource(
                    file_path=file_path,
                    first_character_index=first_char_index,
                    last_character_index=last_char_index
                )
            )
            
        return minimal_sources


    def chunk(self, paths: List[str]) -> List[list[MinimalSource]]:

        res = []

        for path in paths:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = f.read()

                    if path.endswith(".py"):
                        splitter = RecursiveCharacterTextSplitter.from_language(
                            language=Language.PYTHON,
                            chunk_size=self.max_chunk_size,
                            chunk_overlap=100, #Fixed: 5% of 2000 characters, 0.05*2000=100
                            add_start_index=True
                        )

                    elif path.endswith(".md"):
                        splitter = RecursiveCharacterTextSplitter.from_language(
                            language=Language.MARKDOWN,
                            chunk_size=self.max_chunk_size,
                            chunk_overlap=100, #Fixed: 5% of 2000 characters, 0.05*2000=100
                            add_start_index=True
                        )

                    elif path.endswith(".txt"):
                        splitter = RecursiveCharacterTextSplitter(
                            chunk_size=self.max_chunk_size,
                            chunk_overlap=100, #Fixed: 5% of 2000 characters, 0.05*2000=100
                            add_start_index=True
                        )

                    chunks = splitter.create_documents([data])

                    res.extend(self.make_minimal_source(path, chunks))

            except Exception as e: 
                print(e)
        
        print(res)
        
        return res






