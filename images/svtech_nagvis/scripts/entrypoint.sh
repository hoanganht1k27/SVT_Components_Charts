#!/bin/bash

if [ ! -z "${BACKEND_NAME}" -a ! -z "${BACKEND_TYPE}" -a ! -z "${BACKEND_IP}" -a ! -z "${BACKEND_PORT}"  ] ; then
echo "Init backend config:"
cat <<EOF | tee /usr/share/nagvis/etc/nagvis.ini.php
[global]
file_group="apache"
logonmodule="LogonDialog"
refreshtime=60

[paths]
base="/usr/share/nagvis/"
htmlcgi="/grafana"

[index]
showmaps=0
showrotations=0

[automap]
defaultroot="localhost"

[wui]

[worker]

[rotation_demo]
maps="demo-germany,demo-ham-racks,demo-load,demo-muc-srv1,demo-geomap,demo-automap"
interval=15

[states]

[backend_${BACKEND_NAME}]
backendtype="${BACKEND_TYPE}"
socket="tcp:${BACKEND_IP}:${BACKEND_PORT}"

[defaults]
hovertemplate="default"
urltarget="_blank"

hosturl="[htmlcgi]/d/device-dashboard-detail/device-dashboard-detail?orgId=1&var-hostname=[host_name]"
hostgroupurl="[htmlcgi]/d/host-groups-overview/host-groups-overview?orgId=1"
serviceurl="[htmlcgi]/d/service-detail/service-detail?orgId=1&var-hostname=[host_name]&var-servicename=[service_description]"
servicegroupurl="[htmlcgi]/d/service-group-overview/service-group-overview?orgId=1"

backend="${BACKEND_NAME}"
EOF
fi

# tee -a /usr/share/nagvis/share/userfiles/templates/default.hover.html <<EOF
# </br>
# <table class="hover_table" id="graphTable">
#         <tr><th><label>24 Hour Graph for interface [service_description]</label></th></tr>
#         <tr><td><iframe src=/grafana/d-solo/thruk/thruk?histou.js%3ForgId=1&orgId=1&panelId=12&width=750&height=400&var-hostname=[pnp_hostname]&var-interfaces=[service_description]&from=now-24h&to=now width="100%" height="300"  frameborder="1"></td></tr>
# </table>
# EOF

chmod 777 /usr/share/nagvis/var/tmpl/compile
chmod 777 /usr/share/nagvis/var/tmpl/cache
chmod 775 /usr/share/nagvis -R
chown www-data:www-data /usr/share/nagvis -R

exec apache2-foreground
# exec /usr/sbin/apache2ctl -D FOREGROUND