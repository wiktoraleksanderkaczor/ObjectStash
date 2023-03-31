FROM ubuntu:latest
WORKDIR /pioneer

# Basic requirements
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    build-essential

# Docker
RUN curl -fsSL https://get.docker.com -o get-docker.sh
RUN sh get-docker.sh
RUN groupadd docker
RUN usermod -aG docker $USER

# Local CI/CD
RUN curl -L https://github.com/harness/drone-cli/releases/latest/download/drone_linux_amd64.tar.gz | tar zx
RUN install -t /usr/local/bin drone

# Project requirements
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install -r requirements.txt

# Copy project files
ADD . .

# Basic run command
CMD [ "python3" "server.py"]