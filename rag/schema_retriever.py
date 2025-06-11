# rag/schema_retriever.py

import os
import json
import faiss
import numpy as np
import subprocess

SCHEMA_JSON_PATH = "data/schema_chunks.json"
SCHEMA_INDEX_PATH = "data/schema_vector_store.faiss"
SCHEMA_LABELS_PATH = "data/schema_labels.json"

# Reuse embedding subprocess safely
def encode_text(text):
    result = subprocess.run(
        ['python', 'embedding_model_runner.py', text],
        capture_output=True, text=True
    )
    return np.array(json.loads(result.stdout))

def build_schema_vector_store():
    with open(SCHEMA_JSON_PATH, "r") as f:
        chunks = json.load(f)

    texts = [chunk["content"] for chunk in chunks]
    labels = [chunk["label"] for chunk in chunks]
    embeddings = np.array([encode_text(text) for text in texts])

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    faiss.write_index(index, SCHEMA_INDEX_PATH)

    with open(SCHEMA_LABELS_PATH, "w") as f:
        json.dump(labels, f)

def retrieve_schema_chunks(query: str, top_k: int = 3):
    if not os.path.exists(SCHEMA_INDEX_PATH):
        build_schema_vector_store()

    with open(SCHEMA_JSON_PATH, "r") as f:
        chunks = json.load(f)

    index = faiss.read_index(SCHEMA_INDEX_PATH)
    query_vec = encode_text(query).reshape(1, -1)
    distances, indices = index.search(query_vec, k=top_k)

    return [chunks[i]["content"] for i in indices[0]]
