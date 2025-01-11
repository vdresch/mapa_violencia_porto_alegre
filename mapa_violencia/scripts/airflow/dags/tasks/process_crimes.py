import pandas as pd
import difflib
import datetime
import locale

locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')

def process_crimes():
    # TROCAR POR XCOM_PULL QUANDO DOWNLOADER ESTIVER OPERACIONAL
    crimes_2021 = pd.read_csv('scripts/data/crimes_2021.csv', sep=';', encoding="ISO-8859-1")
    crimes_2022 = pd.read_csv('scripts/data/crimes_2022.csv', sep=';', encoding="ISO-8859-1")
    crimes_2023 = pd.read_csv('scripts/data/crimes_2023.csv', sep=';', encoding="ISO-8859-1")
    crimes = pd.concat([crimes_2021, crimes_2022, crimes_2023], ignore_index=True)

    #Open table containing neighborhoods names
    bairros_metadata = pd.read_csv('scripts/resources/shapesbairros2016/Lista_de_bairros_de_Porto_Alegre_1.csv')
    bairros_metadata['Bairro'] = bairros_metadata['Bairro'].apply(lambda x: x.upper())

    bairros = bairros_metadata['Bairro']

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