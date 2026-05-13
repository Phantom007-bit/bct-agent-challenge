# Root Dockerfile for Python AI Backend
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Copy dependency list and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend directories and main execution files explicitly
# This prevents copying frontend/ and gateway/ into the Python container
COPY agents/ ./agents/
COPY core/ ./core/
COPY evaluate/ ./evaluate/
COPY retrieval/ ./retrieval/
COPY schemas/ ./schemas/
COPY main.py .
COPY slice.py .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]