FROM postgis/postgis:16-3.4-alpine

WORKDIR /opt/

# --upgrade libexpat: the base image ships libexpat 2.6.x, while the python3
# pulled in by aws-cli is built against expat >= 2.7.2 and fails to import
# pyexpat (XML_SetAllocTrackerActivationThreshold: symbol not found) otherwise.
RUN set -ex && \
    apk update && \
    apk add --no-cache --upgrade libexpat aws-cli jq && \
    mkdir -p /dumps/

COPY ./dump.sh ./dump.sh
CMD ["bash", "dump.sh"]
