FROM centos:8

WORKDIR /web/nginx/

ENV BUILD_DEPENDENCIES="wget vim gcc-c++ make cmake pcre pcre-devel zlib zlib-devel geoip geoip-devel libmaxminddb-devel libmaxminddb"

RUN yum update -y &&\
yum install -y epel-release &&\
yum install -y $BUILD_DEPENDENCIES

COPY ./prepare_nginx.sh .
COPY ./nginx.conf .

RUN chmod +x prepare_nginx.sh && ./prepare_nginx.sh

CMD /web/nginx/sbin/nginx -g 'daemon off;'