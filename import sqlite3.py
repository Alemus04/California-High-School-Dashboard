import sqlite3
import pandas as pd
import os 



db_path = r"C:\Users\Arthur Lemus\Desktop\database\grad_data.db"

conn = sqlite3.connect(db_path)

cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]

for table in tables:
    df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
    df.to_csv(f"{table}.csv", index = False)
    print(f"Exported {table} to {table}.csv")
    output_folder = r"C:\Users\Arthur Lemus\Desktop\database\exports"

os.makedirs(output_folder, exist_ok=True)  # Create folder if it doesn't exist

df.to_csv(os.path.join(output_folder, f"{table}.csv"), index=False)


conn.close()