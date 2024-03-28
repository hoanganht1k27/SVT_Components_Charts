#!/bin/bash

if [ "${ROLE}" == "master" ]; then
    echo "Setup Master node:"
    icinga2 node setup --master \
        --cn ${COMMON_NAME} \
        --zone ${ZONE} \
        --listen ${ICINGA_HOST},${ICINGA_PORT} \
        --accept-commands --accept-config
    echo "Set TicketSalt for master"
    sed -i 's/^const TicketSalt.*/const TicketSalt = "b31d379c4093b2dd1f5f3b10db0d08a6"/g' /etc/icinga2/constants.conf

elif [ "${ROLE}" == "satellite" ]; then
    echo "Generate trusted-parent.crt:"
    icinga2 pki save-cert \
        --trustedcert /var/lib/icinga2/certs/trusted-parent.crt \
        --host ${PARENT_HOST} \
        --port ${PARENT_PORT}

    echo "Generate ticket string for satellite node:"
    ticket_string=$(icinga2 pki ticket --salt b31d379c4093b2dd1f5f3b10db0d08a6 --cn ${COMMON_NAME})

    echo "Setup satellite node:"
    icinga2 node setup --ticket ${ticket_string} \
        --cn ${COMMON_NAME} \
        --endpoint ${PARENT_NAME} \
        --zone ${ZONE} \
        --parent_zone ${PARENT_ZONE} \
        --parent_host ${PARENT_HOST} \
        --trustedcert /var/lib/icinga2/certs/trusted-parent.crt \
        --accept-commands --accept-config
fi

if [ "${INFLUXDB_ENABLE}" == "true" ]; then
echo "Enable influxdb:"
icinga2 feature enable influxdb
cat <<EOF | tee /etc/icinga2/features-available/influxdb.conf
library "perfdata"
object InfluxdbWriter "influxdb" {
  host = "${INFLUXDB_HOST:-localhost}"
  port = ${INFLUXDB_PORT:-8086}
  database = "${INFLUXDB_DATABASE:-influxdb_nms}"
  username = "${INFLUXDB_USER:-juniper}"
  password = "${INFLUXDB_PASSWORD:-juniper@123}"
  host_template = {
    measurement = "\$host.check_command$"
    tags = {
      hostname = "\$host.name$"
      address = "\$host.address$"
      device_type = "\$host.vars.device_type$"
      state = "\$host.state$"
      state_type = "\$host.state_type$"
      model = "\$host.vars.model$"
    }
  }
  service_template = {
    measurement = "\$service.check_command$"
    tags = {
      hostname = "\$host.name$"
      service = "\$service.name$"
      service_type = "\$service.vars.service_type$"
      state = "\$service.state$"
      state_type = "\$service.state_type$"
    }
  }
  enable_send_thresholds = true
}
EOF

fi


if [ "${IDO_ENABLE}" == "true" ]; then
  echo "Enable ido-mysql:"
  icinga2 feature enable ido-mysql

  if [ ! -z "${IDO_CLEANUP_STATEHISTORY}" ]; then
    statehistory_age="statehistory_age = ${IDO_CLEANUP_STATEHISTORY}"
  else
    statehistory_age=""
  fi

  if [ ! -z "${IDO_CLEANUP_NOTIFICAION}" ]; then
    notifications_age="notifications_age = ${IDO_CLEANUP_NOTIFICAION}"
  else
    notifications_age=""
  fi

  if [ ! -z "${IDO_CLEANUP_SERVICECHECK}" ]; then
    hostchecks_age="hostchecks_age = ${IDO_CLEANUP_SERVICECHECK}"
    servicechecks_age="servicechecks_age = ${IDO_CLEANUP_SERVICECHECK}"
  else
    hostchecks_age=""
    servicechecks_age=""
  fi

cat <<EOF | tee /etc/icinga2/features-available/ido-mysql.conf
object IdoMysqlConnection "ido-mysql" {
  user = "${IDO_USER:-icinga}"
  password = "${IDO_PASSWORD:-icinga}"
  host = "${IDO_HOST:-localhost}"
  port = "${IDO_PORT:-3306}"
  database = "${IDO_DATABASE:-icinga}"
  categories = ${IDO_CATEGORIES}

  cleanup = {
    ${statehistory_age}
    ${notifications_age}
    ${hostchecks_age}
    ${servicechecks_age}
  }
}
EOF
fi

if [ "${NOTI_ENABLE}" == "true" ]; then
sed -i 's,^mailhub.*,mailhub='${MAILHUB_HOST}':'${MAILHUB_PORT}',g' /etc/ssmtp/ssmtp.conf
cat <<EOF | tee /etc/ssmtp/revaliases
root:${RELAY_EMAIL}:${MAILHUB_HOST}:${MAILHUB_PORT}
juniper:${RELAY_EMAIL}:${MAILHUB_HOST}:${MAILHUB_PORT}
icinga:${RELAY_EMAIL}:${MAILHUB_HOST}:${MAILHUB_PORT}
rundeck:${RELAY_EMAIL}:${MAILHUB_HOST}:${MAILHUB_PORT}
EOF
fi

# Enable and config icingadb feature
if [ "${ICINGADB_ENABLE}" == "true" ]; then
echo "Enable icingadb:"
icinga2 feature enable icingadb
cat <<EOF | tee /etc/icinga2/features-enabled/icingadb.conf
library "icingadb"
object IcingaDB "icingadb" {
    host = "${REDIS_HOST:-localhost}"
    port = ${REDIS_PORT:-6379}
}
EOF
fi

if [ -z "$1" ] && [ "$1" != "no_start" ]; then
  echo "Start Icinga2:"
  exec /tini -- icinga2 daemon
fi

