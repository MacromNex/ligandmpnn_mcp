FROM pytorch/pytorch:2.2.0-cuda12.1-cudnn8-runtime

RUN apt-get update && apt-get install -y \
    git wget \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Clone LigandMPNN repository
RUN git clone https://github.com/dauparas/LigandMPNN.git repo/LigandMPNN

# Install LigandMPNN dependencies
RUN pip install --no-cache-dir -r repo/LigandMPNN/requirements.txt

# Install MCP dependencies
RUN pip install --no-cache-dir --ignore-installed fastmcp loguru

# Download model weights into the image to avoid repeated downloads
RUN bash repo/LigandMPNN/get_model_params.sh repo/LigandMPNN/model_params

# Copy application source code
COPY scripts/ ./scripts/
COPY src/ ./src/
COPY examples/ ./examples/
COPY configs/ ./configs/

# Create working directories
RUN mkdir -p results jobs tmp

ENV PYTHONPATH=/app

CMD ["python", "src/server.py"]
