build_image:
	sudo docker build -t mapa_violencia .

run_attach:
	sudo docker run -v /home/deck/Documents/Git/mapa_violencia_django/mapa_violencia:/mapa_violencia -t -d --name mapa_violencia mapa_violencia
	sudo docker exec -it mapa_violencia bash

stop_prune:
	sudo docker stop mapa_violencia
	sudo docker container prune
	sudo rm mapa_violencia/scripts/airflow/airflow.cfg
	sudo rm mapa_violencia/scripts/airflow/airflow.db
	sudo rm mapa_violencia/scripts/airflow/webserver_config.py
	sudo rm mapa_violencia/scripts/airflow/airflow-webserver.pid
	sudo rm -r mapa_violencia/scripts/airflow/logs