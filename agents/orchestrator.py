import ollama
import json
from .analyst import Analyst
from .coder import Coder
import logging
import asyncio

class Orchestrator:
    def __init__(self):
        # The 'Brain' model for planning and synthesis
        self.model = "llama3.2"
        self.analyst = Analyst()
        self.coder = Coder()

    async def validate_response(self, response, expected_keywords=None):
        """Validate the synthesized response to ensure it is relevant and clear."""
        if not response or not isinstance(response, str):
            logging.warning("Synthesized response is empty or invalid.")
            return False, "I'm sorry, I couldn't generate a valid response. Could you rephrase your question?"

        if expected_keywords:
            # Check if the response contains at least one of the expected keywords
            if not any(keyword.lower() in response.lower() for keyword in expected_keywords):
                logging.warning("Synthesized response does not contain expected keywords.")
                return False, "The response seems unrelated to your query. Could you clarify your request?"

        return True, response

    async def refine_input(self, user_prompt):
        """Refine the user input for clarity and specificity."""
        refinement_prompt = f"""
        The user provided the following input: "{user_prompt}".
        Task: Refine this input to make it clearer and more specific for analysis or coding tasks.
        Respond with the refined input only.
        """
        try:
            response = await asyncio.to_thread(ollama.chat, model=self.model, messages=[{'role': 'user', 'content': refinement_prompt}])
            refined_input = response['message']['content'].strip()
            logging.info(f"🔄 Refined Input: {refined_input}")
            return refined_input
        except Exception as e:
            logging.error(f"Error during input refinement: {e}")
            return user_prompt  # Fallback to the original input if refinement fails

    async def validate_and_iterate(self, agent, prompt, expected_keywords, max_attempts=3):
        """Validate the agent's response and iterate if the response is not good enough. Improve the input for retries."""
        for attempt in range(max_attempts):
            try:
                response = await asyncio.to_thread(agent.run, prompt)
                is_valid, validated_response = await self.validate_response(response, expected_keywords)
                if is_valid:
                    logging.info(f"✅ Valid response from {agent.__class__.__name__}: {validated_response}")
                    return validated_response
                logging.warning(f"Attempt {attempt + 1}: Invalid response from {agent.__class__.__name__}. Improving input and retrying...")

                # Improve the input for the next attempt
                improvement_prompt = f"""
                The agent provided the following response: "{response}".
                Task: Improve the original input "{prompt}" to make it clearer and more specific based on the agent's response.
                Respond with the improved input only.
                """
                try:
                    improvement_response = await asyncio.to_thread(ollama.chat, model=self.model, messages=[{'role': 'user', 'content': improvement_prompt}])
                    prompt = improvement_response['message']['content'].strip()
                    logging.info(f"🔄 Improved Input for Retry: {prompt}")
                except Exception as e:
                    logging.error(f"Error during input improvement: {e}")
            except Exception as e:
                logging.error(f"Error during agent interaction: {e}")
        logging.error(f"❌ {agent.__class__.__name__} failed to provide a valid response after {max_attempts} attempts.")
        return None

    async def run(self, user_prompt):
        logging.info(f"\n🚀 Orchestrator (Llama 3.2) received: '{user_prompt}'")

        # --- INPUT REFINEMENT PHASE ---
        refined_prompt = await self.refine_input(user_prompt)

        # --- PHASE 1: PLANNING ---
        plan_prompt = f"""
        User Request: {refined_prompt}
        
        Task: Decide if this request needs an 'ANALYSIS' (research/data), a 'CODE' (programming), or 'BOTH'.
        Respond with ONLY a JSON object: {{"type": "ANALYSIS"|"CODE"|"BOTH", "reason": "why"}}
        """
        
        decision = None
        for attempt in range(3):  # Retry up to 3 times
            try:
                response = await asyncio.to_thread(ollama.chat, model=self.model, messages=[{'role': 'user', 'content': plan_prompt}])
                decision = json.loads(response['message']['content'])
                logging.info(f"📋 Decision: {decision}")
                break
            except (json.JSONDecodeError, KeyError) as e:
                logging.warning(f"Attempt {attempt + 1}: Failed to parse JSON response. Retrying...")
        
        if decision is None:
            logging.error("❌ Planning phase failed after 3 attempts.")
            return "Error: Unable to process the request."

        # --- PHASE 2: DELEGATION ---
        results = []
        
        if "ANALYSIS" in decision.get("type", "") or "BOTH" in decision.get("type", ""):
            analysis_result = await self.validate_and_iterate(self.analyst, refined_prompt, expected_keywords=["data", "analysis", "report"])
            if analysis_result:
                results.append(f"ANALYST REPORT: {analysis_result}")

        if "CODE" in decision.get("type", "") or "BOTH" in decision.get("type", ""):
            code_result = await self.validate_and_iterate(self.coder, refined_prompt, expected_keywords=["code", "function", "script"])
            if code_result:
                results.append(f"CODER OUTPUT: {code_result}")

        # --- PHASE 3: SYNTHESIS ---
        synthesis_prompt = f"""
        Original User Request: {user_prompt}
        Refined Request: {refined_prompt}
        
        Expert Findings:
        {chr(10).join(results)}
        
        Task: Create a final, cohesive response for the user in simple English.
        """
        
        for attempt in range(3):  # Retry synthesis up to 3 times
            final_answer = await asyncio.to_thread(ollama.chat, model=self.model, messages=[{'role': 'user', 'content': synthesis_prompt}])
            is_valid, validated_response = await self.validate_response(final_answer['message']['content'], expected_keywords=["analysis", "code", "report"])
            if is_valid:
                return validated_response
            logging.warning(f"Attempt {attempt + 1}: Synthesized response validation failed. Retrying...")

        logging.error("❌ Synthesis phase failed after 3 attempts.")
        return "Error: Unable to generate a valid response. Please try again later."

if __name__ == "__main__":
    boss = Orchestrator()
    
    # Test with a multi-part query
    query = "Analyze the trend of AI agents in 2026 and write a Python script to track them."
    final_output = boss.run(query)
    
    print("\n" + "="*30)
    print("FINAL RESULT FROM AGENTS:")
    print("="*30)
    print(final_output)