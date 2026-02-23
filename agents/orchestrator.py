import ollama
import json
from analyst import Analyst
from coder import Coder

class Orchestrator:
    def __init__(self):
        # The 'Brain' model for planning and synthesis
        self.model = "llama3.2"
        self.analyst = Analyst()
        self.coder = Coder()

    def run(self, user_prompt):
        print(f"\n🚀 Orchestrator (Llama 3.2) received: '{user_prompt}'")
        
        # --- PHASE 1: PLANNING ---
        # We ask the model to return a structured JSON plan
        plan_prompt = f"""
        User Request: {user_prompt}
        
        Task: Decide if this request needs an 'ANALYSIS' (research/data), a 'CODE' (programming), or 'BOTH'.
        Respond with ONLY a JSON object: {{"type": "ANALYSIS"|"CODE"|"BOTH", "reason": "why"}}
        """
        
        response = ollama.chat(model=self.model, messages=[{'role': 'user', 'content': plan_prompt}])
        # Note: In production, use a JSON parser. For this example, we'll assume valid output.
        decision = response['message']['content']
        print(f"📋 Decision: {decision}")

        # --- PHASE 2: DELEGATION ---
        results = []
        
        if "ANALYSIS" in decision or "BOTH" in decision:
            # Task the Analyst (Phi-4)
            analysis_result = self.analyst.run(user_prompt)
            results.append(f"ANALYST REPORT: {analysis_result}")

        if "CODE" in decision or "BOTH" in decision:
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