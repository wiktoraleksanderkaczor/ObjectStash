FROM ubuntu:latest
WORKDIR /pioneer

# Basic requirements
RUN apt-get update && apt-get install -y \
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

# Local CI/CD
RUN curl -L https://github.com/harness/drone-cli/releases/latest/download/drone_linux_amd64.tar.gz | tar zx
RUN install -t /usr/local/bin drone

# Project setup
ADD . .
RUN python3 -m pip install -r requirements.txt


# Basic run command
CMD [ "python3" "server.py"]
