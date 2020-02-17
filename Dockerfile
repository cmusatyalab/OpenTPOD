FROM ubuntu:18.04

ARG http_proxy
ARG https_proxy
ARG no_proxy
ARG socks_proxy
ARG TZ

ENV TERM=xterm \
    http_proxy=${http_proxy}   \
    https_proxy=${https_proxy} \
    no_proxy=${no_proxy} \
    socks_proxy=${socks_proxy} \
    LANG='C.UTF-8'  \
    LC_ALL='C.UTF-8' \
    TZ=${TZ}

ARG USER
ARG DJANGO_CONFIGURATION
ENV DJANGO_CONFIGURATION=${DJANGO_CONFIGURATION}

# Install necessary apt packages
# mostly are dependencies for cvat
RUN apt-get update && \
    apt-get install -yq \
    software-properties-common \
    wget

RUN add-apt-repository ppa:deadsnakes/ppa -y && \
    apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -yq \
    ffmpeg \
    libgeos-dev \
    libpq-dev \
    python3.7 \
    python3.7-dev \
    python3-pip \
    tzdata \
    unzip \
    unrar \
    p7zip-full \
    vim && \
    ln -fs /usr/bin/python3.7 /usr/bin/python && \
    ln -fs /usr/share/zoneinfo/${TZ} /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata && \
    rm -rf /var/lib/apt/lists/*

RUN python -m pip install -U pip setuptools

# Add and switch to a non-root user
ENV USER="opentpod"
ENV HOME="/home/${USER}"
RUN adduser --shell /bin/bash --disabled-password --gecos "" ${USER}
USER ${USER}
RUN mkdir ${HOME}/openTPOD

# Install and initialize CVAT, copy all necessary files
WORKDIR ${HOME}/openTPOD
COPY requirements/ ./requirements/
RUN python -m pip install --no-cache-dir -r requirements/production.txt

COPY config/ ./config/
COPY cvat/ ./cvat/
COPY opentpod/ ./opentpod/
COPY nginx/ ./nginx/
COPY supervisord/ ./supervisord/
COPY www/ ./www/
COPY static/ ./static/
COPY manage.py ./manage.py

# need to set the environs in some way

# make sure all binary installed by python can be found
ENV PATH="${HOME}/.local/bin/:${PATH}"

# RUN mkdir data share media keys logs /tmp/supervisord
# RUN python3 manage.py collectstatic

# EXPOSE 8080 8443
# ENTRYPOINT ["/usr/bin/supervisord"]
