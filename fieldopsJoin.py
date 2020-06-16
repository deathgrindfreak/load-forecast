import pydoc
import pandas as pd

conn = pyodbc.connect('DRIVER={SQL Server};'
                      'SERVER=fieldoperations;'
                      'DATABASE=five_tools;'
                      'UID=cq_engineer;'
                      'PWD=engineer;')

cursor = conn.cursor()

