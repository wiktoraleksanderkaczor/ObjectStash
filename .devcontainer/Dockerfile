FROM ubuntu:latest

# Switch to work directory
WORKDIR /pioneer

# Input variables
ARG USERNAME

# Basic requirements
RUN apt-get update && apt-get install -y \
    man \
    zip \
    sudo \
    wget \
    curl \
    nano \
    unzip \
    # gnupg \
    locales \
    # ca-certificates \
    build-essential

# Set locale
RUN sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV LC_ALL=en_US.UTF-8

# Install development environment
RUN apt-get update && apt-get install -y \
    # Python
    python3 \
    python3-pip \
    python3-dev \
    python3-wheel \
    python3-setuptools \
    # Required
    fuse \
    libmagic-dev \
    # Tooling
    git

# Python environment
RUN python3 -m pip install --upgrade pip wheel

# Docker
RUN curl -fsSL https://get.docker.com -o get-docker.sh
RUN sh get-docker.sh

# Project setup
ADD . .
RUN python3 -m pip install --no-warn-script-location -r dev-requirements.txt
RUN python3 -m pip install --no-warn-script-location -r requirements.txt

# Add container user
RUN useradd --create-home --shell /bin/bash ${USERNAME} \
    && apt-get install -y sudo \
    && echo ${USERNAME} ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/${USERNAME} \
    && chmod 0440 /etc/sudoers.d/${USERNAME}

# Switch to container user
USER ${USERNAME}

# Basic run command
CMD [ "python3" "server.py"]
