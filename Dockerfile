FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5001

CMD exec gunicorn --bind 0.0.0.0:${PORT:-5001} --workers 1 --threads 8 --timeout 120 app:app
