# rag/semantic_retriever.py
import faiss
import numpy as np
import os
import pickle
import subprocess
import json
from data.qa_bank import canonical_qa_bank
from utils.text_utils import normalize_question



VECTOR_STORE_PATH = "data/qa_vector_store.faiss"
QA_EMBEDDINGS_PATH = "data/qa_embeddings.pkl"


# Load model once
def encode_text(text):
    result = subprocess.run(
        ["python", "embedding_model_runner.py", text],
        capture_output=True, text=True
    )
    return np.array(json.loads(result.stdout))

def build_vector_store():
    questions = [normalize_question(item["question"]) for item in canonical_qa_bank]
    embeddings = np.array([encode_text(q) for q in questions])

    # Save FAISS index
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    faiss.write_index(index, VECTOR_STORE_PATH)

    # Save original questions so we can map matches later
    with open(QA_EMBEDDINGS_PATH, "wb") as f:
        pickle.dump(questions, f)

def retrieve_similar_question(query: str, threshold: float = 0.85):
    if not os.path.exists(VECTOR_STORE_PATH):
        build_vector_store()

    index = faiss.read_index(VECTOR_STORE_PATH)
    with open(QA_EMBEDDINGS_PATH, "rb") as f:
        stored_questions = pickle.load(f)
    norm_query = normalize_question(query)
    query_vec = encode_text(norm_query).reshape(1, -1)
    distances, indices = index.search(query_vec, k=1)

    match_index = indices[0][0]
    score = 1 - distances[0][0]  # convert L2 to similarity
    print(f"🧠 Matching:\n   Query   → {norm_query}\n   Against → {stored_questions[match_index]}\n   Score   → {score:.4f}")


    if score >= threshold:
        match_question = stored_questions[match_index]
        for item in canonical_qa_bank:
            if item["question"].strip().lower() == match_question.strip().lower():
                return item["sql"]
    return None
