import yaml
import asyncio
import logging
from agents.orchestrator import Orchestrator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def main():
    # 1. Initialize the Brain
    # The Orchestrator class should handle the internal creation 
    # of the Analyst and Coder instances.
    boss = Orchestrator()

    logging.info("--- 2026 Local Agent System Active ---")
    logging.info("Running on MacBook Air (Unified Memory Optimization)")
    
    while True:
        user_input = input("\nUser: ")
        if user_input.lower() in ['exit', 'quit']:
            break
            
        try:
            # 2. Let the Orchestrator manage the flow
            # It will plan (Llama 3.2), research (Phi-4), and code (Qwen 2.5)
            response = await boss.run(user_input)
            
            logging.info("\n" + "="*40)
            logging.info("FINAL AGENT RESPONSE:")
            logging.info("="*40)
            logging.info(response)
            
        except Exception as e:
            logging.error(f"❌ System Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())