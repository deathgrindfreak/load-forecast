import pandas as pd
from datetime import timedelta

welldf = pd.read_excel(r'C:\Users\bbell\Desktop\newwellDB.xlsx')
pmedf = pd.read_excel(r'C:\Users\bbell\Desktop\pmeDB.xlsx')

welldatelist = welldf['DOFP']
wellmaxdate = welldatelist.max() + timedelta(days=1000)
graphdf = pd.DataFrame(pd.date_range(welldatelist.min(), wellmaxdate), columns=['DOFP'])

graphdates_list = graphdf['DOFP'].tolist()
pme_list = pmedf['PME'].tolist()

dict_pme = {'DOFP': graphdates_list}

for i in pme_list:
    pmeindex = pmedf.loc[pmedf['PME'] == i].index.item()
    pmecapacity = int(pmedf.iloc[pmeindex, 1])
    pme_initial = [pmecapacity] * len(graphdates_list)
    dict_pme.update({i: pme_initial})

pme_resultdf = pd.DataFrame(dict_pme)
