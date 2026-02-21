FROM pytorch/pytorch:2.2.0-cuda12.1-cudnn8-runtime

RUN apt-get update && apt-get install -y \
    git wget \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Clone LigandMPNN repository
RUN mkdir -p repo && \
    for attempt in 1 2 3; do \
      echo "Clone attempt $attempt/3"; \
      git clone --depth 1 https://github.com/dauparas/LigandMPNN.git repo/LigandMPNN && break; \
      if [ $attempt -lt 3 ]; then sleep 5; fi; \
    done

# Install LigandMPNN dependencies (excluding PyTorch to avoid conflicts with base image)
# The pytorch/pytorch base image already has PyTorch 2.2.0 with proper CUDA bindings
RUN pip install --no-cache-dir \
    $(grep -v -E "^(torch|torchaudio|torchvision)" repo/LigandMPNN/requirements.txt | grep -v "^#" | tr '\n' ' ')

# Install MCP dependencies
RUN pip install --no-cache-dir --ignore-installed fastmcp loguru

# Download model weights into the image to avoid repeated downloads
RUN bash repo/LigandMPNN/get_model_params.sh repo/LigandMPNN/model_params

# Copy application source code
COPY scripts/ ./scripts/
RUN chmod -R a+r /app/scripts/
COPY src/ ./src/
RUN chmod -R a+r /app/src/
COPY examples/ ./examples/
RUN chmod -R a+r /app/examples/
COPY configs/ ./configs/
RUN chmod -R a+r /app/configs/

# Create working directories
RUN mkdir -p results jobs tmp

ENV PYTHONPATH=/app

CMD ["python", "src/server.py"]
