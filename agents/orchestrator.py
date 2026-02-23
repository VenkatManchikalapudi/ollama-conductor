import ollama
import json
from analyst import Analyst
from coder import Coder
import logging

class Orchestrator:
    def __init__(self):
        # The 'Brain' model for planning and synthesis
        self.model = "llama3.2"
        self.analyst = Analyst()
        self.coder = Coder()

    def run(self, user_prompt):
        logging.info(f"\n🚀 Orchestrator (Llama 3.2) received: '{user_prompt}'")
        
        # --- PHASE 1: PLANNING ---
        # We ask the model to return a structured JSON plan
        plan_prompt = f"""
        User Request: {user_prompt}
        
        Task: Decide if this request needs an 'ANALYSIS' (research/data), a 'CODE' (programming), or 'BOTH'.
        Respond with ONLY a JSON object: {{"type": "ANALYSIS"|"CODE"|"BOTH", "reason": "why"}}
        """
        
        decision = None
        for attempt in range(3):  # Retry up to 3 times
            try:
                response = ollama.chat(model=self.model, messages=[{'role': 'user', 'content': plan_prompt}])
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
            # Task the Analyst (Phi-4)
            analysis_result = self.analyst.run(user_prompt)
            results.append(f"ANALYST REPORT: {analysis_result}")

        if "CODE" in decision.get("type", "") or "BOTH" in decision.get("type", ""):
            # Task the Coder (Qwen)
            code_result = self.coder.run(user_prompt)
            results.append(f"CODER OUTPUT: {code_result}")

        # --- PHASE 3: SYNTHESIS ---
        # Send all worker results back to Llama 3.2 for a final user-friendly summary
        synthesis_prompt = f"""
        Original User Request: {user_prompt}
        
        Expert Findings:
        {chr(10).join(results)}
        
        Task: Create a final, cohesive response for the user in simple English.
        """
        
        final_answer = ollama.chat(model=self.model, messages=[{'role': 'user', 'content': synthesis_prompt}])
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