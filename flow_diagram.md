# Updated Orchestrator Agent Workflow

```mermaid
graph TD
    A[User Prompt] --> B[Orchestrator (Llama 3.2)]
    B --> C[Plan Task: ANALYSIS, CODE, or BOTH]
    C -->|ANALYSIS| D[Analyst (Phi-4)]
    C -->|CODE| E[Coder (Qwen)]
    C -->|BOTH| D
    C -->|BOTH| E
    D --> F[Analyst Report]
    E --> G[Coder Output]
    F --> H[Synthesis by Orchestrator]
    G --> H
    H --> I[Final User-Friendly Response]
    I --> J[Output Delivered to User]
```
