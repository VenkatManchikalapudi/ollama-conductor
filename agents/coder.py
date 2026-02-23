import ollama

class Coder:
    def __init__(self):
        # Qwen 2.5 Coder is highly optimized for Python, Java, and JS
        self.model = "qwen2.5-coder:7b"

    def run(self, task_description):
        """
        Takes a specific coding task and returns structured code.
        """
        print(f"💻 Coder (Qwen) is generating code for: {task_description[:50]}...")

        # System prompt tells Qwen to skip the 'chatter' and focus on the code
        system_prompt = (
            "You are an expert Senior Software Engineer. "
            "Provide clean, efficient, and well-documented code. "
            "Always include a brief explanation of how the code works. "
            "Wrap your code in markdown blocks (```python ... ```)."
        )

        try:
            response = ollama.chat(
                model=self.model,
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': task_description}
                ],
                options={
                    "temperature": 0.2,  # Low temperature for precise, bug-free code
                    "num_ctx": 8192      # Larger context for complex scripts
                }
            )
            return response['message']['content']
        except Exception as e:
            return f"Coding error: {str(e)}"

# Usage:
# coder = Coder()
# print(coder.run("Write a Python script to scrape news headlines from a URL."))