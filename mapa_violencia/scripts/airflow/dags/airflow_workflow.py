# scrap data
# open neighborhoods
# open crimes
# bairros metadata
# reload aplication

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime

# Import tasks
from tasks.download_data import download_data
from tasks.process_crimes import process_crimes
from tasks.process_neighborhoods import process_neighborhoods

# DAG
with DAG(
    dag_id='update_crimes',
    description='Monthly update on the crime statistics for Porto Alegre',
    start_date=datetime(2024, 12, 25, 22, 0),
    schedule_interval='@monthly'
) as dag:
    # Download the data from the oficial website
    task1 = PythonOperator(
        task_id = 'download_data',
        python_callable = download_data
    )
    # Process the data and metadata from the downloaded data
    task2 = PythonOperator(
        task_id = 'process_crimes',
        python_callable = process_crimes
    )
    # Process the data and metadata from the neighborhoods geo data
    task3 = PythonOperator(
        task_id = 'process_neighborhoods',
        python_callable = process_neighborhoods  
    )
    # Reload Django aplication
    task4 = BashOperator(
        task_id = 'restart_django_server',
        bash_command= '''echo "# meow" >> /mapa_violencia/manage.py && sed -i -e '$ d' /mapa_violencia/manage.py'''
    )

    task1 >> task2
    task2 >> task4
    task3 >> task4
