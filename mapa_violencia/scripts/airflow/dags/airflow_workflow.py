# scrap data
# open neighborhoods
# open crimes
# bairros metadata

from airflow import DAG
from datetime import datetime


with DAG(
    dag_id='update_crimes',
    description='Monthly update on the crime statistics for Porto Alegre',
    start_date=datetime(2024, 12, 20, 22, 0),
    schedule_interval='@monthly'
) as dag:
    pass