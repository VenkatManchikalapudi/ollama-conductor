import ollama
import requests
import json
from urllib.parse import urlencode

class Analyst:
    def __init__(self):
        # Using the model you pulled earlier
        self.model = "phi4-mini"
        self.search_api_key = "YOUR_API_KEY"
        self.search_engine_id = "YOUR_CX"

    def ask_phi(self, prompt, system_msg="You are a helpful analyst."):
        """Helper to get a response from local Phi-4."""
        response = ollama.chat(
            model=self.model,
            messages=[
                {'role': 'system', 'content': system_msg},
                {'role': 'user', 'content': prompt}
            ]
        )
        return response['message']['content']

    def web_search(self, query):
        """Standard Google Search retrieval."""
        print(f"🔍 Analyst is searching the web for: {query}")
        encoded_query = urlencode({"q": query})
        url = f"https://www.googleapis.com/customsearch/v1?{encoded_query}&key={self.search_api_key}&cx={self.search_engine_id}"
        try:
            r = requests.get(url)
            r.raise_for_status()
            items = r.json().get("items", [])
            # We only need the snippets for the model to 'read'
            return "\n".join([f"- {i['title']}: {i['snippet']}" for i in items[:3]])
        except Exception as e:
            return f"Search failed: {str(e)}"

    def run(self, input_data):
        print(f"🧠 Analyst (Phi-4) is processing: {input_data[:50]}...")

        # 1. THOUGHT PHASE: Ask Phi-4 if it needs external data
        # Phi-4 is excellent at this 'reasoning' step.
        decision_prompt = f"""
        User Query: {input_data}
        Do you have enough internal knowledge to answer this accurately, or do you need a web search?
        Respond with ONLY 'SEARCH' or 'ANALYZE'.
        """
        decision = self.ask_phi(decision_prompt).strip().upper()

        # 2. ACTION PHASE
        context = ""
        if "SEARCH" in decision:
            # Let Phi-4 generate a better search query than the raw user input
            query_gen = self.ask_phi(f"Create a 5-word search query for: {input_data}")
            context = self.web_search(query_gen)
        
        # 3. SYNTHESIS PHASE: Final output with or without search data
        final_prompt = f"Using this context: {context}\n\nAnswer this: {input_data}"
        return self.ask_phi(final_prompt, "You are a data analyst. Provide a concise, factual report.")

# Usage
# analyst = Analyst()
# print(analyst.run("What is the current stock price of Nvidia?"))