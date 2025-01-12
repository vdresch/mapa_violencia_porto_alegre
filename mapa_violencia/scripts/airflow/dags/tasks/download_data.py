import requests
from bs4 import BeautifulSoup
import zipfile
import os


def download_data():
    # Path where data will be stored
    diretory_path = "scripts/data/"

    # url to parse and download data
    url = requests.get('https://ssp.rs.gov.br/dados-abertos')

    # Parse the url
    soup = BeautifulSoup(url.content, "html.parser")

    download_links = []

    for a in soup.find_all("a"):
        href = a.get("href")
        if href and (href.endswith(".csv") or href.endswith(".zip")) and "semestre" not in href.lower():
            download_links.append(href)

    seen = {}
    download_links = [seen.setdefault(x, x) for x in download_links if x not in seen]

    # Download the right files and unzip
    ano = 2021

    paths = []

    for link in download_links:
        link = "https://ssp.rs.gov.br" + link

        if '.csv' in link:
            extension = '.csv'
        elif '.zip' in link:
            extension = '.zip'

        path = diretory_path+ "crimes_" + str(ano) + extension

        response = requests.get(link, stream=True)

        with open(path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        if extension == '.zip':
            with zipfile.ZipFile(path, 'r') as zip_ref:
                file_name = zip_ref.infolist()[0].filename
                zip_ref.extractall(diretory_path)

            os.remove(path)  

            path = diretory_path+ "crimes_" + str(ano) + '.csv'
            os.rename(diretory_path + file_name, path)

        paths.append(path)      

        ano += 1

    return paths