FROM python:3.11-slim

WORKDIR /app

# Installera systemberoenden
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Kopiera kravfil och installera Python-paket
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiera källkod
COPY . .

EXPOSE 5001

ENV PORT=5001
ENV PYTHONUNBUFFERED=1

CMD ["python", "app.py"]
