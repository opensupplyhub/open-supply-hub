FROM  quay.io/azavea/postgis:3-postgres12.4-slim

WORKDIR /opt/

RUN echo "Hello, World!"
# RUN echo "host.docker.internal:5433:opensupplyhub:opensupplyhub:" > ~/.pgpass
# RUN chmod 600 ~/.pgpass
COPY ./do_work.sh ./do_work.sh
COPY ./initdb.sql /docker-entrypoint-initdb.d
ENV POSTGRES_PASSWORD=anondb
ENV POSTGRES_USER=anondb
ENV POSTGRES_DB=anondb
RUN mkdir -p /dumps/
VOLUME /dumps
# ENTRYPOINT [ "docker-entrypoint.sh" ]
CMD ["sh", "do_work.sh"]

