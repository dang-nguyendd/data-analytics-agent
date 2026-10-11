from dotenv import load_dotenv
from services.ai_connector import AIConnector
from services.data_summary import data_summary
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
ai.start_data_chat(df_summary = json.dumps(result))

result = ai.send_chat_message("Clean duplicates and missing data")

print("AI RESPONSE: ")
print(result)