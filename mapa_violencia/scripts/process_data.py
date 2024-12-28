######################################################################################################
#
#   Code should be run by Django before starting the server with the following command:
#   python manage.py runscript process_data
#
#   This code should be updates every year because of the new files.
#
#   The objective of this code is to clean the data provided by Secretaria da Segurança
#   Pública. The neighborhoods will be cleaned and the output is a CSV that can be used by Tableau.
#   There will be aldo a CSV with metadata about the neighborhoods.
#
#   The code takes CSV files located in the folder data, as well as a shapefile located on the folder
#   shapes_bairros2016. In this folder, there will also be a wikipedia table with the metadata from the
#   year 2010, to be updated with the new Census.
#
#   The output will be two CSV files, both on the folder data.
#
######################################################################################################

import pandas as pd
import difflib
import datetime
import re
import numpy as np
import json
from pathlib import Path
import locale

locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')

#Function so it can be used from other script
def run():
    #Read data
    crimes_2021 = pd.read_csv('scripts/data/crimes_2021.csv', sep=';', encoding="ISO-8859-1")
    crimes_2022 = pd.read_csv('scripts/data/crimes_2022.csv', sep=';', encoding="ISO-8859-1")
    crimes_2023 = pd.read_csv('scripts/data/crimes_2023.csv', sep=';', encoding="ISO-8859-1")


    crimes = pd.concat([crimes_2021, crimes_2022, crimes_2023], ignore_index=True)


    #Drop colunas desnecessárias
    crimes = crimes.drop(crimes.columns[10:], axis=1)
    #Drop cidades que não são Porto Alegre
    crimes =  crimes[crimes['Municipio Fato'] == 'PORTO ALEGRE']
    #Drop NA na coluna bairros. Converte coluna para lower
    crimes =  crimes[crimes['Bairro'].notna()]
    #Lower case
    crimes['Bairro'] = crimes['Bairro'].apply(lambda x: x.lower())
    #Tira acentos
    crimes['Bairro'] = crimes['Bairro'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
    #Arruma alguns erros comuns de gramática
    crimes['Bairro'] = crimes['Bairro'].str.replace('vl', 'vila')
    crimes['Bairro'] = crimes['Bairro'].str.replace('sta', 'santa')
    #Arruma alguns bairros errados, segundo o mapa utilizado para a análise
    crimes['Bairro'] = crimes['Bairro'].str.replace('protasio alves', 'morro santana')
    crimes['Bairro'] = crimes['Bairro'].str.replace('cais do porto', 'centro historico')
    crimes['Bairro'] = crimes['Bairro'].str.replace('intercap', 'partenon')
    crimes.loc[crimes['Bairro'] == 'centro', 'Bairro'] = 'centro historico'
    #Upper case
    crimes['Bairro'] = crimes['Bairro'].apply(lambda x: x.upper())

    crimes['Data Fato'] = crimes['Data Fato'].apply(lambda x: datetime.datetime.strptime(x, '%d/%m/%Y'))
    crimes['Hora Fato'] = crimes['Hora Fato'].apply(lambda x: datetime.datetime.strptime(x, '%H:%M:%S'))


    #Open table containing neighborhoods names
    bairros_metadata = pd.read_csv('scripts/resources/shapesbairros2016/Lista_de_bairros_de_Porto_Alegre_1.csv')
    bairros_metadata['Bairro'] = bairros_metadata['Bairro'].apply(lambda x: x.upper())

    bairros = bairros_metadata['Bairro']


    #Finds neighborhood with closest name
    crimes['Bairro2'] = crimes['Bairro'].apply(lambda x: difflib.get_close_matches(x, bairros, n=1))

    #Saves errors. Errors occur when it can't find any neighborhood
    crimes[crimes["Bairro2"].str.len() == 0].groupby('Bairro').count().to_csv('scripts/data/error.csv')

    #Drop old column, drop rows without neighborhood
    crimes['Bairro'] = crimes['Bairro2']
    crimes = crimes.drop(columns='Bairro2')

    crimes = crimes[crimes["Bairro"].str.len() != 0]
    crimes["Bairro"] = crimes["Bairro"].apply(lambda x: x[0])

    #Saves file
    crimes.to_pickle('scripts/data/processed_data.pkl')


    #Now, let's process the metadata

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


if __name__=="__main__":
    run()