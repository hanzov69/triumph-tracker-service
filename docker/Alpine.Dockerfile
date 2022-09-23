FROM python:3-alpine3.16
ENV GECKODRIVER_VER v0.31.0

# update apk repo
RUN echo "http://dl-4.alpinelinux.org/alpine/v3.16/main" >> /etc/apk/repositories && \
    echo "http://dl-4.alpinelinux.org/alpine/v3.16/community" >> /etc/apk/repositories

RUN apk update && \
    apk add firefox py3-pandas && \
    rm -rf /var/cache/apk/*

# upgrade pip
RUN pip install --upgrade pip

# install selenium lxml
RUN pip install selenium lxml webdriver-manager

# Set path since we're using prebuilt from alpine
ENV PYTHONPATH /usr/lib/python3.10/site-packages