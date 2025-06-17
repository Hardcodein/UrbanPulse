## Docker for running nginx with geoip support
- Installs maxmind geoip2 databases
- Downloads [leev/ngx_http_geoip2_module](https://github.com/leev/ngx_http_geoip2_module) nginx module. It creates variables with 
values from the maxmind geoip2 databases based on the client IP
- Builds from source nginx with ngx_http_geoip2_module module
- Runs nginx which sets geo-related headers

## Building & running
```bash
docker build -t homehub_geoip:latest .
docker run -p 8004:80 homehub_geoip:latest
```