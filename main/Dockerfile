# Use PyTorch base image
FROM --platform=linux/amd64 pytorch/pytorch:2.6.0-cuda12.4-cudnn9-runtime AS build

# Create working directory
WORKDIR /app

# Install system dependencies for building Python extensions
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Install torch, torchvision, and torchaudio using the official PyTorch index.
RUN pip install --no-cache-dir \
    torch==2.6.0 \
    torchvision==0.21.0 \
    torchaudio==2.6.0 \
    --index-url https://download.pytorch.org/whl/cu121

# Install the remaining dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source
COPY app/ ./app/

# Expose port 8000
EXPOSE 8000

# Launch FastAPI with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
