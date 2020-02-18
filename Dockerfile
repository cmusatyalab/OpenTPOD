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

# Install necessary apt packages
# mostly are dependencies for cvat
RUN apt-get update && \
    apt-get install -yq \
    software-properties-common \
    wget

# some python package requires gcc when installing from conda, therefore
# installing build-essential
RUN add-apt-repository ppa:deadsnakes/ppa -y && \
    apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -yq \
    build-essential \
    ffmpeg \
    libgeos-dev \
    libpq-dev \
    tzdata \
    unzip \
    unrar \
    p7zip-full \
    vim && \
    ln -fs /usr/share/zoneinfo/${TZ} /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata && \
    rm -rf /var/lib/apt/lists/*

# python3.7 \
# python3.7-dev \
# python3-pip \
# ln -fs /usr/bin/python3.7 /usr/bin/python && \
# RUN python -m pip install -U pip setuptools

# use conda to manage requirements
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-4.5.11-Linux-x86_64.sh -O ~/miniconda.sh && \
    /bin/bash ~/miniconda.sh -b -p /opt/conda && \
    rm ~/miniconda.sh && \
    /opt/conda/bin/conda clean -tipsy && \
    ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
    echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc

# Install and initialize CVAT, copy all necessary files
RUN mkdir -p /root/openTPOD
WORKDIR /root/openTPOD

COPY requirements/ ./requirements/

RUN ["/bin/bash", "-lc", "conda env create -f requirements/environment.yml"]
# RUN python -m pip install --no-cache-dir -r requirements/production.txt

COPY config/ ./config/
COPY cvat/ ./cvat/
COPY opentpod/ ./opentpod/
COPY nginx/ ./nginx/
COPY supervisord/ ./supervisord/
COPY www/ ./www/
COPY static/ ./static/
COPY manage.py ./manage.py

# RUN mkdir data share media keys logs /tmp/supervisord
# RUN python3 manage.py collectstatic

EXPOSE 8000
CMD ["/bin/bash", "-lc", "conda activate opentpod-env && supervisord -n -c supervisord/production.conf"]
