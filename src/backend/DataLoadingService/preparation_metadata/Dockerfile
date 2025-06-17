FROM node:10

ENV WORK_DIR /work_dir
WORKDIR $WORK_DIR

RUN npm install circle-to-polygon turf

COPY create_circle_around_city.js $WORK_DIR

CMD node create_circle_around_city.js $osm_dir
