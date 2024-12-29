# Docker image
FROM python:3.9

# Set workdir
WORKDIR /mapa_violencia

# Install dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install "apache-airflow[celery]==2.10.4" --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.10.4/constraints-3.8.txt"
RUN apt-get update && \
    apt-get install -y locales && \
    sed -i -e 's/# ot_BR.UTF-8 UTF-8/pt_BR.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales

# Copy all files
COPY /mapa_violencia .

# Setup airflow
ENV AIRFLOW_HOME="/mapa_violencia/scripts/airflow"
RUN airflow db init
# Temporary user and password
RUN airflow users  create --role Admin --username admin --email admin --firstname admin --lastname admin --password admin 

# Build db


# Expose ports
EXPOSE 8000 3000

# Start the application and airflow
CMD ["bash", "start.sh"]