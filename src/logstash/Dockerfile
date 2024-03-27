FROM logstash:8.13.0

# copy the postgres jdbc driver to the external library folder of logstash
COPY ./bin/ /usr/share/logstash/logstash-core/lib/jars/

# copy the logstash configuration file to the config folder of logstash
COPY config/ /usr/share/logstash/config/

CMD ["logstash", "-f", "/usr/share/logstash/config/sync_facilities.conf"]
