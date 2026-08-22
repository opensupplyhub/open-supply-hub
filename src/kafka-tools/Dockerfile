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
RUN dnf install -y --setopt=install_weak_deps=False \
        java-1.8.0-amazon-corretto \
        tar \
        gzip \
        gawk \
    && dnf clean all \
    && rm -rf /var/cache/dnf

# curl -f rather than wget: archive.apache.org can answer a rate-limited or
# bot-checked request with an HTML page under HTTP 200. wget saves that as
# kafka_*.tgz and exits 0, so the build only blows up later at `tar`, with no
# hint of why. -f plus the checksum comparison make the download step itself
# fail, and print what actually arrived.
RUN set -eu; \
    tarball="kafka_${KAFKA_SCALA_VERSION}-${KAFKA_VERSION}.tgz"; \
    url="${KAFKA_MIRROR}/${KAFKA_VERSION}/${tarball}"; \
    curl -fsSL --retry 5 --retry-delay 5 --retry-connrefused -o "${tarball}" "${url}"; \
    expected="$(curl -fsSL --retry 5 --retry-delay 5 "${url}.sha512" \
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

WORKDIR ${KAFKA_HOME}

COPY ssl.config kafka.sh fix_replication.sh list.txt ./

RUN chmod +x kafka.sh fix_replication.sh
