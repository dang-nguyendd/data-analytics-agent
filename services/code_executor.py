import re
import pandas as pd
import matplotlib.pyplot as plt
import io
from contextlib import redirect_stdout

class CodeExecutor:
    def __init__(self, initial_df=None):
        # This dictionary is the "memory" of your environment.
        self.env = {
            "df": initial_df,
            "pd": pd,
            "plt": plt
        }

    def get_df(self):
        """Returns the current state of the DataFrame after AI modifications."""
        return self.env.get("df")

    def set_df(self, new_df):
        """Allows the UI to inject a completely new DataFrame (e.g., loading a new CSV)."""
        self.env["df"] = new_df

    def extract_code(self, ai_response: str) -> str:
        """Finds the python code block in the AI's markdown response."""
        match = re.search(r'```python\s*(.*?)\s*```', ai_response, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None

    def execute(self, ai_response: str) -> str:
        """Executes the extracted code and captures any print outputs."""
        code = self.extract_code(ai_response)
        
        if not code:
            return "No code found to execute."

        output_buffer = io.StringIO()
        
        try:
            with redirect_stdout(output_buffer):
                # Run the code inside our shared environment
                exec(code, self.env)
                
            console_output = output_buffer.getvalue()
            return f"Execution successful.\n{console_output}"
            
        except Exception as e:
            return f"Execution Error: {str(e)}"