FROM python:3.14-rc-bullseye

ENV OSMIUM_VERSION 2.13.1
ENV OSMIUM_TOOL_VERSION 1.7.1

ENV BUILD_DEPENDENCIES="wget g++ cmake cmake-curses-gui make libexpat1-dev zlib1g-dev libbz2-dev libsparsehash-dev \
    libboost-program-options-dev libboost-dev libgdal-dev libproj-dev doxygen graphviz pandoc"

RUN apt-get update && \
    apt-get install -y $BUILD_DEPENDENCIES

# Создаем рабочую директорию внутри контейнера
ENV WORK_DIR /work_dir
WORKDIR $WORK_DIR

RUN wget https://github.com/osmcode/libosmium/archive/v${OSMIUM_VERSION}.tar.gz && \
    tar xzvf v${OSMIUM_VERSION}.tar.gz && \
    rm v${OSMIUM_VERSION}.tar.gz && \
    mv libosmium-${OSMIUM_VERSION} libosmium

RUN cd libosmium && \
    mkdir build && cd build && \
    cmake -DCMAKE_BUILD_TYPE=Release -DBUILD_EXAMPLES=OFF -DBUILD_TESTING=OFF -DINSTALL_PROTOZERO=ON .. && \
    make -j7

RUN wget https://github.com/osmcode/osmium-tool/archive/v${OSMIUM_TOOL_VERSION}.tar.gz && \
    tar xzvf v${OSMIUM_TOOL_VERSION}.tar.gz && \
    rm v${OSMIUM_TOOL_VERSION}.tar.gz && \
    mv osmium-tool-${OSMIUM_TOOL_VERSION} osmium-tool

RUN cd osmium-tool && \
    mkdir build && cd build && \
    cmake -DOSMIUM_INCLUDE_DIR=$WORK_DIR/libosmium/include/ .. && \
    make -j7

RUN mv $WORK_DIR/osmium-tool/build/src/osmium /usr/bin/osmium

# Копируем скрипт в контейнер
COPY ./Start.py $WORK_DIR

# Создаем точку монтирования для хостовой директории
RUN mkdir -p /data

# Указываем volume для сохранения данных на хосте
VOLUME /data

# Изменяем команду запуска, чтобы использовать смонтированную директорию
CMD python Start.py --dir /data --cities $cities