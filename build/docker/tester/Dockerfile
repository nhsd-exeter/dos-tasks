FROM python:3.10.2-alpine

# Install python package build requirements
RUN set -eux && \
    apk add --no-cache \
        openssl-dev \
        postgresql-libs \
        musl-dev \
        gcc \
        libffi-dev \
        postgresql-dev
# Copy Python requirements
COPY assets/requirements.txt /
# Install Python requirements
RUN python -m pip install -r /requirements.txt --upgrade
