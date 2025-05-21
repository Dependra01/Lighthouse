# embedding_model_runner.py

# embedding_model_runner.py
import sys
import json
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

question = sys.argv[1]
embedding = model.encode(question).tolist()
print(json.dumps(embedding))
