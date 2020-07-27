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
# some python package requires gcc when installing from conda, therefore
# installing build-essential, some other dependencies are for cvat
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -yq \
    build-essential \
    ffmpeg \
    libgeos-dev \
    libpq-dev \
    p7zip-full \
    software-properties-common \
    tzdata \
    unrar \
    unzip \
    vim \
    wget \
 && apt-get clean && rm -rf /var/lib/apt/lists/* \
 && ln -fs /usr/share/zoneinfo/${TZ} /etc/localtime \
 && dpkg-reconfigure -f noninteractive tzdata

# use conda to manage requirements
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-4.5.11-Linux-x86_64.sh -O ~/miniconda.sh \
 && /bin/bash ~/miniconda.sh -b -p /opt/conda \
 && rm ~/miniconda.sh \
 && /opt/conda/bin/conda clean -tipsy \
 && ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh \
 && sed -i 's/mesg n/test -t 0 \&\& mesg n/' ~/.profile
SHELL ["/bin/bash", "-lc"]

# Install python dependencies
COPY requirements/ /root/openTPOD/requirements/
WORKDIR /root/openTPOD
RUN conda env create -f requirements/environment.yml \
 && echo 'conda activate opentpod-env' >> ~/.profile

# Install nodejs dependencies
COPY frontend/package.json /root/openTPOD/frontend/
RUN cd frontend && npm install

# Copy frontend source and build npm static files
COPY frontend /root/openTPOD/frontend/
RUN cd frontend && npm run-script build

VOLUME /root/openTPOD/www

# Copy rest of the opentpod source
COPY . /root/openTPOD/

EXPOSE 8000
CMD ./run-development.sh
