FROM logstash:8.13.0

# copy the postgres jdbc driver to the external library folder of logstash
COPY ./bin/ /usr/share/logstash/logstash-core/lib/jars/

# copy the logstash configuration file to the config folder of logstash
COPY config/ /usr/share/logstash/config/

# copy sql script to the root folder of logstash
COPY sql/ /usr/share/logstash/sql/

# copy sql script to the scripts folder of logstash
COPY scripts/ /usr/share/logstash/scripts/

# copy sql script to the indexes folder of logstash
COPY indexes/ /usr/share/logstash/indexes/

CMD ["logstash", "-f", "/usr/share/logstash/config/sync_facilities.conf"]
