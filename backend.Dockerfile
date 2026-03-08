FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code (only what's needed)
COPY api/ ./api/

# Config files are handled via volumes in docker-compose for persistence,
# but we provide defaults here so the container can start if volumes are missing.
COPY config_sandbox.json config_prod.json ./

EXPOSE 8000

# Enable unbuffered output for better logs in Docker
ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "api.server:app", "--host", "0.0.0.0", "--port", "8000"]
