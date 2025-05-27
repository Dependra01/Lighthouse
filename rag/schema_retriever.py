# rag/schema_retriever.py

import json
import faiss
import os
from sentence_transformers import SentenceTransformer
import numpy as np

SCHEMA_JSON_PATH = "data/schema_chunks.json"
VECTOR_STORE_PATH = "data/schema_vector_store.faiss"
CHUNK_LABELS_PATH = "data/schema_labels.json"

model = SentenceTransformer("all-MiniLM-L6-v2")

def build_schema_vector_store():
    with open(SCHEMA_JSON_PATH, "r") as f:
        chunks = json.load(f)
    
    texts = [chunk["content"] for chunk in chunks]
    labels = [chunk["label"] for chunk in chunks]
    embeddings = model.encode(texts, convert_to_numpy=True)

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    faiss.write_index(index, VECTOR_STORE_PATH)

    with open(CHUNK_LABELS_PATH, "w") as f:
        json.dump(labels, f)

def retrieve_schema_chunks(query: str, top_k: int = 3):
    if not os.path.exists(VECTOR_STORE_PATH):
        build_schema_vector_store()

    index = faiss.read_index(VECTOR_STORE_PATH)
    with open(CHUNK_LABELS_PATH, "r") as f:
        labels = json.load(f)
    with open(SCHEMA_JSON_PATH, "r") as f:
        chunks = json.load(f)

    query_embedding = model.encode([query], convert_to_numpy=True)
    distances, indices = index.search(query_embedding, top_k)

    return [chunks[i]["content"] for i in indices[0]]
