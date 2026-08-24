# Kafka CLI tools image: provides kafka-topics.sh / kafka-configs.sh /
# kafka-reassign-partitions.sh for kafka.sh (topic creation) and
# fix_replication.sh (OSDEV-3063).

# Pinned, not :latest. `amazonlinux:latest` moves between major versions, and
# AL2 -> AL2023 changes both the package set and what ships in the base image
# (notably: no gzip). A moving base is why a build that passed last month can
# fail with no change to this file.
FROM amazonlinux:2023

ARG KAFKA_SCALA_VERSION=2.13
ARG KAFKA_VERSION=3.8.0
ARG KAFKA_MIRROR=https://archive.apache.org/dist/kafka

ENV KAFKA_HOME=/opt/kafka_${KAFKA_SCALA_VERSION}-${KAFKA_VERSION}

WORKDIR /opt/

# gzip is REQUIRED by `tar -xz` and is not present in the AL2023 base image.
# Without it tar fails with "gzip: Cannot exec" / "Error is not recoverable"
# and exits 2 -- the failure being debugged here.
# gawk: fix_replication.sh parses `--describe` output with awk functions.
#       Already in the base image, listed to keep the dependency explicit.
# curl is already present as curl-minimal; do NOT `dnf install curl`, it
# conflicts with curl-minimal on AL2023.
#
# Corretto 8 has no -headless variant on AL2023 -- the JRE package is exactly
# `java-1.8.0-amazon-corretto` (the -devel suffix is the full JDK, not needed
# to run the CLI tools). This is the package that satisfies the bare
# `java-1.8.0` the original Dockerfile asked for.
# shadow-utils supplies groupadd/useradd for the unprivileged user below.
RUN dnf install -y --setopt=install_weak_deps=False \
        java-1.8.0-amazon-corretto \
        tar \
        gzip \
        gawk \
        shadow-utils \
    && dnf clean all \
    && rm -rf /var/cache/dnf

# curl -f rather than wget: archive.apache.org can answer a rate-limited or
# bot-checked request with an HTML page under HTTP 200. wget saves that as
# kafka_*.tgz and exits 0, so the build only blows up later at `tar`, with no
# hint of why. -f plus the checksum comparison make the download step itself
# fail, and print what actually arrived.
#
# --proto '=https' --proto-redir '=https' pin the transport: KAFKA_MIRROR is a
# build arg, so it can be overridden with an http:// URL, and -L would otherwise
# follow an https -> http redirect. Both curls refuse anything but HTTPS.
RUN set -eu; \
    tarball="kafka_${KAFKA_SCALA_VERSION}-${KAFKA_VERSION}.tgz"; \
    url="${KAFKA_MIRROR}/${KAFKA_VERSION}/${tarball}"; \
    curl -fsSL --proto '=https' --proto-redir '=https' \
        --retry 5 --retry-delay 5 --retry-connrefused -o "${tarball}" "${url}"; \
    expected="$(curl -fsSL --proto '=https' --proto-redir '=https' \
        --retry 5 --retry-delay 5 "${url}.sha512" \
        | tr -d '[:space:]' | tr 'A-F' 'a-f' | sed 's/^.*tgz://')"; \
    actual="$(sha512sum "${tarball}" | cut -d' ' -f1)"; \
    if [ "${expected}" != "${actual}" ]; then \
        echo "ERROR: checksum mismatch for ${tarball}" >&2; \
        echo "  expected: ${expected}" >&2; \
        echo "  actual:   ${actual}" >&2; \
        echo "  first 200 bytes of the downloaded file:" >&2; \
        head -c 200 "${tarball}" >&2; \
        exit 1; \
    fi; \
    tar -xzf "${tarball}"; \
    rm -f "${tarball}"

# Symlink, not a hard link: a hard link silently breaks if the target layer is
# rebuilt, and /usr/local/bin is the conventional place for this.
RUN ln -s "${KAFKA_HOME}/bin/kafka-topics.sh" /usr/local/bin/kafka-topics

# Run as an unprivileged user. The ECS task definition does not set `user`, so
# whatever this image declares is what ./kafka.sh runs as in a deploy.
#
# Only the KAFKA_HOME directory itself is chowned, deliberately NOT -R: the
# extracted distribution is already world-readable (bin/*.sh 755, libs 644), and
# recursively chowning ~100MB of it would duplicate the whole thing into a new
# layer to change nothing but ownership bits. Write access on the directory is
# what is actually needed, because fix_replication.sh creates add-replicas.json
# in its working directory.
RUN groupadd --system --gid 10001 kafka \
    && useradd --system --uid 10001 --gid kafka --no-create-home \
        --home-dir "${KAFKA_HOME}" --shell /sbin/nologin kafka \
    && chown kafka:kafka "${KAFKA_HOME}"

# Every kafka-*.sh wrapper sources kafka-run-class.sh, which does
# `mkdir -p "$LOG_DIR"` with LOG_DIR defaulting to $KAFKA_HOME/logs. Pointing it
# at /tmp keeps that write off the distribution directory entirely.
ENV LOG_DIR=/tmp/kafka-logs

WORKDIR ${KAFKA_HOME}

COPY --chown=kafka:kafka ssl.config kafka.sh fix_replication.sh list.txt ./

RUN chmod +x kafka.sh fix_replication.sh

USER kafka
