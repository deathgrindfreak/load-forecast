import pyodbc
import pandas as pd
import sqlalchemy
import urllib

dtype_dict = {'WID': sqlalchemy.types.INTEGER(),
              'DOFP': sqlalchemy.DateTime(),
              'wellName': sqlalchemy.types.VARCHAR(),
              'project': sqlalchemy.types.VARCHAR(),
              'prodArea': sqlalchemy.types.VARCHAR(),
              'meter': sqlalchemy.types.VARCHAR(),
              'bench': sqlalchemy.types.VARCHAR(),
              'liftType': sqlalchemy.types.VARCHAR(),
              'gen': sqlalchemy.types.INTEGER(),
              'LT1': sqlalchemy.types.INTEGER(),
              'LTD1': sqlalchemy.types.VARCHAR(),
              }

graph_dict = {'DOFP': sqlalchemy.DateTime(),
              'WID': sqlalchemy.types.INTEGER(),
              'Load': sqlalchemy.types.FLOAT(),
              }

#welldf = pd.read_excel(r'C:\Users\bbell\Desktop\masterforecastDB.xlsx', sheet_name='Sheet2')

testwelldf = pd.read_excel(r'C:\Users\bbell\Desktop\testDB.xlsx')

#curvedf = pd.read_excel(r'C:\Users\bbell\Desktop\mastercurveDB.xlsx', sheet_name = 'allcurves')

#pmedf = pd.read_excel(r'C:\Users\bbell\Desktop\pmeDB.xlsx')

conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                      'SERVER=SV-GEOSCADA\SQLEXPRESS;'
                      'DATABASE=loadForecast;'
                      'Trusted_Connection=yes;')

params = urllib.parse.quote_plus("DRIVER={ODBC Driver 17 for SQL Server};SERVER=SV-GEOSCADA\SQLEXPRESS;DATABASE=loadForecast;Trusted_Connection=yes")

engine = sqlalchemy.create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)

testwelldf.to_sql(name="test", con=engine, schema='dbo', index=False, if_exists='replace', dtype=dtype_dict)

#curvedf.to_sql(name="loadcurves", con=engine, schema='dbo', index=False, if_exists='replace')

#pmedf.to_sql(name="pmes", con=engine, schema='dbo', index=False, if_exists='replace')

conn.close()