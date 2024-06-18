FROM logstash:8.13.4

# Install a specific version of the OpenSearch output plugin for Logstash.
RUN bin/logstash-plugin install --version 2.0.2 logstash-output-opensearch

# Delete configuration samples in the custom image to ensure that the example
# configuration files from the base image are not retained.
RUN rm -f /usr/share/logstash/pipeline/* \
    && rm -f /usr/share/logstash/config/logstash-sample.conf

# Copy the PostgreSQL jdbc driver to the external library folder of Logstash.
COPY --chown=logstash:root ./bin/ /usr/share/logstash/logstash-core/lib/jars/

# Copy the Logstash configuration file to the config folder of Logstash.
COPY --chown=logstash:root ./config/ /usr/share/logstash/config/

# Copy the Logstash pipeline configuration file to the pipeline folder of
# Logstash.
COPY --chown=logstash:root ./pipeline/ /usr/share/logstash/pipeline/

# Copy sql script to the root folder of Logstash.
COPY --chown=logstash:root ./sql/ /usr/share/logstash/sql/

# Copy sql script to the scripts folder of Logstash.
COPY --chown=logstash:root ./scripts/ /usr/share/logstash/scripts/

# Copy sql script to the indexes folder of Logstash.
COPY --chown=logstash:root ./indexes/ /usr/share/logstash/indexes/

CMD ["logstash"]
