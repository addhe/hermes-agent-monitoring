FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir prometheus_client
COPY exporter.py /app/exporter.py
EXPOSE 9100
CMD ["python", "exporter.py"]
