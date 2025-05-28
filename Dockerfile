FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Set environment variables (but *don't* hardcode values here!)
ENV GEMINI_API_KEY=""
ENV GCS_BUCKET_NAME=""
ENV PDF_FILE_NAME=""


CMD gunicorn --bind :8080 --workers 1 --threads 8 main:app