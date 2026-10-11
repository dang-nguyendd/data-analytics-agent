from services.data_summary import data_summary
from pathlib import Path
import pandas as pd


path = Path(".data/hotel_bookings.csv")

df = pd.read_csv(path)

result = data_summary(df)

print("SUMMARY: ")
print(result)
