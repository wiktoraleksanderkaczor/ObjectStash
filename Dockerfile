FROM ubuntu:latest
WORKDIR /pioneer

# Basic requirements
RUN apt-get update && apt-get install -y \
    git \
    curl \
    python3 \
    python3-pip \
    python3-dev \
    build-essential

# Python environment
RUN python3 -m pip install --upgrade pip wheel

# Docker
RUN curl -fsSL https://get.docker.com -o get-docker.sh
RUN sh get-docker.sh

# Project setup
ADD . .
RUN python3 -m pip install -r requirements.txt

# Git hooks setup
RUN pre-commit autoupdate
RUN pre-commit install

# Basic run command
CMD [ "python3" "server.py"]
