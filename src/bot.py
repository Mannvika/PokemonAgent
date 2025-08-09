import sentence_transformers as st
import chromadb
import requests
import json
from langchain_community.llms import Ollama
from langchain.agents import AgentExecutor, Tool
from langchain_core.tools import tool
from langchain import hub
import discord

@tool
def search_database(self, query):
    chromadb_client = chromadb.PersistentClient(path="chroma_db")
    collection = chromadb_client.get_collection(name="pokemon_towns")

    encoder = st.SentenceTransformer('all-MiniLM-L6-v2')
    query_embedding = encoder.encode(query)

    result = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=5
    )

    return result['documents'][0] if result['documents'] else []

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


    
    def invoke_llm(self, prompt):
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

        if response.status_code == 200:
            return response.json().get("response", "")
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return ""
        
    def parse_action(self, llm_response):
        if "search_database(" in llm_response:
            start = llm_response.index("search_database(") + len("search_database(")
            end = llm_response.index(")", start)
            query = llm_response[start:end].strip('"')
            return {"action": "search_database", "query": query}
        elif "final_answer(" in llm_response:
            start = llm_response.index("final_answer(") + len("final_answer(")
            end = llm_response.index(")", start)
            answer = llm_response[start:end].strip('"')
            return {"action": "final_answer", "answer": answer}
        else:
            return {"action": "unknown", "response": llm_response}

    def process_question(self, question):
        max_iterations = 3
        accumulated_context = set()

        initial_context = self.search_database(question)
        for doc in initial_context:
            accumulated_context.add(doc)

        for i in range(max_iterations):
            prompt = self.create_agent_prompt(question, accumulated_context)
            print(f"Iteration {i + 1}: {prompt}")
            llm_response = self.invoke_llm(prompt)
            print(f"LLM Response: {llm_response}")
            action = self.parse_action(llm_response)

            if "final_answer" in action:
                print(f"Final Answer Action: {action}")
                return action.get("answer", "No final answer provided.")
            elif "search_database" in action:
                query = action["query"]
                if query:
                    new_context = self.search_database(query)
                    for doc in new_context:
                        accumulated_context.add(doc)
                else:
                    break
            else:
                break

        return self.synthesize_final_answer(accumulated_context)
    
    def synthesize_final_answer(self, accumulated_context):
        if not accumulated_context:
            return "No information found to answer the question."

        # Combine all context into a single string
        combined_context = "\n\n".join(accumulated_context)
        return f"Based on the information gathered:\n{combined_context}\nI cannot provide a final answer at this time."


    def create_agent_prompt(self, question, accumulated_context: list[str]):
        context_text = "\n\n".join(accumulated_context)
        return f"""
        You are a helpful Pokémon expert. Your goal is to answer the user's question as completely as possible.
        You have access to a tool called `search_database`.

        To answer the question, you must follow this cycle:
        1. **Thought:** First, think about what you need to do. Do you have enough information? If not, what specific information do you need next?
        2. **Action:** If you need more information, use the `search_database` tool with a specific query. If you have enough information to answer the question, use the tool `final_answer`.

        Here is the format for your action:
        `search_database(query="your specific search query")`
        OR
        `final_answer(answer="your complete, final answer to the user")`

        Begin!

        User Question: {question}
        Initial Context:
        {context_text}
        """

intents=discord.Intents.default()
intents.message_content = True

client = DiscordClient(intents=intents)
client.run('')