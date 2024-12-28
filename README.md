# Mapa da violência Porto Alegre

### About
This code runs a website with a fully custom dashboard with relevant statistics about crime in the city of Porto Alegre. The map will show the stats for evey neighborhood. There is also filters for dates and specific crimes. With this tool, you will be able to have a better understanding of the safety situation in Porto Alegre and it's neighborhoods, as well to make decisions based on it.

![Website](https://github.com/vdresch/mapa_violencia_django/blob/main/map_example.png)

### How to run
There are only three things needed to run this project:

- Python 3.9
- The Python packages
- The database

All the Python packages are listed in `requirements.txt`. To install them, you need to run the following command: `pip install -r requirements.txt`.

The database will be available at the [SSP RS website](https://ssp.rs.gov.br/dados-abertos). You will need to download a file for every desired year. Depending on the number of years downloaded, you might need to adapt the `mapa_violencia/scripts/process_data.py` file. All the files must be in CSV format and be moved to `mapa_violencia/scripts/data`. To run the script that builds the database, use the following command: `python mapa_violencia/manage.py runscript process_data.py`.

Once the database has been built, you will be ready to run the website. For this, use the following command: `python mapa_violencia/manage.py runserver`.

Now, the website will be available at http://127.0.0.1:8000/mapa.

### Metodology

#### Database
According to Law No. 15,610 of April 29, 2021, the Secretary of Public Security of Rio Grande do Sul publishes a monthly database with all records of crimes in the state. This database contains one entry for each registered crime, with information on date, type of occurrence, and location of the event. All information related to crimes comes from [this database](https://ssp.rs.gov.br/dados-abertos).

The geographical boundaries of the neighborhoods are provided by the [Municipality of Porto Alegre](http://observapoa.com.br/default.php?reg=259&p_secao=46). Population data is sourced from [Wikipedia](https://pt.wikipedia.org/wiki/Lista_de_bairros_de_Porto_Alegre) and refers to the 2010 Census. As there are neighborhoods created after the Census, these neighborhoods do not have population data. Therefore, it is not possible to calculate crime rates per capita.

#### Processing
The processing of the database is quite simple and involves cleaning the database and merging it with geographical and population data.

Database cleaning consists of first filtering only events that occurred in Porto Alegre and second correcting neighborhood name issues. Since the victim manually fills in the occurrence neighborhood, the step of correcting the name is necessary. Name correction involves changing some abbreviations (sta to Santa and vl to Vila), changing some common names to the official name (Protásio Alves to Morro Santana, Centro and Cais do Porto to Centro Histórico, Intercap to Partenon), and finally, the get_close_matches() algorithm from difflib is used to correct minor grammatical issues. The process is open source and can be accessed at [this link](https://github.com/vdresch/mapa_violencia_django/blob/main/mapa_violencia/scripts/process_data.py).

#### Violent and Non-Violent Crimes
The definition of what constitutes a violent crime and a non-violent crime was arbitrary and non-technical. Since the process was carried out manually, there may also be human errors in classification. The list of crimes for each classification can be accessed at the following link: [crime classification](https://github.com/vdresch/mapa_violencia_django/blob/main/mapa_violencia/mapa/crimes_list.py).

### TODO to deploy
- css to separate file
- clean and document code
- domain
- deploy

### TODO extra features
- ranking of crimes
- change datepicker min date mobile (so it does not go below oct 2021)
- filter by weekday and time
- deprecated L.min