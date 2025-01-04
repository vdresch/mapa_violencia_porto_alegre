import pandas as pd
import numpy as np
from pathlib import Path
import json
import datetime
import re
import difflib

def process_neighborhoods(ti):
    bairros = ti.xcom_pull(task_id='open_neighborhoods')

    #Geojson
    src = Path("scripts/resources/shapesbairros2016/poa.geojson")
    geojson = json.loads(src.read_text(encoding='ISO-8859-1'))
    geometria = dict()
    for i in geojson['features']:
        geometria[i['properties']['Name']] = i['geometry']

    #Same process to find closest names
    bairros_metadata['Bairro2'] = bairros_metadata['Bairro'].apply(lambda x: difflib.get_close_matches(x, bairros, n=1))

    #Drop old column. Drop rows without name
    bairros_metadata['Bairro'] = bairros_metadata['Bairro2']
    bairros_metadata = bairros_metadata.drop(columns='Bairro2')

    bairros_metadata = bairros_metadata[bairros_metadata["Bairro"].str.len() != 0]
    bairros_metadata["Bairro"] = bairros_metadata["Bairro"].apply(lambda x: x[0])

    #Some processing and cleaning
    bairros_metadata = bairros_metadata[:-2]
    bairros_metadata['Área'] = bairros_metadata['Área'].apply(lambda x: re.findall('\d+\.?\d*', x)[0] if pd.notna(x) else np.nan)
    bairros_metadata['Densidade'] = bairros_metadata['Densidade'].apply(lambda x: re.findall('\d+\.?\d*', x)[0] if pd.notna(x) else np.nan)
    bairros_metadata['Renda média por \ndomicílio'] = bairros_metadata['Renda média por \ndomicílio'].apply(lambda x: re.findall('\d+\.?\d*', x)[0] if pd.notna(x) else np.nan)
    bairros_metadata['Data de \nCriação'] = bairros_metadata['Data de \nCriação'].apply(lambda x: datetime.datetime.strptime(x, '%d %b %Y'))

    bairros_metadata = bairros_metadata.drop_duplicates(subset=['Bairro'], keep='first')

    bairros_metadata = bairros_metadata.fillna(0)

    #Adds the geojson
    bairros_metadata['geometry'] = [geometria[i] for i in bairros_metadata['Bairro']]

    #Rename
    bairros_metadata = bairros_metadata.rename(columns={'Data de \nCriação': 'created_at', 'Área': 'area', 'População\n2010': 'population',
                                  'Tx Cresc Pop \n91-00': 'grouth', 'Densidade': 'density', 'Renda média por \ndomicílio': 'average_income'})

    #Saves data
    bairros_metadata.to_pickle('scripts/data/bairros_metadata.pkl')