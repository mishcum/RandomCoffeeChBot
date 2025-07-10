FROM python:3.12-slim
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists
WORKDIR /app
COPY app/ ./app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "-m", "app.main"]