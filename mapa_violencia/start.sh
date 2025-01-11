# This file makes it possible so docker starts with more than one command

# Airflow setup
export AIRFLOW__CORE__LOAD_EXAMPLES=False
airflow db migrate
# Temporary user and password
airflow users  create --role Admin --username admin --email admin --firstname admin --lastname admin --password admin 
airflow scheduler &

# Start servers
airflow webserver -p 3000 &
python manage.py runserver 0.0.0.0:8000 &
wait