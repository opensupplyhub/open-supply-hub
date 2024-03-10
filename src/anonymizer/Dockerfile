FROM postgres:12-alpine3.18

COPY ./scripts/entrypoint.sh /usr/local/bin/

COPY ./input/dump.dump /usr/local/bin/dump_file.custom

COPY ./scripts/anonimize_script.sql /scripts/

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

CMD ["postgres"]

