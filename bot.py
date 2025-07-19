import sentence_transformers as st
import chromadb
import requests
import json
from langchain_community.llms import Ollama
import discord

class DiscordClient(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')
    
    async def on_message(self, message):
        if message.author == self.user:
            return
        
        if message.content.startswith('!ask'):
            question = message.content[len('!ask '):]
            await message.channel.send(f'You asked: {question}\n Thinking...')
            
            # Process the question and get an answer
            answer = self.process_question(question)
            await message.channel.send(f'Answer: {answer}')

    def process_question(self, question):
        #llm = Ollama(model="llama3:8b")
        user_question = ""
        encoder = st.SentenceTransformer('all-MiniLM-L6-v2')

        chromadb_client = chromadb.PersistentClient(path="chroma_db")
        collection = chromadb_client.get_collection(name="pokemon_towns")

        #user_question = input("Please enter your question about Pokémon towns: ")

        query_embedding = encoder.encode(question)

        result = collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=50
        )

        prompt = f"""You are a helpful assistant that answers questions about Pokémon towns.
        You will be given a question and context from a database. Provide an answer based ONLY on the provided context.

        Question: {question}
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
            return answer_string.strip()
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return "Sorry, I couldn't process your question at the moment."

intents=discord.Intents.default()
intents.message_content = True

client = DiscordClient(intents=intents)
client.run('MTM5NTkyNjYyMzI1NzEwNDQ2NA.GA5a8M.ddwfwdHBYXNbjVRSbtcjaw_liPgHxrS5MyR2w4')