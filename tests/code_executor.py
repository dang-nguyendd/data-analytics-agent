from dotenv import load_dotenv
from services.ai_connector import AIConnector
from services.data_summary import data_summary
from services.code_executor import CodeExecutor
from pathlib import Path
import pandas as pd
import json

load_dotenv()

path = Path(".data/hotel_bookings.csv")
df = pd.read_csv(path)

result = data_summary(df)

print("SUMMARY: ")
print(result)

ai = AIConnector()
ai.start_data_chat()

result = ai.send_chat_message(df=df, message="Draw a graph to show amound of class of each variable")

print("AI RESPONSE: ")
print(result)

code_executor = CodeExecutor(initial_df=df)
code_executor.set_df(df)
result = code_executor.execute(ai_response=result)

print("CODE EXECUTION: ")
print(result)