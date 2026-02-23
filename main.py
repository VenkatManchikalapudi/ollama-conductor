import yaml
from agents.orchestrator import Orchestrator

def main():
    # 1. Initialize the Brain
    # The Orchestrator class should handle the internal creation 
    # of the Analyst and Coder instances.
    boss = Orchestrator()

    print("--- 2026 Local Agent System Active ---")
    print("Running on MacBook Air (Unified Memory Optimization)")
    
    while True:
        user_input = input("\nUser: ")
        if user_input.lower() in ['exit', 'quit']:
            break
            
        try:
            # 2. Let the Orchestrator manage the flow
            # It will plan (Llama 3.2), research (Phi-4), and code (Qwen 2.5)
            response = boss.run(user_input)
            
            print("\n" + "="*40)
            print("FINAL AGENT RESPONSE:")
            print("="*40)
            print(response)
            
        except Exception as e:
            print(f"❌ System Error: {e}")

if __name__ == "__main__":
    main()