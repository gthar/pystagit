FROM alpine:3.13

RUN mkdir -p /tmp/pystagit
COPY . /tmp/pystagit

RUN apk add --update --no-cache \
        python3 \
        libgit2 && \
    apk add --update --no-cache --virtual .build-deps \
        py3-pip \
        python3-dev \
        musl-dev \
        libffi-dev \
        libgit2-dev \
        gcc && \
    pip install /tmp/pystagit && \
    rm -r /tmp/pystagit && \
    apk del .build-deps && \
    addgroup \
        --gid 10001 \
        pystagit && \
    adduser \
        --uid 10000 \
        --home /data \
        --ingroup pystagit \
        --disabled-password \
        --shell /sbin/nologin \
        pystagit && \
    mkdir -p /data/input /data/outuput

VOLUME /data/input /data/outuput
WORKDIR /data/output
USER pystagit
