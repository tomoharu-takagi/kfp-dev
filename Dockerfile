# Dockerfile for a simple KFP environment

FROM python:3.8-slim

# Install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install KFP SDK and any other necessary packages
RUN pip install --no-cache-dir \
    kfp==1.8.9 \
    jupyterlab

# Copy your pipeline code here if needed
COPY ./pipeline /pipeline

# Set working directory
WORKDIR /pipeline

# Expose ports for Jupyter
EXPOSE 8888

# Command to run Jupyter for KFP
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--allow-root"]
