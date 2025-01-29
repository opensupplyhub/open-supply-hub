FROM postgis/postgis:16-3.4-alpine

WORKDIR /opt/

RUN set -ex && \
    apk update && \
    apk add --no-cache aws-cli jq && \
    mkdir -p /dumps/

COPY ./dump.sh ./dump.sh
CMD ["bash", "dump.sh"]
