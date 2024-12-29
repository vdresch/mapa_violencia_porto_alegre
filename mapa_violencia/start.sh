# This file makes it possible so docker starts with more than one command
python manage.py runserver 0.0.0.0:8000 &
airflow webserver -p 3000 &
wait