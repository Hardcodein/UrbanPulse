mkdir /web/nginx/modules
mkdir  /web/nginx/run

# Get nginx:
wget https://nginx.org/download/nginx-1.21.3.tar.gz
tar -zxvf nginx-1.21.3.tar.gz
rm  -rf  nginx-1.21.3.tar.gz

cd nginx-1.21.3

# Get geoip module:
wget https://github.com/leev/ngx_http_geoip2_module/archive/refs/tags/3.3.tar.gz
tar -zxvf 3.3.tar.gz
rm  -rf  3.3.tar.gz

# Set flags to suppress errors on 'make' step of building nginx:
export CFLAGS="-Wno-error"
export CXXFLAGS="-Wno-error"

# Build and install nginx:
./configure \
--prefix=/web/nginx \
--modules-path=/web/nginx/modules \
--without-http_fastcgi_module \
--without-http_uwsgi_module \
--without-http_grpc_module \
--without-http_scgi_module \
--without-mail_imap_module \
--without-mail_pop3_module \
--add-dynamic-module=./ngx_http_geoip2_module-3.3

make modules
make
make install

# Update nginx config:
mv /web/nginx/nginx.conf /web/nginx/conf/