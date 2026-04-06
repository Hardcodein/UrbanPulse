FROM ubuntu:20.04@sha256:b4f9e18267eb98998f6130342baacaeb9553f136142d40959a1b46d6401f0f2b

# Setting Time Zone for install tzdata
ENV DEBIAN_FRONTEND noninteractive
ENV TZ Europe/Moscow

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
    software-properties-common \
    gcc \
    g++ \
    gdb \
    git \
    pkg-config \
    python3-dev \
    python3-tk \
    python3-pip \
    python3-opencv \
    python3-dbg \
    python3-setuptools \
    libcairo2-dev \
    wget

# installing GDAL-dependencies
RUN add-apt-repository ppa:ubuntugis/ppa && \
    apt-get update -y && \
    apt-get install -y --no-install-recommends \
    gdal-bin \
    libgdal-dev


# Update C env vars so compiler can find gdal
ENV CPLUS_INCLUDE_PATH /usr/include/gdal
ENV C_INCLUDE_PATH /usr/include/gdal

# GDAL needs to be installed before numpy
RUN pip3 install -U GDAL==$(gdal-config --version) --global-option=build_ext --global-option="-I/usr/include/gdal"

# install pycairo for pip3-check
RUN pip3 install pycairo

# Cleaning
RUN apt-get clean && \
    rm -rf /var/cache/apt/* && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /tmp/*

RUN rm -f /usr/bin/python && ln -s /usr/bin/python3 /usr/bin/python

# Install GoLang

RUN wget -P /tmp https://dl.google.com/go/go1.13.linux-amd64.tar.gz

RUN tar -C /usr/local -xzf /tmp/go1.13.linux-amd64.tar.gz
RUN rm /tmp/go1.13.linux-amd64.tar.gz

ENV GOPATH /go
ENV PATH $GOPATH/bin:/usr/local/go/bin:$PATH
RUN mkdir -p "$GOPATH/src" "$GOPATH/bin" && chmod -R 777 "$GOPATH"

WORKDIR $GOPATH

# Install import OSM
RUN wget https://github.com/omniscale/imposm3/releases/download/v0.14.1/imposm-0.14.1-linux-x86-64.tar.gz &&\
tar -xzf imposm-0.14.1-linux-x86-64.tar.gz

COPY requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt

RUN pip3 check

COPY res ./res
COPY Loader ./Loader

COPY Start.py .
#  --from-stage create_filters_coverage --to-stage create_filters_coverage create_infrastructure_coverage
CMD python3 -u Start.py --osm-dir $OSM_DIR --cities $CITIES
