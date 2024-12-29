build_image:
	sudo docker build -t mapa_violencia .

run_attach:
	sudo docker run -t -d --name mapa_violencia mapa_violencia
	sudo docker exec -it mapa_violencia bash