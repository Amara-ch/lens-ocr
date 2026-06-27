# syntax=docker/dockerfile:1.6
FROM python:3.11-slim

# System dependencies for image processing + PDFs
RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps first for better layer caching
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project sources
COPY pyproject.toml ./
COPY src ./src
COPY api ./api

# Install the package itself so the `lens-ocr` CLI works
RUN pip install --no-cache-dir -e .

EXPOSE 8000

# Default: run the FastAPI server
CMD ["uvicorn", "api.server:app", "--host", "0.0.0.0", "--port", "8000"]