# Use the Alpine Linux base image
FROM alpine:3.19.0

# label for github attach this image to Project_Containers github repo
LABEL org.opencontainers.image.source=https://github.com/moophat/SVTECH_Projects_Container

# ENV for process_check_result scripts
ENV ICINGA_HOST="localhost"
ENV ICINGA_PORT="5665"
ENV ICINGA_USER="icingaAdmin"
ENV ICINGA_PASSWORD="icingaAdmin"
# ENV for snmptt.ini
ENV MYSQL_DBI_ENABLE="0"
ENV MYSQL_DBI_HOST="localhost"
ENV MYSQL_DBI_PORT="3306"
ENV MYSQL_DBI_DATABASE="snmptt"
ENV MYSQL_DBI_TABLE="snmptt"
ENV MYSQL_DBI_TABLE_UNKNOWN="snmptt_unknown"
ENV MYSQL_DBI_USERNAME="snmptt"
ENV MYSQL_DBI_PASSWORD="snmptt"
# Install necessary packages
RUN apk add --no-cache tzdata net-snmp snmptt net-snmp-tools perl-dbd-mysql perl-net-ip net-snmp-perl curl tcpdump gettext && \
    rm -rf /var/cache/apk/*
# Set time zone
ENV TZ=Asia/Ho_Chi_Minh
# Copy config
RUN mkdir -p /data/snmptt/ && mkdir -p /data/scripts
COPY ./snmp-conf/ /data/snmptt/
COPY ./scripts/ /data/scripts/
RUN chmod +x /data/scripts/* && chmod +x /data/snmptt/external_command/process_check_result && cp /data/scripts/reload /usr/bin/

# Copy Base MIB
COPY ./base_mibs/ /usr/share/snmp/mibs/
# Expose UDP port 162 for SNMP traps
EXPOSE 162/udp

# Mount volume for /etc/snmp
# VOLUME ["/etc/snmptt/", "/var/log/snmptt/"]

# Start services
ENTRYPOINT [ "/data/scripts/entrypoint.sh" ]
