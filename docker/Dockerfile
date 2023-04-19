FROM python:3-alpine3.16
LABEL maintainer="hanzov69 <hanzo@freezerpants.com>"\
    org.opencontainers.image.authors="hanzov69 <hanzo@freezerpants.com>" \
    architecture="amd64/x86_64" \
    alpine-version="3.16" \
    org.opencontainers.image.title="triumph-tracker" \
    org.opencontainers.image.description="Gunicorn + Flask + Python Docker image running on Alpine Linux for triumph-tracker" \
    org.opencontainers.image.url="https://github.com/hanzov69?tab=packages&repo_name=triumph-tracker-service" \
    org.opencontainers.image.source="https://github.com/hanzov69/triumph-tracker-service" 

ENV ALPINE_VERSION=3.16

# update apk repo
RUN echo "http://dl-4.alpinelinux.org/alpine/v${ALPINE_VERSION}/main" >> /etc/apk/repositories && \
    echo "http://dl-4.alpinelinux.org/alpine/v${ALPINE_VERSION}/community" >> /etc/apk/repositories &&\
    apk update &&\
    apk add bash gcc musl-dev python3-dev

RUN mkdir -p /app
COPY app/ /app/
RUN ls -la /app

RUN pip install --upgrade pip
RUN pip install -U pip setuptools wheel
ENV PYTHONPATH /usr/lib/python3.10/site-packages
RUN pip install -r ./app/requirements.txt

EXPOSE 8000

ENTRYPOINT [ "/app/entry.sh" ]
CMD ["/app/start.sh"]
