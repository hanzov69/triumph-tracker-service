FROM python:3-alpine3.16
LABEL maintainer="hanzov69 <hanzo@freezerpants.com>"\
    org.opencontainers.image.authors="hanzov69 <hanzo@freezerpants.com>" \
    architecture="amd64/x86_64" \
    nginx-version="1.22.0" \
    alpine-version="3.16" \
    org.opencontainers.image.title="triumph-tracker" \
    org.opencontainers.image.description="Nginx + Python Docker image running on Alpine Linux for triumph-tracker" \
    org.opencontainers.image.url="https://github.com/hanzov69?tab=packages&repo_name=triumph-tracker-service" \
    org.opencontainers.image.source="https://github.com/hanzov69/triumph-tracker-service" 

ENV NGINX_VERSION=1.22.0
ENV ALPINE_VERSION=3.16

# update apk repo
RUN echo "http://dl-4.alpinelinux.org/alpine/v${ALPINE_VERSION}/main" >> /etc/apk/repositories && \
    echo "http://dl-4.alpinelinux.org/alpine/v${ALPINE_VERSION}/community" >> /etc/apk/repositories &&\
    build_pkgs="build-base linux-headers openssl-dev pcre-dev wget zlib-dev" && \
    runtime_pkgs="ca-certificates openssl pcre zlib tzdata git firefox py3-pandas" && \
    apk update &&\
    apk --no-cache add ${build_pkgs} ${runtime_pkgs}

RUN cd /tmp && \
    wget https://nginx.org/download/nginx-${NGINX_VERSION}.tar.gz && \
    tar xzf nginx-${NGINX_VERSION}.tar.gz && \
    cd /tmp/nginx-${NGINX_VERSION} && \
    ./configure \
    --prefix=/etc/nginx \
    --sbin-path=/usr/sbin/nginx \
    --conf-path=/etc/nginx/nginx.conf \
    --error-log-path=/var/log/nginx/error.log \
    --http-log-path=/var/log/nginx/access.log \
    --pid-path=/var/run/nginx.pid \
    --lock-path=/var/run/nginx.lock \
    --http-client-body-temp-path=/var/cache/nginx/client_temp \
    --http-proxy-temp-path=/var/cache/nginx/proxy_temp \
    --http-fastcgi-temp-path=/var/cache/nginx/fastcgi_temp \
    --http-uwsgi-temp-path=/var/cache/nginx/uwsgi_temp \
    --http-scgi-temp-path=/var/cache/nginx/scgi_temp \
    --user=nginx \
    --group=nginx \
    --with-http_ssl_module \
    --with-http_realip_module \
    --with-http_addition_module \
    --with-http_sub_module \
    --with-http_dav_module \
    --with-http_flv_module \
    --with-http_mp4_module \
    --with-http_gunzip_module \
    --with-http_gzip_static_module \
    --with-http_random_index_module \
    --with-http_secure_link_module \
    --with-http_stub_status_module \
    --with-http_auth_request_module \
    --with-mail \
    --with-mail_ssl_module \
    --with-file-aio \
    --with-threads \
    --with-stream \
    --with-stream_ssl_module \
    --with-stream_realip_module \
    --with-http_slice_module \
    --with-http_v2_module && \
    make && \
    make install && \
    sed -i -e 's/#access_log  logs\/access.log  main;/access_log \/dev\/stdout;/' -e 's/#error_log  logs\/error.log  notice;/error_log stderr notice;/' /etc/nginx/nginx.conf && \
    addgroup -S nginx && \
    adduser -D -S -h /var/cache/nginx -s /sbin/nologin -G nginx nginx && \
    rm -rf /tmp/* && \
    apk del ${build_pkgs} && \
    rm -rf /var/cache/apk/*

COPY files/index.html /app/
COPY files/nginx.conf /etc/nginx/nginx.conf
COPY files/disciple-slayer_status.html.tpl /app/disciple-slayer_status.html
COPY files/rivensbane_status.html.tpl /app/rivensbane_status.html
COPY files/kingslayer_status.html.tpl /app/kingslayer_status.html

RUN rm /etc/crontabs/root
COPY files/triumph-cron /etc/crontabs/root

RUN mkdir -p /app
COPY app/* /app/

RUN pip install --upgrade pip
ENV PYTHONPATH /usr/lib/python3.10/site-packages
RUN pip install -r ./app/requirements.txt

VOLUME ["/var/cache/nginx"]

EXPOSE 80 443

CMD crond && nginx
