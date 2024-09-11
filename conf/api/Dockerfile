FROM ubuntu:20.04

RUN ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime

RUN apt-get update \
    && apt-get install -y \
        git \
        curl \
        wget \
        build-essential \
        libssl-dev \
        zlib1g-dev \
        libbz2-dev \
        libreadline-dev \
        libsqlite3-dev \
        llvm \
        libncurses5-dev \
        libncursesw5-dev \
        xz-utils \
        tk-dev \
        libffi-dev \
        liblzma-dev \
        python-openssl \
        ca-certificates \
        && rm -rf /var/lib/apt/lists/*

RUN curl https://pyenv.run | bash

ENV PATH="/root/.pyenv/bin:$PATH"
RUN echo 'eval "$(pyenv init --path)"' >> ~/.bashrc

RUN pyenv install 3.12.2 \
    && pyenv global 3.12.2

ENV PATH="/root/.pyenv/shims:/root/.pyenv/bin:$PATH"

WORKDIR /app
COPY ./app ./

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt