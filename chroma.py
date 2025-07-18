import chromadb
import sqlite3

with sqlite3.connect('pokemon.db') as connection:
    cursor = connection.cursor()
    cursor.execute('SELECT name, lore FROM towns')
    towns = cursor.fetchall()

client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_or_create_collection(name="pokemon_towns")

ids = [town[0] for town in towns]
documents = [town[1] for town in towns]
metdatas = [{"name": town[0]} for town in towns]

collection.add(
    documents=documents,
    metadatas=metdatas,
    ids=ids
)

print(f"Added {len(towns)} towns to the ChromaDB collection.")
