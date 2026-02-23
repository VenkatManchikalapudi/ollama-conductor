# Multi-Agent Orchestrator

## Overview

The Multi-Agent Orchestrator is a Python-based system that coordinates tasks between multiple agents to handle complex workflows. It uses:

- **Orchestrator (Llama 3.2)**: Plans and delegates tasks.
- **Analyst (Phi-4)**: Performs data analysis and research with enhanced input validation, response guardrails, and error handling.
- **Coder (Qwen)**: Generates code based on user requirements.

All models are locally installed and managed using **Ollama**, ensuring fast and secure processing without relying on external APIs.

## Features

- Task planning and delegation.
- Integration with local models (Ollama).
- Web search capabilities for data enrichment.
- Python script generation for coding tasks.
- **Enhanced Guardrails**:
  - Input validation to ensure clarity and prevent errors.
  - Response validation to ensure relevance and quality.
  - Fallback mechanisms for ambiguous or invalid inputs.

## Workflow

1. **User Prompt**: The user provides a query.
2. **Input Refinement**: The Orchestrator refines the input for clarity and specificity.
3. **Task Planning**: The Orchestrator decides if the task requires analysis, coding, or both.
4. **Task Delegation**: Tasks are delegated to the Analyst and/or Coder agents.
5. **Validation and Iteration**: The Orchestrator validates agent responses and iterates if necessary.
6. **Synthesis**: Results are combined into a final user-friendly response.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/VenkatManchikalapudi/multiAgent-Agent.git
   ```
2. Navigate to the project directory:
   ```bash
   cd multiAgent-Agent
   ```
3. Set up a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the Orchestrator:

```bash
python3 agents/orchestrator.py
```

## Project Structure

- `agents/`
  - `orchestrator.py`: Main orchestrator logic.
  - `analyst.py`: Analyst agent logic with guardrails for input validation and response handling.
  - `coder.py`: Coder agent logic.
- `config.yaml`: Configuration file for models.
- `flow_diagram.md`: Mermaid.js flow diagram of the workflow.
- `.env`: Environment variables for API keys and model configurations.

## Environment Variables

The `.env` file should contain the following variables:

- `SEARCH_API_KEY`: Your Google Custom Search API key.
- `SEARCH_ENGINE_ID`: Your Google Custom Search Engine ID.

Example `.env` file:

```
SEARCH_API_KEY=your_api_key
SEARCH_ENGINE_ID=your_search_engine_id
```

## Contributing

Feel free to submit issues or pull requests to improve the project.

## License

This project is licensed under the MIT License.
