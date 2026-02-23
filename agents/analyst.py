import ollama
import requests
import json
from urllib.parse import urlencode
import os
import re
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Analyst:
    def __init__(self):
        # Using the model you pulled earlier
        self.model = "phi4-mini"
        self.search_api_key = os.getenv("SEARCH_API_KEY", "")
        self.search_engine_id = os.getenv("SEARCH_ENGINE_ID", "")

        # Debug logging for API key and search engine ID
        if not self.search_api_key:
            logging.warning("SEARCH_API_KEY is not set or empty.")
        else:
            logging.info("SEARCH_API_KEY successfully retrieved.")

        if not self.search_engine_id:
            logging.warning("SEARCH_ENGINE_ID is not set or empty.")
        else:
            logging.info("SEARCH_ENGINE_ID successfully retrieved.")

    def validate_input(self, input_data):
        """Validate and preprocess user input."""
        if not input_data or not isinstance(input_data, str):
            raise ValueError("Input must be a non-empty string.")
        # Check if input is numeric but ambiguous
        if re.match(r"^\d+$", input_data):
            return "Ambiguous", input_data
        # Default to general input
        return "General", input_data

    def ask_phi(self, prompt, system_msg="You are a helpful analyst."):
        """Helper to get a response from local Phi-4."""
        try:
            response = ollama.chat(
                model=self.model,
                messages=[
                    {'role': 'system', 'content': system_msg},
                    {'role': 'user', 'content': prompt}
                ]
            )
            return response['message']['content']
        except Exception as e:
            logging.error(f"Error in ask_phi: {e}")
            return "I'm sorry, I encountered an error while processing your request."

    def web_search(self, query):
        """Standard Google Search retrieval with enhanced error handling."""
        logging.info(f"🔍 Analyst is searching the web for: {query}")
        encoded_query = urlencode({"q": query})
        url = f"https://www.googleapis.com/customsearch/v1?{encoded_query}&key={self.search_api_key}&cx={self.search_engine_id}"
        try:
            r = requests.get(url)
            r.raise_for_status()
            items = r.json().get("items", [])
            if not items:
                logging.warning("No results found.")
                return "No results found."
            # We only need the snippets for the model to 'read'
            return "\n".join([f"- {i['title']}: {i['snippet']}" for i in items[:3]])
        except requests.exceptions.RequestException as e:
            logging.error(f"Error during web search: {e}")
            return "Search failed due to a network error."
        except KeyError:
            logging.error("Unexpected response format from Google API.")
            return "Search failed due to unexpected response format."

    def validate_response(self, response, expected_keywords=None):
        """Validate the model's response to ensure it is relevant and clear."""
        if not response or not isinstance(response, str):
            logging.warning("Response is empty or invalid.")
            return False, "I'm sorry, I couldn't generate a valid response. Could you rephrase your question?"

        if expected_keywords:
            # Check if the response contains at least one of the expected keywords
            if not any(keyword.lower() in response.lower() for keyword in expected_keywords):
                logging.warning("Response does not contain expected keywords.")
                return False, "The response seems unrelated to your query. Could you clarify your request?"

        return True, response

    def run(self, input_data):
        try:
            logging.info(f"🧠 Analyst (Phi-4) is processing: {input_data[:50]}...")

            # Validate input
            input_type, processed_input = self.validate_input(input_data)
            if input_type == "Ambiguous":
                clarification_prompt = f"The user input '{input_data}' seems ambiguous. Could you clarify if this is a ZIP code, a year, or something else?"
                clarification = self.ask_phi(clarification_prompt, "You are a helpful assistant. Provide clarification.")
                return f"Clarification needed: {clarification}"

            logging.info("📝 General input detected.")

            # 1. THOUGHT PHASE: Ask Phi-4 if it needs external data
            decision_prompt = f"""
            The user input is '{input_data}'. Do you have enough internal knowledge to answer this accurately, or do you need a web search?
            Respond with ONLY 'SEARCH' or 'ANALYZE'.
            """
            decision = self.ask_phi(decision_prompt).strip().upper()
            logging.info(f"Decision: {decision}")

            # 2. ACTION PHASE
            context = ""
            if "SEARCH" in decision:
                # Let Phi-4 generate a better search query than the raw user input
                query_gen = self.ask_phi(f"Generate a search query for: {input_data}")
                logging.info(f"Generated Query: {query_gen}")
                context = self.web_search(query_gen)

            # 3. SYNTHESIS PHASE: Final output with or without search data
            final_prompt = f"Using this context: {context}\n\nAnswer this: {input_data}"
            raw_response = self.ask_phi(final_prompt, "You are a data analyst. Provide a concise, factual report.")

            # Validate the response
            is_valid, validated_response = self.validate_response(raw_response, expected_keywords=["weather", "forecast", "temperature"])
            if not is_valid:
                return validated_response

            return validated_response
        except ValueError as ve:
            logging.error(f"Validation error: {ve}")
            return str(ve)
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            return "An unexpected error occurred while processing your request."

# Usage
# analyst = Analyst()
# print(analyst.run("What is the current stock price of Nvidia?"))