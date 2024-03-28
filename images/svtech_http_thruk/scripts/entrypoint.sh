#!/bin/bash

function check_empty_dir {
    dir="$1"
    default_dir="$2"
    status=`ls -A $dir | grep -v 'lost+found' | grep -v '.stfolder' | wc -l`

    if [[ "$status" != "0" ]]; then
        echo "$dir is not Empty. Take no action"
    else
        echo "$dir is Empty. Push Thruk default config to /etc/thruk:"
        cp -rfvu $default_dir/* $dir
        chown www-data:www-data $dir -R && chmod 775 $dir -R
    fi
}

check_empty_dir "/etc/thruk" "/var/backup/thruk"

if [ ! -z "${BACKEND_NAME}" -a ! -z "${BACKEND_ID}" -a ! -z "${BACKEND_TYPE}" -a ! -z "${BACKEND_IP}" -a ! -z "${BACKEND_PORT}"  ] ; then
echo "Init backend config:"
cat <<EOF | tee /etc/thruk/thruk_local.conf
<Component Thruk::Backend>
    <peer>
      name      = ${BACKEND_NAME}
      id        = ${BACKEND_ID}
      type      = ${BACKEND_TYPE}
      <options>
         peer   = ${BACKEND_IP}:${BACKEND_PORT}
      </options>
    </peer>
</Component>
<configtool>
  core_type     = icinga2
  core_conf     = /etc/icinga2/icinga2.conf
  obj_check_cmd = /run/icinga2/cmd/icinga2.cmd -v /run/icinga2/cmd/icinga2.cmd
</configtool>
EOF
fi

exec apache2-foreground
