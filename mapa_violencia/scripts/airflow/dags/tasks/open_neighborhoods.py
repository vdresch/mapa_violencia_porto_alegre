import pandas as pd

def open_neighborhoods():
    #Open table containing neighborhoods names
    bairros_metadata = pd.read_csv('scripts/resources/shapesbairros2016/Lista_de_bairros_de_Porto_Alegre_1.csv')
    bairros_metadata['Bairro'] = bairros_metadata['Bairro'].apply(lambda x: x.upper())

    bairros = bairros_metadata['Bairro']

    return bairros