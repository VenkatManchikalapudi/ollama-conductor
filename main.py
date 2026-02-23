import yaml
import asyncio
import logging
import argparse
from agents.orchestrator import Orchestrator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def main(prompt=None):
    # 1. Initialize the Brain
    # The Orchestrator class should handle the internal creation 
    # of the Analyst and Coder instances.
    boss = Orchestrator()

    logging.info("--- 2026 Local Agent System Active ---")
    logging.info("Running on MacBook Air (Unified Memory Optimization)")

    if prompt:
        try:
            # Pass the prompt directly to the Orchestrator
            response = await boss.run(prompt)
            logging.info("\n" + "="*40)
            logging.info("FINAL AGENT RESPONSE:")
            logging.info("="*40)
            logging.info(response)
        except Exception as e:
            logging.error(f"❌ System Error: {e}")
    else:
        while True:
            user_input = input("\nUser: ")
            if user_input.lower() in ['exit', 'quit']:
                break

            try:
                response = await boss.run(user_input)
                logging.info("\n" + "="*40)
                logging.info("FINAL AGENT RESPONSE:")
                logging.info("="*40)
                logging.info(response)
            except Exception as e:
                logging.error(f"❌ System Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Multi-Agent Orchestrator with a prompt.")
    parser.add_argument("--prompt", type=str, help="The prompt to pass to the Orchestrator.")
    args = parser.parse_args()

    asyncio.run(main(prompt=args.prompt))