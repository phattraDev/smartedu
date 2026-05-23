FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY backend/requirements.txt /tmp/backend-requirements.txt
RUN pip install --no-cache-dir -r /tmp/backend-requirements.txt

# Copy all source
COPY backend/ /app/backend/
COPY bot/ /app/bot/
COPY dashboard/ /app/dashboard/

# Create uploads directory
RUN mkdir -p /app/uploads

WORKDIR /app/backend

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
