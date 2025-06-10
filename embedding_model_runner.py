# embedding_model_runner.py

# embedding_model_runner.py
import sys
import json
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L12-v2')

def encode(text):
    return model.encode(text, convert_to_numpy=True).tolist()

if __name__ == "__main__":
    input_text = sys.stdin.read()  # <-- Accept from stdin
    embedding = encode(input_text)
    print(json.dumps(embedding))