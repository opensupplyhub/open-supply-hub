FROM logstash:8.15.3

# Install a specific version of the OpenSearch output plugin for Logstash.
# Temporarily increase heap size for plugin installation.
RUN LS_JAVA_OPTS="-Xmx2g" bin/logstash-plugin install --version 2.0.2 logstash-output-opensearch

ENV LS_JAVA_OPTS="-XX:MaxDirectMemorySize=512m"

# 1. Delete configuration samples in the custom image to ensure that the example
# configuration files from the base image are not retained.
# 2. Delete the pipelines.yml file to overwrite it and support multiple
# pipelines.
# 3. Create the folder to save the lock files for the JDBC inputs.
RUN rm -f /usr/share/logstash/pipeline/* \
    && rm -f /usr/share/logstash/config/logstash-sample.conf \
    && rm -f /usr/share/logstash/config/pipelines.yml \
    && mkdir -p /usr/share/logstash/data/plugins/inputs/jdbc

# Copy the PostgreSQL jdbc driver to the external library folder of Logstash.
COPY --chown=logstash:root ./bin/ /usr/share/logstash/logstash-core/lib/jars/

# Copy the Logstash configuration files to the config folder of Logstash.
COPY --chown=logstash:root ./config/ /usr/share/logstash/config/

# Copy the Logstash pipeline configuration files to the pipeline folder of
# Logstash.
COPY --chown=logstash:root ./pipeline/ /usr/share/logstash/pipeline/

# Copy SQL scripts to the sql folder of Logstash.
COPY --chown=logstash:root ./sql/ /usr/share/logstash/sql/

# Copy Ruby scripts to the scripts folder of Logstash.
COPY --chown=logstash:root ./scripts/ /usr/share/logstash/scripts/

# Copy OpenSearch index templates to the indexes folder of Logstash.
COPY --chown=logstash:root ./indexes/ /usr/share/logstash/indexes/

# Copy country formats static_data to the static_data folder of Logstash.
COPY --chown=logstash:root ./static_data/ /usr/share/logstash/static_data/

CMD ["logstash"]
