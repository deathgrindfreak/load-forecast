import pandas as pd
import datetime
import pyodbc

#connect to SQL Server
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                      'SERVER=SV-GEOSCADA\SQLEXPRESS;'
                      'DATABASE=loadForecast;'
                      'Trusted_Connection=yes;')

# write SQL tables to dataframes
well_query = pd.read_sql_query('''SELECT WID, DOFP, wellName, project, prodArea, meter, bench, liftType, gen, LT1, LTD1 from dbo.test''', conn)
curve_query = pd.read_sql_query('''SELECT LS_300, LS_240, HA_300, HA_240, HA_180, HB_300, HB_180  from dbo.loadcurves''', conn)

welldf = pd.DataFrame(well_query, columns=['WID', 'DOFP', 'wellName', 'project', 'prodArea', 'meter', 'bench', 'liftType', 'gen', 'LT1', 'LTD1'])
curvedf = pd.DataFrame(curve_query, columns=['LS_300', 'LS_240', 'HA_300', 'HA_240', 'HA_180', 'HB_300', 'HB_180'])

# close SQL Server connection
conn.close()

# create initial date range for graphdf
welldatelist = welldf['DOFP']
wellmaxdate = welldatelist.max() + datetime.timedelta(days=1000)
graphdf = pd.DataFrame(pd.date_range(welldatelist.min(), wellmaxdate), columns=['DOFP'])

# discrete load curve lists
LS300_list = curvedf['LS_300'].tolist()
LS240_list = curvedf['LS_240'].tolist()
HA300_list = curvedf['HA_300'].tolist()
HA240_list = curvedf['HA_240'].tolist()
HA180_list = curvedf['HA_180'].tolist()
HB300_list = curvedf['HB_300'].tolist()
HB180_list = curvedf['HB_180'].tolist()

# create lists of wells with a flat load
oldwelldf = welldf.loc[welldf['liftType'].isnull()]
oldwell_list = oldwelldf['WID'].tolist()

# create lists of wells with a load curve
newwelldf = welldf.loc[welldf['liftType'].notnull()]
newwell_list = newwelldf['WID'].tolist()

# initialize dictionary
graphdates_list = graphdf['DOFP'].tolist()
dict_amps = {'DOFP': graphdates_list}
dict_kw = {'DOFP': graphdates_list}

# function for determining user input type
def led_function(led):
    try:
        testdays = datetime.timedelta(1)
        ledtype = led - testdays + testdays
        return 'Date'
    except TypeError:
        pass

    try:
        ledtype = int(led)
        return 'Integer'
    except:
        pass

    return 'String'

# for loop for wells using a load curve
for i in newwell_list:
    wellindex = welldf.loc[welldf['WID'] == i].index.item()
    date = welldf.iloc[wellindex, 1]
    index = graphdf[graphdf['DOFP'] == date].index.item()

    n = len(graphdates_list) - len(LS300_list)
    curve_initial = [0] * n
    typecurve = welldf.iloc[wellindex, 7]
    gendays = welldf.iloc[wellindex, 8]

    if typecurve == 'LS_300':
        curve_initial[index:index] = LS300_list

    elif typecurve == 'LS_240':
        curve_initial[index:index] = LS240_list

    elif typecurve == 'HA_300':
        curve_initial[index:index] = HA300_list

    elif typecurve == 'HA_240':
        curve_initial[index:index] = HA240_list

    elif typecurve == 'HA_180':
        curve_initial[index:index] = HA180_list

    elif typecurve == 'HB_300':
        curve_initial[index:index] = HB300_list

    elif typecurve == 'HB_180':
        curve_initial[index:index] = HB180_list

    if gendays is not None:
        gendays = int(gendays)
        genslice = gendays + index
        gen_zeros = [0] * gendays
        curve_initial[index:genslice] = gen_zeros

    curve_initial_kw = [element * 0.831 for element in curve_initial]

    dict_amps.update({i: curve_initial})
    dict_kw.update({i: curve_initial_kw})


# for loop for wells using a flat load
for i in oldwell_list:
    wellindex = welldf.loc[welldf['WID'] == i].index.item()
    date = welldf.iloc[wellindex, 1]
    index = graphdf[graphdf['DOFP'] == date].index.item()


    lifthp = (welldf.iloc[wellindex, 9]) / 1.114
    led = welldf.iloc[wellindex, 10]
    flat_list = []

    # if user entered an integer
    if led_function(led) == "Integer":
        time = int(welldf.iloc[wellindex, 10])
        flat_list = [lifthp] * time

    # if user entered a string
    elif led_function(led) == "String":
        length = wellmaxdate - date
        flat_list = [lifthp] * length.days

    # if user entered a date
    else:
        date_length = led - date
        flat_list = [lifthp] * date_length.days


    x = len(graphdates_list) - len(flat_list)
    flat_initial = [0] * x
    flat_initial[index:index] = flat_list

    flat_initial_kw = [element * 0.831 for element in flat_initial]

    dict_amps.update({i: flat_initial})
    dict_kw.update({i: flat_initial_kw})

result_amps = pd.DataFrame(dict_amps)
result_kw = pd.DataFrame(dict_kw)

# sum up all rows
result_amps['sum'] = result_amps.sum(axis=1)
result_kw['sum'] = result_kw.sum(axis=1)

print(result_kw)