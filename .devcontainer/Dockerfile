FROM debian:bullseye-slim

ENV DEBIAN_FRONTEND=noninteractive

ARG USERNAME=wizard
ARG USER_UID=1000
ARG USER_GID=$USER_UID

ARG PYTHON_VERSION=3.11.1

# Instale dependências
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget ca-certificates build-essential libssl-dev zlib1g-dev libbz2-dev \
    libreadline-dev libsqlite3-dev libncurses5-dev libncursesw5-dev xz-utils \
    tk-dev libffi-dev liblzma-dev gnupg \
    && rm -rf /var/lib/apt/lists/*

# Compile e instale Python
RUN wget https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tar.xz \
    && tar xf Python-${PYTHON_VERSION}.tar.xz \
    && cd Python-${PYTHON_VERSION} \
    && ./configure --enable-optimizations --prefix=/usr/local \
    && make -j $(nproc) \
    && make altinstall \
    && cd .. \
    && rm -rf Python-${PYTHON_VERSION} Python-${PYTHON_VERSION}.tar.xz

# Configure Python
RUN ln -s /usr/local/bin/python3.11 /usr/local/bin/python \
    && ln -s /usr/local/bin/python3.11 /usr/local/bin/python3 \
    && ln -s /usr/local/bin/pip3.11 /usr/local/bin/pip

# Instale R
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 95C0FAF38DB3CCAD0C080A7BDC78B2DDEABC47B7 \
    && echo "deb http://cloud.r-project.org/bin/linux/debian bullseye-cran40/" > /etc/apt/sources.list.d/r-project.list \
    && apt-get update && apt-get install -y --no-install-recommends r-base r-base-dev \
    && rm -rf /var/lib/apt/lists/*

# Crie o usuário
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME

# Limpeza final
RUN apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

USER $USERNAME