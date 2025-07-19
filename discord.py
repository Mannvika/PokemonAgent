import sentence_transformers as st
import chromadb
import requests
import json
from langchain_community.llms import Ollama

#llm = Ollama(model="llama3:8b")
user_question = ""
encoder = st.SentenceTransformer('all-MiniLM-L6-v2')

chromadb_client = chromadb.PersistentClient(path="chroma_db")
collection = chromadb_client.get_collection(name="pokemon_towns")


user_question = input("Please enter your question about Pokémon towns: ")

query_embedding = encoder.encode(user_question)

result = collection.query(
    query_embeddings=[query_embedding.tolist()],
    n_results=5
)

prompt = f"""You are a helpful assistant that answers questions about Pokémon towns.
You will be given a question and context from a database. Provide an answer based ONLY on the provided context.

Question: {user_question}
"""

prompt += "\nContext:\n"
for i, document in enumerate(result['documents'][0]):
    prompt += f"{i + 1}. {document}\n"

url = "http://localhost:11434/api/generate"
headers = {
    "Content-Type": "application/json"
}
data = {
    "model": "llama3:8b",
    "prompt": prompt,
    "stream": False,
}

response = requests.post(url, headers=headers, data=json.dumps(data))

print("Thinking...")
#response = llm.invoke(prompt)
#print(response)

if response.status_code == 200:
    answer_string = response.json().get("response", "No answer found.")
    print("\n--- Answer ---")
    print(answer_string.strip())
else:
    print(f"Error: {response.status_code} - {response.text}")