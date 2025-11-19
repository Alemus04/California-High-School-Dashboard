import sqlite3
import pandas as pd
import numpy as np


db_path = r"directory.db"

conn = sqlite3.connect(db_path)
#query = "SELECT * FROM graduation_stats_eight WHERE AcademicYear IS NOT NULL AND AggregateLevel = 'S' AND ReportingCategory = 'TA' AND CharterSchool IN ('Y', 'N') AND DASS IN ('Y', 'N') GROUP BY SchoolID, SchoolName, Year"
Main_df = pd.read_sql( 
    "SELECT * FROM graduation_stats_eight WHERE AcademicYear IS NOT NULL AND AggregateLevel = 'S' AND ReportingCategory == 'TA'"
    , conn
)
#print(Main_df['AcademicYear'].unique)

#Dropping NULL SchoolName and DistrictName
Main_df = Main_df.dropna(subset=['SchoolName', 'DistrictName'])


#Converting to Int and replacing null vals
Main_df['Regular HS Diploma Graduates (Count)'] = (
    Main_df['Regular HS Diploma Graduates (Count)']
    .astype(str)  # Ensure it's string for regex
    .str.extract('(\d+)')  # Extract first numeric sequence
    .astype(float)  # Convert to float for imputation
)

# Impute missing values with school-year mean, then round and cast
Main_df['Regular HS Diploma Graduates (Count)'] = (
    Main_df['Regular HS Diploma Graduates (Count)']
    .fillna(Main_df.groupby(['SchoolName', 'AcademicYear'])['Regular HS Diploma Graduates (Count)'].transform('mean'))
    .round()
    .astype('Int64')
)

print('This worked')

Main_df['Regular HS Diploma Graduates (Rate)'] = (
    Main_df['Regular HS Diploma Graduates (Rate)']
    .astype(str)
    .str.extract('(\d+\.\d+)')  # Extract first float only
    .astype(float)
)
Main_df['Regular HS Diploma Graduates (Rate)'] = (
    Main_df['Regular HS Diploma Graduates (Rate)']
    .fillna(Main_df.groupby(['SchoolName', 'AcademicYear'])['Regular HS Diploma Graduates (Rate)'].transform('mean'))
    .round(2)
)


print('This worked')


# Grouping by District to find total district graduates for the year
Main_df['District Total Graduates'] = Main_df.groupby(['DistrictName', 'AcademicYear'])['Regular HS Diploma Graduates (Count)'].transform('sum')
Main_df['School_ratio_in_district'] = Main_df['Regular HS Diploma Graduates (Count)']/Main_df['District Total Graduates']
Main_df['Join Key'] = "All"

Main_df = Main_df.drop_duplicates(subset=['SchoolCode', 'AcademicYear'], keep='first')


# Jordan High school
#J_df = pd.read_sql("SELECT * FROM graduation_stats WHERE CountyName == 'Los Angeles' AND SchoolName LIKE '%Jordan%' AND DistrictName LIKE '%Los Angeles%' AND AggregateLevel == 'S' AND ReportingCategory == 'TA'", conn)

# Simon Tech
#St_df = pd.read_sql("SELECT * FROM graduation_stats WHERE CountyName == 'Los Angeles' AND SchoolName LIKE '%Alliance Cindy and Bill Simon%' AND DistrictName LIKE '%Los Angeles%' AND AggregateLevel == 'S' AND ReportingCategory == 'TA'", conn)


print(Main_df.shape)
print(Main_df.columns)

"Push to SQL server"
Main_df.to_sql('Eight', conn, if_exists='replace', index = False)


conn.close()