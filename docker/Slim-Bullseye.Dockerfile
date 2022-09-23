FROM python:3-slim-bullseye
ENV DEBIAN_FRONTEND noninteractive

ARG firefox_ver=105.0
ARG geckodriver_ver=0.31.0
ARG build_rev=0

RUN apt-get update &&\ 
    apt-get upgrade -y &&\
    toolDeps="curl bzip2" &&\
    apt-get install -y --no-install-recommends --no-install-suggests \
      ca-certificates $toolDeps &&\
    apt-get install -y --no-install-recommends --no-install-suggests \
      `apt-cache depends firefox-esr | awk '/Depends:/{print$2}'` \
      libasound2 libxt6 libxtst6
 
RUN curl -fL -o /tmp/firefox.tar.bz2 \
      https://ftp.mozilla.org/pub/firefox/releases/${firefox_ver}/linux-x86_64/en-GB/firefox-${firefox_ver}.tar.bz2 &&\
      tar -xjf /tmp/firefox.tar.bz2 -C /tmp/ &&\
      mv /tmp/firefox /opt/firefox 

RUN curl -fL -o /tmp/geckodriver.tar.gz \
      https://github.com/mozilla/geckodriver/releases/download/v${geckodriver_ver}/geckodriver-v${geckodriver_ver}-linux64.tar.gz &&\
      tar -xzf /tmp/geckodriver.tar.gz -C /tmp/ &&\
      chmod +x /tmp/geckodriver &&\
      mv /tmp/geckodriver /usr/local/bin/ 
 # Cleanup unnecessary stuff
RUN apt-get purge -y --auto-remove \
      -o APT::AutoRemove::RecommendsImportant=false \
        $toolDeps &&\
        rm -rf /var/lib/apt/lists/* /tmp/*

RUN pip install --upgrade pip
RUN pip install selenium lxml webdriver-manager pandas
ENV MOZ_HEADLESS=1
ENV PATH="${PATH}:/opt/firefox"

