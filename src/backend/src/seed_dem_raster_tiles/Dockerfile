FROM python:3


WORKDIR /usr/src/app

RUN apt-get update && \
    apt-get install -y --no-install-recommends gdal-bin libgdal-dev

ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

RUN pip install --no-cache-dir matplotlib numpy && \
    pip install GDAL==$(gdal-config --version) --global-option=build_ext --global-option="-I/usr/include/gdal" && \
    pip install gdal2tiles

COPY seed_tiles.py .
COPY seed_dem.py .

CMD python -u seed_tiles.py -d /data -l 6 -g 11
