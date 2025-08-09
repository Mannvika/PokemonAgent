import sentence_transformers as st
import chromadb
import asyncio
from langchain_community.llms import Ollama
from langchain.agents import AgentExecutor, create_json_chat_agent
from langchain_core.tools import tool
from langchain import hub
import discord

@tool
def search_database(query):
    """
    Searches a database for information about Pokémon characters, towns, and lore.
    Use this to answer any question about the Pokémon world. Provide a specific
    and detailed query as input.
    """
    print(f"Searching database for query: {query}")
    chromadb_client = chromadb.PersistentClient(path="chroma_db")
    collection = chromadb_client.get_collection(name="pokemon_towns")

    encoder = st.SentenceTransformer('all-MiniLM-L6-v2')
    query_embedding = encoder.encode(query)

    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=5
    )

    return "\n\n".join(results['documents'][0]) if results.get('documents') else "No information found."

class DiscordClient(discord.Client):

    def __init__(self, agent_executor, **options):
        super().__init__(**options)
        self.agent_executor = agent_executor

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')
    
    async def on_message(self, message):
        if message.author == self.user:
            return
        
        if message.content.startswith('!ask'):
            question = message.content[len('!ask '):].strip()
            await message.channel.send(f'You asked: {question}\n Thinking...')

            try:
                def run_blocking_agent():
                    return self.agent_executor.invoke({"input": question})

                result = await asyncio.to_thread(run_blocking_agent)
                answer = result.get('output', 'No answer found.')
            except Exception as e:
                print(f"Error processing question: {str(e)}")
                answer = f"Error processing the question: {str(e)}"

            await message.channel.send(f'Answer: {answer}')

def setup_agent():
    tools = [search_database]
    prompt = hub.pull("hwchase17/react-chat-json")
    llm = Ollama(
        model="llama3:8b",
        temperature=0.2,
    )

    agent = create_json_chat_agent(llm, tools, prompt=prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, handle_parsing_errors=True, verbose=True)
    return agent_executor

if __name__ == '__main__':
    pokemon_agent_executor = setup_agent()
    intents = discord.Intents.default()
    intents.message_content = True    
    client = DiscordClient(agent_executor=pokemon_agent_executor, intents=intents)
    
    with open("api", "r") as file:
        key = file.read().strip()

    client.run(key)