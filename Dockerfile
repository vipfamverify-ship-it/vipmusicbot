FROM python:3.11-slim-bookworm

# NodeJS install for PyTgCalls
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    git \
    g++ \
    cmake \
    build-essential \
    curl \
    libcurl4-openssl-dev \
    libasound2-dev \
    libpulse-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install NodeJS 18 LTS
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .
