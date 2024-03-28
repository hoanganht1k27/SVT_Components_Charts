#!/bin/bash -e

PERMISSIONS_OK=0

if [ ! -r "$GF_PATHS_CONFIG" ]; then
    echo "GF_PATHS_CONFIG='$GF_PATHS_CONFIG' is not readable."
    PERMISSIONS_OK=1
fi

if [ ! -w "$GF_PATHS_DATA" ]; then
    echo "GF_PATHS_DATA='$GF_PATHS_DATA' is not writable."
    PERMISSIONS_OK=1
fi

if [ ! -r "$GF_PATHS_HOME" ]; then
    echo "GF_PATHS_HOME='$GF_PATHS_HOME' is not readable."
    PERMISSIONS_OK=1
fi

if [ $PERMISSIONS_OK -eq 1 ]; then
    echo "You may have issues with file permissions, more information here: http://docs.grafana.org/installation/docker/#migration-from-a-previous-version-of-the-docker-container-to-5-1-or-later"
fi

if [ ! -d "$GF_PATHS_PLUGINS" ]; then
    mkdir "$GF_PATHS_PLUGINS"
fi

if [ ! -z ${GF_AWS_PROFILES+x} ]; then
    > "$GF_PATHS_HOME/.aws/credentials"

    for profile in ${GF_AWS_PROFILES}; do
        access_key_varname="GF_AWS_${profile}_ACCESS_KEY_ID"
        secret_key_varname="GF_AWS_${profile}_SECRET_ACCESS_KEY"
        region_varname="GF_AWS_${profile}_REGION"

        if [ ! -z "${!access_key_varname}" -a ! -z "${!secret_key_varname}" ]; then
            echo "[${profile}]" >> "$GF_PATHS_HOME/.aws/credentials"
            echo "aws_access_key_id = ${!access_key_varname}" >> "$GF_PATHS_HOME/.aws/credentials"
            echo "aws_secret_access_key = ${!secret_key_varname}" >> "$GF_PATHS_HOME/.aws/credentials"
            if [ ! -z "${!region_varname}" ]; then
                echo "region = ${!region_varname}" >> "$GF_PATHS_HOME/.aws/credentials"
            fi
        fi
    done

    chmod 600 "$GF_PATHS_HOME/.aws/credentials"
fi

# Convert all environment variables with names ending in __FILE into the content of
# the file that they point at and use the name without the trailing __FILE.
# This can be used to carry in Docker secrets.
for VAR_NAME in $(env | grep '^GF_[^=]\+__FILE=.\+' | sed -r "s/([^=]*)__FILE=.*/\1/g"); do
    VAR_NAME_FILE="$VAR_NAME"__FILE
    if [ "${!VAR_NAME}" ]; then
        echo >&2 "ERROR: Both $VAR_NAME and $VAR_NAME_FILE are set (but are exclusive)"
        exit 1
    fi
    echo "Getting secret $VAR_NAME from ${!VAR_NAME_FILE}"
    export "$VAR_NAME"="$(< "${!VAR_NAME_FILE}")"
    unset "$VAR_NAME_FILE"
done

export HOME="$GF_PATHS_HOME"

if [ ! -z "${GF_INSTALL_PLUGINS}" ]; then
  OLDIFS=$IFS
  IFS=','
  for plugin in ${GF_INSTALL_PLUGINS}; do
    IFS=$OLDIFS
    if [[ $plugin =~ .*\;.* ]]; then
        pluginUrl=$(echo "$plugin" | cut -d';' -f 1)
        pluginWithoutUrl=$(echo "$plugin" | cut -d';' -f 2)
        grafana-cli --pluginUrl "${pluginUrl}" --pluginsDir "${GF_PATHS_PLUGINS}" plugins install ${pluginWithoutUrl}
    else
        grafana-cli --pluginsDir "${GF_PATHS_PLUGINS}" plugins install ${plugin}
    fi
  done
fi


if [ ! -z "${MYSQL_HOST}" ] && [ ! -z "${MYSQL_PORT}" ] ; then
    sed -i "s,^host = .*,host = ${MYSQL_HOST}:${MYSQL_PORT},g" /etc/grafana/grafana.ini
fi

if [ ! -z "${MYSQL_DB}" ] ; then
    sed -i "s,^name = .*,name = ${MYSQL_DB},g" /etc/grafana/grafana.ini
fi

if [ ! -z "${MYSQL_USER}" ] ; then
    sed -i "s,^user = .*,user = ${MYSQL_USER},g" /etc/grafana/grafana.ini
fi

if [ ! -z "${MYSQL_PASSWORD}" ] ; then
    sed -i "s,^password = .*,password = ${MYSQL_PASSWORD},g" /etc/grafana/grafana.ini
fi

if [ ! -z "${ADMIN_USER}" ] ; then
    sed -i "s,^admin_user = .*,admin_user = ${ADMIN_USER},g" /etc/grafana/grafana.ini
fi

if [ ! -z "${ADMIN_PASSWORD}" ] ; then
    sed -i "s,^admin_password = .*,admin_password = ${ADMIN_PASSWORD},g" /etc/grafana/grafana.ini
fi



TIMEOUT=${TIMEOUT:-60}
result=false
function grafana_is_up {
    sleep 1
    if [ "${TIMEOUT}" == 0 ]; then
        echo "Timeout Waiting grafana Up !"
        result="timeout"
        return 0;
    fi

    echo "Waiting grafana Up ..."
    curl -X GET -u thrukadmin:thrukadmin http://localhost:3000/api/admin/stats &> /dev/null
    if [ $? == 0 ]; then
        result="up"
        echo "Grafana is Up"
        true
    else
        TIMEOUT=$(expr $TIMEOUT - 1)
        false
    fi

    return $?;
}

function import_grafana_entities {
    while ! grafana_is_up ; do true; done
    grafana_dashboard_number=`curl -X GET -u thrukadmin:thrukadmin http://localhost:3000/api/admin/stats | python2 -c "import sys, json; print json.load(sys.stdin)['dashboards']"`
    grafana_datasource_number=`curl -X GET -u thrukadmin:thrukadmin http://localhost:3000/api/admin/stats | python2 -c "import sys, json; print json.load(sys.stdin)['datasources']"`
    if [ "${result}" == "up" ]; then
        if [[ ${grafana_dashboard_number} == 0 && ${grafana_datasource_number} == 0 ]]; then
            cd /opt/grafana-entities && wizzy export datasources && wizzy export dashboards
        fi
    fi
}

if [[ ! -z "${IMPORT_DEFAULT}" && ${IMPORT_DEFAULT} == "true" ]] ; then
    import_grafana_entities &
fi


exec grafana-server                                         \
  --homepath="$GF_PATHS_HOME"                               \
  --config="$GF_PATHS_CONFIG"                               \
  --packaging=docker                                        \
  "$@"                                                      \
  cfg:default.log.mode="console"                            \
  cfg:default.paths.data="$GF_PATHS_DATA"                   \
  cfg:default.paths.logs="$GF_PATHS_LOGS"                   \
  cfg:default.paths.plugins="$GF_PATHS_PLUGINS"             \
  cfg:default.paths.provisioning="$GF_PATHS_PROVISIONING"
