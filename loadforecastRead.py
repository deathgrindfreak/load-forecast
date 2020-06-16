import pandas as pd
import pyodbc

conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                      'SERVER=SV-GEOSCADA\SQLEXPRESS;'
                      'DATABASE=loadForecast;'
                      'Trusted_Connection=yes;')

graphdf = pd.read_sql_query('''SELECT * from dbo.graph''', conn)

graphdf.to_excel(r'C:\Users\bbell\Desktop\graphDB.xlsx')

conn.close()
