# Docker image
FROM python:3.9

# Set workdir
WORKDIR /mapa_violencia

# Install dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install "apache-airflow[celery]==2.10.4" --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.10.4/constraints-3.8.txt"

# Copy all files
COPY /mapa_violencia .

# Expose port
EXPOSE 8000

# Start the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]