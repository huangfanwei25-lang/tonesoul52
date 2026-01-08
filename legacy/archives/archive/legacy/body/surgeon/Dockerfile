# ToneSoul Sandbox - The Fortress
FROM python:3.10-slim-buster

# 1. System Dependencies (Minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# 2. Security: Create Non-Root User
RUN useradd -m surgeon
USER surgeon
WORKDIR /home/surgeon/workspace

# 3. Environment Setup
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 4. Default Entry (Wait for command)
CMD ["python3"]
