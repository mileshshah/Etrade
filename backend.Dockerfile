FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY api/ ./api/
# Copy config files (placeholders or user-provided)
COPY config_sandbox.json config_prod.json ./

# Expose port
EXPOSE 8000

# Start command
CMD ["uvicorn", "api.server:app", "--host", "0.0.0.0", "--port", "8000"]
