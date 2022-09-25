FROM python:3-alpine3.16

# update apk repo
RUN echo "http://dl-4.alpinelinux.org/alpine/v3.16/main" >> /etc/apk/repositories && \
    echo "http://dl-4.alpinelinux.org/alpine/v3.16/community" >> /etc/apk/repositories

RUN apk update && \
    apk add firefox py3-pandas && \
    rm -rf /var/cache/apk/*

# upgrade pip
RUN pip install --upgrade pip

# install selenium lxml
RUN pip install selenium lxml webdriver-manager json2table argparse pathlib

RUN mkdir -p /app
COPY app/* /app

# Set path since we're using prebuilt from alpine
ENV PYTHONPATH /usr/lib/python3.10/site-packages