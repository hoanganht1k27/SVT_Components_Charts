# vim:set ft=dockerfile:
FROM ubuntu:jammy

LABEL org.opencontainers.image.source=https://github.com/moophat/SVTECH_Projects_Container

ENV MXS_VERSION=6.4.13

# Update System
RUN apt-get update -y \
 && apt-get -qq --no-install-recommends -y install dnsutils curl ca-certificates findutils monit libncurses5-dev net-tools rsyslog openssl procps tini \
 && apt-get clean all \
 && rm -rf /var/cache/apt/archives /var/lib/apt/lists/*

# Add MariaDB Enterprise Repo
RUN curl -LsS https://downloads.mariadb.com/MariaDB/mariadb_repo_setup | \
    bash -s -- --mariadb-maxscale-version=${MXS_VERSION} --apply 

# Install Maxscale
RUN apt-get -qq --no-install-recommends -y install maxscale \
 && apt-get clean all \
 && rm -rf /var/cache/apt/archives /var/lib/apt/lists/*

# Copy Files To Image
COPY config /tmp/config
COPY scripts /tmp/scripts

RUN cp -rf /tmp/config/maxscale.cnf /etc/ \
 && cp -rf /tmp/config/monit/ /etc/monit/ \
 && cp -rf /tmp/scripts/maxscale-start /usr/bin/ \
 && cp -rf /tmp/scripts/maxscale-stop /usr/bin/ \
 && cp -rf /tmp/scripts/maxscale-restart /usr/bin/ \
 && cp -rf /tmp/scripts/docker-entrypoint.sh /usr/bin/ \
 && cp -rf /tmp/scripts/default-attributes.sh /usr/bin/ \
 && chmod +x /usr/bin/maxscale-start /usr/bin/maxscale-stop /usr/bin/maxscale-restart

# Expose MariaDB Port
EXPOSE 3306

# Expose REST API port
EXPOSE 8989

# Create Persistent Volume
VOLUME ["/var/lib/maxscale"]

# Make Entrypoint Executable & Create Legacy Symlink
RUN chmod +x /usr/bin/docker-entrypoint.sh /usr/bin/default-attributes.sh \
 && ln -s /usr/bin/docker-entrypoint.sh /docker-entrypoint.sh \
 && ln -s /usr/bin/default-attributes.sh /default-attributes.sh 
 
# Clean System & Reduce Size
RUN sed -i 's|SysSock.Use="off"|SysSock.Use="on"|' /etc/rsyslog.conf && \
    sed -i 's|^.*module(load="imjournal"|#module(load="imjournal"|g' /etc/rsyslog.conf && \
    sed -i 's|^.*StateFile="imjournal.state")|#  StateFile="imjournal.state"\)|g' /etc/rsyslog.conf && \
    sed -i '/imklog/s/^/#/' /etc/rsyslog.conf && \
    find /var/log -type f -exec cp /dev/null {} \; && \
    cat /dev/null > ~/.bash_history && \
    chmod -R 700 /etc/monit/monitrc
    
# Start Up
ENTRYPOINT ["/usr/bin/tini","--","docker-entrypoint.sh"]

CMD maxscale-start && monit -I
