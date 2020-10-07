FROM ubuntu:18.04

ENV TERM=xterm \
    LANG='C.UTF-8'  \
    LC_ALL='C.UTF-8' \
    BASH_ENV=/etc/profile

# Install necessary apt packages
# some python package requires gcc when installing from conda, therefore
# installing build-essential, some other dependencies are for cvat
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -yq \
        build-essential \
        ffmpeg \
        git \
        libavcodec-dev \
        libavdevice-dev \
        libavfilter-dev \
        libavformat-dev \
        libavutil-dev \
        libgeos-dev \
        libpq-dev \
        libswresample-dev \
        libswscale-dev \
        p7zip-full \
        pkg-config \
        software-properties-common \
        tzdata \
        unrar \
        unzip \
        vim \
        wget \
 && apt-get clean && rm -rf /var/lib/apt/lists/*

# use conda to manage requirements
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-py37_4.8.3-Linux-x86_64.sh -O ~/miniconda.sh \
 && /bin/bash ~/miniconda.sh -b -p /opt/conda \
 && rm ~/miniconda.sh \
 && /opt/conda/bin/conda update -n base -c defaults conda \
 && /opt/conda/bin/conda clean -tipsy \
 && ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh \
 && echo ". /etc/profile" >> ~/.bashrc  # used by docker exec/run
SHELL [ "/bin/bash", "-c" ]

# Install python dependencies
COPY requirements/ /root/openTPOD/requirements/
WORKDIR /root/openTPOD

RUN MAKEFLAGS=-j8 conda env create -f requirements/environment.yml \
 && echo 'conda activate opentpod-env' > /etc/profile.d/opentpod.sh

# Install nodejs dependencies
COPY frontend/package.json /root/openTPOD/frontend/
RUN cd frontend && npm install

# Copy frontend source and build npm static files
COPY frontend /root/openTPOD/frontend/
RUN cd frontend && npm run-script build

VOLUME /root/openTPOD/static

# Copy rest of the opentpod source
COPY . /root/openTPOD/

EXPOSE 8000
CMD [ "/bin/bash" ]
