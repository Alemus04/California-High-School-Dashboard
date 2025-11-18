import requests 
import pandas as pd
from io import StringIO 
import sqlite3
# Code is pulling from URL, converting to CSV and uploading it to SQLite database
urls = ["https://www3.cde.ca.gov/demo-downloads/acgr/acgr24.txt", 
        "https://www3.cde.ca.gov/demo-downloads/acgr/acgr23-v2.txt", 
        "https://www3.cde.ca.gov/demo-downloads/acgr/acgr22-v3.txt", 
        "https://www3.cde.ca.gov/demo-downloads/acgr/acgr21.txt", 
        "https://www3.cde.ca.gov/demo-downloads/acgr/acgr20.txt", 
        "https://www3.cde.ca.gov/demo-downloads/acgr/acgr19.txt", 
        "https://www3.cde.ca.gov/demo-downloads/acgr/acgr18.txt", 
        "https://www3.cde.ca.gov/demo-downloads/acgr/acgr17.txt"]
#response = requests.get(url)
db_path = r"C:\Users\Arthur Lemus\Desktop\database\grad_data.db"
conn = sqlite3.connect(db_path)

dataframes = []

for url in urls:
    response = requests.get(url)
    if response.status_code == 200:
        df = pd.read_csv(StringIO(response.text), delimiter='\t')
        dataframes.append(df)

# Get union of all columns
all_columns = set().union(*(df.columns for df in dataframes))

# Reindex each DataFrame to match full schema
aligned_dfs = [df.reindex(columns=all_columns) for df in dataframes]

# Concatenate and write once
combined_df = pd.concat(aligned_dfs, ignore_index=True)
combined_df = combined_df.drop(columns=['Golden State Seal Merit Diploma (Count)', 'CHSPE Completer (Count)',
       'SPED Certificate (Count)', 'CharterSchool', 
       'Graduates Meeting Local Requirements Exemption (Count)',
       'ï»¿AcademicYear',
        'DistrictCode',
       'GED Completer (Count)', "Met UC/CSU Grad Req's (Count)", 'DASS',
       'CPP Completer (Count)',
       'Adult Ed. HS Diploma (Count)',
       'Graduates Meeting Local Requirements Exemption (Rate)',
       "Met UC/CSU Grad Req's (Rate)", 'Other Transfer (Count)',
       'Seal of Biliteracy (Rate)', 'Adult Ed. HS Diploma (Rate)',
       'Other Transfer (Rate)', 'Still Enrolled (Count)',
       'SPED Certificate (Rate)',
       'Still Enrolled (Rate)',
       'Golden State Seal Merit Diploma (Rate', 'CHSPE Completer (Rate)',
       'GED Completer (Rate)', 'Seal of Biliteracy (Count)'])
conn = sqlite3.connect(r"C:\Users\Arthur Lemus\Desktop\database\grad_data.db")
combined_df.to_sql("graduation_stats_eight", conn, if_exists="replace", index=False)
print(combined_df.columns)
conn.close()
