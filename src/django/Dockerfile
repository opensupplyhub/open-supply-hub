FROM --platform=linux/amd64 python:3.7-slim-bookworm

RUN mkdir -p /usr/local/src/static/static
WORKDIR /usr/local/src

COPY requirements.txt /usr/local/src/

# [OSDEV-1785][https://github.com/aio-libs/aiokafka/issues/1093] - Remove aiokafka in requirements.txt to avoid conflicts.
RUN sed -i '/aiokafka/d' requirements.txt

RUN set -ex \
    && buildDeps=" \
    build-essential \
    libpq-dev \
    " \
    && deps=" \
    gdal-bin \
    gettext \
    postgresql-client-15 \
    git \
    curl \
    " \
    && apt-get update && apt-get install -y $buildDeps $deps --no-install-recommends \
    && pip install --no-cache-dir -r requirements.txt \
    # [OSDEV-1785][https://github.com/aio-libs/aiokafka/issues/1093] - Install aiokafka from the forked repo.
    && pip install --no-cache-dir git+https://github.com/opensupplyhub/aiokafka.git@kafka-python-2.0.3 \
    && apt-get purge -y --auto-remove $buildDeps \
    && rm -rf /usr/local/src/requirements.txt /var/lib/apt/lists/*

COPY . /usr/local/src

RUN GOOGLE_SERVER_SIDE_API_KEY="" \
    OAR_CLIENT_KEY="" \
    HUBSPOT_API_KEY="" \
    HUBSPOT_SUBSCRIPTION_ID="" \
    EXTERNAL_DOMAIN="" \
    python manage.py collectstatic --no-input

ENTRYPOINT ["/usr/local/bin/gunicorn"]

CMD ["-b :8080", \
    "--workers=1", \
    "--timeout=180", \
    "--access-logfile=-", \
    "--access-logformat=%({X-Forwarded-For}i)s %(h)s %(l)s %(u)s %(t)s \"%(r)s\" %(s)s %(b)s \"%(f)s\" \"%(a)s\"", \
    "--error-logfile=-", \
    "--log-level=info", \
    "--capture-output", \
    "oar.wsgi"]
