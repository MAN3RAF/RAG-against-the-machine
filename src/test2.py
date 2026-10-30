from pathlib import Path
from ragbm25 import RagBm25

repo_root = Path(".")  # Change if your repo is elsewhere

rag = RagBm25()

question = "what is Cmake?"

hits = rag.retrieve_hits(
    question,
    k=5,
)

assert hits, "No matching chunks were retrieved."

print(f"Question: {question}")

for hit in hits:
    source = hit["source"]

    file_path = repo_root / source.file_path

    with file_path.open(
        "r", encoding="utf-8", newline=""
    ) as f:
        original_text = f.read()

    extracted_text = original_text[
        source.first_character_index:
        source.last_character_index
    ]

    assert extracted_text == hit["text"]
    assert len(hit["text"]) <= 2000

    print("File:", source.file_path)
    print("Score:", hit["score"])
    print(
        "Characters:",
        source.first_character_index,
        source.last_character_index,
    )
    print("Text:", hit["text"][:150])
    print("-" * 50)

print("All retrieved source positions are valid!")