#!/bin/sh
# envsubst for snmptt.ini
/usr/bin/envsubst < /data/snmptt/snmptt.ini.tmp > /data/snmptt/snmptt.ini
# Copy config
if [ -d /etc/snmptt/external_command ] && [ -d /etc/snmptt/trapconf ] && [ -f /etc/snmptt/snmptt.ini ] && [ -f /etc/snmptt/snmptrapd.conf ]; then
  echo "Configurations existed"
else
  echo "Configurations do not existed. Copy default configuration into /etc/snmptt"
  cp -R /data/snmptt/* /etc/snmptt/
  chown -R snmptt:root /etc/snmptt/
fi

chown -R snmptt:root /var/log/snmptt/

# Start snmpd
snmpd -LS0-6d &

# Start snmptrapd
snmptrapd -f -Lo -c /etc/snmptt/snmptrapd.conf &

# Start snmptt
if [ -f /var/run/snmptt.pid ]; then
  rm -rf /var/run/snmptt.pid
fi
snmptt --daemon &

# Keep the container running
tail -f /dev/null
