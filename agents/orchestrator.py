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

    async def run(self, user_prompt):
        logging.info(f"\n🚀 Orchestrator (Llama 3.2) received: '{user_prompt}'")
        
        # --- PHASE 1: PLANNING ---
        plan_prompt = f"""
        User Request: {user_prompt}
        
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
            analysis_result = await asyncio.to_thread(self.analyst.run, user_prompt)
            results.append(f"ANALYST REPORT: {analysis_result}")

        if "CODE" in decision.get("type", "") or "BOTH" in decision.get("type", ""):
            code_result = await asyncio.to_thread(self.coder.run, user_prompt)
            results.append(f"CODER OUTPUT: {code_result}")

        # --- PHASE 3: SYNTHESIS ---
        synthesis_prompt = f"""
        Original User Request: {user_prompt}
        
        Expert Findings:
        {chr(10).join(results)}
        
        Task: Create a final, cohesive response for the user in simple English.
        """
        
        final_answer = await asyncio.to_thread(ollama.chat, model=self.model, messages=[{'role': 'user', 'content': synthesis_prompt}])
        return final_answer['message']['content']

if __name__ == "__main__":
    boss = Orchestrator()
    
    # Test with a multi-part query
    query = "Analyze the trend of AI agents in 2026 and write a Python script to track them."
    final_output = boss.run(query)
    
    print("\n" + "="*30)
    print("FINAL RESULT FROM AGENTS:")
    print("="*30)
    print(final_output)