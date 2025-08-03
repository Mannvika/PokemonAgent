import chromadb
import sqlite3

with sqlite3.connect('./pokemon.db') as connection:
    cursor = connection.cursor()
    cursor.execute('SELECT name, lore FROM towns')
    towns = cursor.fetchall()

    cursor.execute('SELECT name, lore FROM trainers')
    trainers = cursor.fetchall()

client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_or_create_collection(name="pokemon_towns")

ids = [town[0] for town in towns]
documents = [town[1] for town in towns]
metdatas = [{"name": town[0]} for town in towns]

for trainer in trainers:
    ids.append(trainer[0])
    documents.append(trainer[1])
    metdatas.append({"name": trainer[0], "type": "trainer"})

collection.add(
    documents=documents,
    metadatas=metdatas,
    ids=ids
)

print(f"Added {len(towns)} towns to the ChromaDB collection.")
