FROM python:3.5.1-slim

COPY . /requirements/

WORKDIR /requirements/

RUN set -x \
    && echo "Asia/Shanghai" > /etc/timezone \
    && dpkg-reconfigure -f noninteractive tzdata \
    && apt-get update \
    && apt-get install gcc g++ make --no-install-recommends -y \
    && pip install -U pip setuptools \
    && pip install -r requirements.txt \
    && find /usr/local -type f -name '*.pyc' -name '*.pyo' -delete \
    && rm -rf ~/.cache/ \
    && apt-get purge gcc make g++ -y \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
