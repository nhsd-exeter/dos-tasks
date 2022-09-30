FROM python:3.10.2-alpine

# Install python package build requirements
RUN set -eux && \
    apk add --no-cache \
        openssl-dev \
        postgresql-libs \
        musl-dev \
        gcc \
        g++ \
        libffi-dev \
        postgresql-dev
# Copy Python requirements
COPY assets/requirements.txt /
COPY assets/integration/data-files /data-files
# Install Python requirements
RUN python -m pip install -r /requirements.txt --upgrade
