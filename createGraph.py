import plotly.graph_objects as go
import pandas as pd
import datetime
import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import pyodbc
import sqlalchemy
import urllib

graph_dict = {'DOFP': sqlalchemy.DateTime(),
              'WID': sqlalchemy.types.INTEGER(),
              'Load': sqlalchemy.types.FLOAT(),
              }

conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                      'SERVER=SV-GEOSCADA\SQLEXPRESS;'
                      'DATABASE=loadForecast;'
                      'Trusted_Connection=yes;')

# read SQL tables to dataframes
well_query = pd.read_sql_query('''SELECT WID, DOFP, wellName, project, prodArea, meter, bench, liftType, gen, LT1, LTD1 from dbo.test''', conn)
curve_query = pd.read_sql_query('''SELECT LS_300, LS_240, HA_300, HA_240, HA_180, HB_300, HB_180  from dbo.loadcurves''', conn)

welldf = pd.DataFrame(well_query, columns=['WID', 'DOFP', 'wellName', 'project', 'prodArea', 'meter', 'bench', 'liftType', 'gen', 'LT1', 'LTD1'])
curvedf = pd.DataFrame(curve_query, columns=['LS_300', 'LS_240', 'HA_300', 'HA_240', 'HA_180', 'HB_300', 'HB_180'])

well_list = welldf['WID'].tolist()

LS300_list = curvedf['LS_300'].tolist()
LS240_list = curvedf['LS_240'].tolist()
HA300_list = curvedf['HA_300'].tolist()
HA240_list = curvedf['HA_240'].tolist()
HA180_list = curvedf['HA_180'].tolist()
HB300_list = curvedf['HB_300'].tolist()
HB180_list = curvedf['HB_180'].tolist()

graphmaxdate = welldf['DOFP'].max() + datetime.timedelta(days=999)

def led_function(led):
    try:
        ledtype = int(led)
        return 'Integer'
    except:
        pass

    return 'String'


def find_loadcurve(typecurve, flatcurve, led):
    if typecurve is not None:
        if typecurve == 'LS_300':
            return LS300_list

        elif typecurve == 'LS_240':
            return LS240_list

        elif typecurve == 'HA_300':
            return HA300_list

        elif typecurve == 'HA_240':
            return HA240_list

        elif typecurve == 'HA_180':
            return HA180_list

        elif typecurve == 'HB_300':
            return HB300_list

        elif typecurve == 'HB_180':
            return HB180_list

    if flatcurve is not None:
        if led_function(led) == "Integer":
            liftamps = flatcurve / 1.114
            flat_list = [liftamps] * int(led)
            return flat_list

        # if user entered a string
        elif led_function(led) == "String":
            liftamps = flatcurve / 1.114
            daterange = graphmaxdate - dofp + datetime.timedelta(days=1)
            flat_list = [liftamps] * daterange.days
            return flat_list

def find_dates(dofp):
    #date range for wells with type curve
    if typecurve is not None:
        maxdate = dofp + datetime.timedelta(days=999)
        date_range = pd.date_range(dofp, maxdate)
        return date_range
    #date range for wells with a flat curve
    else:
        #Integer
        if led_function(led) == "Integer":
            maxdate = dofp + datetime.timedelta(days=(int(led)-1))
            date_range = pd.date_range(dofp, maxdate)
            return date_range
        #String
        else:
            maxdate = graphmaxdate
            date_range = pd.date_range(dofp, maxdate)
            return date_range


sumdf = pd.DataFrame()

for i in well_list:
    resultdf = pd.DataFrame()

    wellindex = welldf.loc[welldf['WID'] == i].index.item()
    typecurve = welldf.iloc[wellindex, 7]
    gendays = welldf.iloc[wellindex, 8]
    flatcurve = welldf.iloc[wellindex, 9]
    led = welldf.iloc[wellindex, 10]

    dofp = welldf.iloc[wellindex, 1]
    dates_list = find_dates(dofp)

    wid_list = [i] * len(dates_list)

    loadcurve_list = find_loadcurve(typecurve, flatcurve, led)

    if np.isnan(gendays) == False:
        gendays = int(gendays)
        gen_zeros = [0] * gendays
        loadcurve_list[:gendays] = gen_zeros

    resultdf = pd.DataFrame({'DOFP': dates_list, 'WID': wid_list, 'Load': loadcurve_list})

    sumdf = sumdf.append(resultdf, ignore_index=True)

# write sumdf back to SQl database
params = urllib.parse.quote_plus("DRIVER={ODBC Driver 17 for SQL Server};SERVER=SV-GEOSCADA\SQLEXPRESS;DATABASE=loadForecast;Trusted_Connection=yes")
engine = sqlalchemy.create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)
sumdf.to_sql(name="graph", con=engine, schema='dbo', index=False, if_exists='replace', dtype=graph_dict)

# close SQL Server connection
conn.close()

