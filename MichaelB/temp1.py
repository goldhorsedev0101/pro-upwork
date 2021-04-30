import sqlite3
import pandas as pd

conn = sqlite3.connect("coinsTESTPricesDB.db")	
df = pd.read_sql_query("SELECT * FROM coinPrices", conn)	

df.index = df["name"]
print(df)