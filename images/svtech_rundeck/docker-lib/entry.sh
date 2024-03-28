#!/bin/bash
# set -eou pipefail

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"

for inc in $(ls $DIR/includes | sort -n); do
    source $DIR/includes/$inc
done

export HOSTNAME=$(hostname)

export RUNDECK_HOME=${RUNDECK_HOME:-/home/rundeck}
export HOME=$RUNDECK_HOME

# Store custom exec command if set so it will not be lost when unset later
EXEC_CMD="${RUNDECK_EXEC_CMD:-}"

export REMCO_HOME=${REMCO_HOME:-/etc/remco}
export REMCO_RESOURCE_DIR=${REMCO_HOME}/resources.d
export REMCO_TEMPLATE_DIR=${REMCO_HOME}/templates
export REMCO_TMP_DIR=/tmp/remco-partials

# Create temporary directories for config partials
mkdir -p ${REMCO_TMP_DIR}/framework
mkdir -p ${REMCO_TMP_DIR}/rundeck-config
mkdir -p ${REMCO_TMP_DIR}/artifact-repositories

remco -config "${REMCO_HOME}/config.toml"



# Generate a new server UUID
if [[ "${RUNDECK_SERVER_UUID}" = "RANDOM" ]] ; then
    RUNDECK_SERVER_UUID=$(uuidgen)
fi
echo "rundeck.server.uuid = ${RUNDECK_SERVER_UUID}" > ${REMCO_TMP_DIR}/framework/server-uuid.properties

# Combine partial config files
cat ${REMCO_TMP_DIR}/framework/* >> etc/framework.properties
cat ${REMCO_TMP_DIR}/rundeck-config/* >> server/config/rundeck-config.properties
cat ${REMCO_TMP_DIR}/artifact-repositories/* >> server/config/artifact-repositories.yaml

# Add some rundeck config
echo 'server.max-http-header-size=640000' >> /home/rundeck/server/config/rundeck-config.properties
echo 'grails.controllers.upload.maxFileSize=2621440000' >> /home/rundeck/server/config/rundeck-config.properties
echo 'grails.controllers.upload.maxRequestSize=2621440000' >> /home/rundeck/server/config/rundeck-config.properties
echo 'rundeck.fileUploadService.tempfile.maxsize=2G' >> /home/rundeck/server/config/rundeck-config.properties
echo 'rundeck.security.httpHeaders.provider.xfo.enabled=false' >> /home/rundeck/server/config/rundeck-config.properties

# Store settings that may be unset in script variables
SETTING_RUNDECK_FORWARDED="${RUNDECK_SERVER_FORWARDED:-false}"


export TZ="${TZ:-Asia/Ho_Chi_Minh}"
rm -rf /etc/localtime
ln -s /usr/share/zoneinfo/$TZ /etc/localtime
echo $TZ > /etc/timezone

export RUNDECK_GRAILS_URL=${RUNDECK_GRAILS_URL:-http://localhost:4440/rundeck}
export RUNDECK_SERVER_CONTEXT_PATH=${RUNDECK_SERVER_CONTEXT_PATH:-/rundeck}

export IMPORT_NMS_JOB=${IMPORT_NMS_JOB:-false}
export IMPORT_AUTOMATION_JOB=${IMPORT_AUTOMATION_JOB:-false}

export OVERRIDE_IMPORT_JOB=${OVERRIDE_IMPORT_JOB:-false}
export RUNDECK_OPTION_PROVIDER_URL=${RUNDECK_OPTION_PROVIDER_URL:-}

export HOST_IP=${HOST_IP:-}

export ICINGA2_REPORT_URL=${ICINGA2_REPORT_URL:-}
export ICINGA2_API_HOST=${ICINGA2_API_HOST:-}
export ICINGA2_CONTAINER=${ICINGA2_CONTAINER:-true}

export RUNDECK_ADMIN_USER=${RUNDECK_ADMIN_USER:-thrukadmin}
export RUNDECK_ADMIN_PASSWORD=${RUNDECK_ADMIN_PASSWORD:-thrukadmin}
export RUNDECK_ADMIN_TOKEN=${RUNDECK_ADMIN_TOKEN:-UkTttnpfh5MC9A3O859k43wPhhWbCsf8}


# Enable multiURL
sed -i 's,#\?.*rundeck.multiURL.enabled.*,rundeck.multiURL.enabled=true,g' /home/rundeck/server/config/rundeck-config.properties

if ! [ -z "${RUNDECK_GRAILS_URL}" ]; then
    sed -i 's,#\?.*grails.serverURL.*\=.*,grails.serverURL\='${RUNDECK_GRAILS_URL}',g' /home/rundeck/server/config/rundeck-config.properties
fi

if ! [ -z "${RUNDECK_SERVER_CONTEXT_PATH}" ]; then
    sed -i 's,#\?.*server.servlet.context-path.*\=.*,server.servlet.context-path\='${RUNDECK_SERVER_CONTEXT_PATH}',g' /home/rundeck/server/config/rundeck-config.properties
fi


if ! [ -z "${RUNDECK_ADMIN_USER}" ] && ! [ -z "${RUNDECK_ADMIN_PASSWORD}" ]; then

    check_exists_admin_user=`grep "${RUNDECK_ADMIN_USER}:${RUNDECK_ADMIN_PASSWORD}" /home/rundeck/server/config/realm.properties | wc -l`
    if ! [[ "$check_exists_admin_user" != "0" ]] ; then

cat << EOF > /home/rundeck/server/config/realm.properties
${RUNDECK_ADMIN_USER}:${RUNDECK_ADMIN_PASSWORD},user,admin
user:user,user
EOF

    fi
fi

if ! [ -z "${RUNDECK_ADMIN_TOKEN}" ] && ! [ -z "${RUNDECK_ADMIN_USER}" ]; then
cat << EOF > /home/rundeck/etc/tokens.properties
${RUNDECK_ADMIN_USER}: ${RUNDECK_ADMIN_TOKEN}, admin
EOF

export check_token=`cat /home/rundeck/etc/framework.properties | grep rundeck.tokens | wc -l`
if [ -e /home/rundeck/etc/tokens.properties ] && [[ "$check_token" = "0" ]]; then
    echo "rundeck.tokens.file=/home/rundeck/etc/tokens.properties" >> /home/rundeck/etc/framework.properties
fi

fi

if [ -d "/opt/SVTECH-Junos-Automation" ]; then
    sed -i 's,#!/opt/.pyenv/versions/automation36/bin/python,#!/usr/bin/env python,g' $(find /opt/SVTECH-Junos-Automation -type f -name "*.py" -not -path "/opt/SVTECH-Junos-Automation/Jsnapy_test/*")
fi


TIMEOUT=${TIMEOUT:-300}
result=false
OVERRIDE_IMPORT_JOB="${OVERRIDE_IMPORT_JOB:-False}"
function rundeck_is_up {
    sleep 1
    if [ "${TIMEOUT}" == 0 ]; then
        echo "Timeout Waiting rundeck Up !"
        result="timeout"
        return 0;
    fi
    export RD_URL=http://localhost:4440/rundeck
    export RD_USER="${RUNDECK_ADMIN_USER}"
    export RD_PASSWORD="${RUNDECK_ADMIN_PASSWORD}"
    echo "Waiting rundeck Up ..."
    rd system info &> /dev/null
    if [ $? == 0 ]; then
        result="up"
        echo "Rundeck is Up"
        true
    else
        TIMEOUT=$(expr $TIMEOUT - 1)
        false
    fi

    return $?;
}

function import_rundeck_job {
    while ! rundeck_is_up ; do true; done

    if [ "${result}" == "up" ]; then
        if [ "${IMPORT_NMS_JOB}" == "true" ]; then
            mkdir -p /tmp/rundeck_import_job/NMS
            cp -rf /opt/SVTECH-Junos-Automation/Rundeck-Projects/NMS/* /tmp/rundeck_import_job/NMS
            if ! [ -z "${RUNDECK_OPTION_PROVIDER_URL}" ]; then
                sed -i 's,http://localhost:1111,'${RUNDECK_OPTION_PROVIDER_URL}',g' /tmp/rundeck_import_job/NMS/*
            fi

            if ! [ -z "${ICINGA2_REPORT_URL}" ]; then
                sed -i 's,http://localhost/report,'${ICINGA2_REPORT_URL}',g' /tmp/rundeck_import_job/NMS/*
                sed -i 's,http://localhost:8888,'${ICINGA2_REPORT_URL}',g' /tmp/rundeck_import_job/NMS/*
            fi

            sed -i 's,filter:\ localhost,filter: rundeck,g' /tmp/rundeck_import_job/NMS/*
            sed -i 's,venv: True,venv: False,g' /tmp/rundeck_import_job/NMS/*
            echo "Import 'Monitoring' Project"
            ansible-playbook /opt/SVTECH-Junos-Automation/Rundeck-Projects/rundeck_import_job.yml --extra-vars "create_project=True override="$OVERRIDE_IMPORT_JOB" project_name=Monitoring rundeck_job_path=/tmp/rundeck_import_job/NMS"

            # # Init Icinga Config
            # cd /etc/icinga2/conf.d/managed && git init && git config --global user.name "icinga" && git config --global user.email 'icinga@"localhost"'
        fi

        if [ "${IMPORT_AUTOMATION_JOB}" == "true" ]; then
            mkdir -p /tmp/rundeck_import_job/Automation
            cp -rf /opt/SVTECH-Junos-Automation/Rundeck-Projects/Automation/* /tmp/rundeck_import_job/Automation
            if ! [ -z "${RUNDECK_OPTION_PROVIDER_URL}" ]; then
                sed -i 's,http://localhost:1111,'${RUNDECK_OPTION_PROVIDER_URL}',g' /tmp/rundeck_import_job/Automation/*
            fi

            sed -i 's,filter:\ localhost,filter: rundeck,g' /tmp/rundeck_import_job/Automation/*
            sed -i 's,venv: True,venv: False,g' /tmp/rundeck_import_job/Automation/*
            echo "Import 'Automation' Project"
            ansible-playbook /opt/SVTECH-Junos-Automation/Rundeck-Projects/rundeck_import_job.yml --extra-vars "create_project=True override="$OVERRIDE_IMPORT_JOB"  project_name=Automation rundeck_job_path=/tmp/rundeck_import_job/Automation"
        fi
    fi

}

if [ "${IMPORT_NMS_JOB}" == "true" ] || [ "${IMPORT_AUTOMATION_JOB}" == "true" ] ; then
    import_rundeck_job &
fi


# Unset all RUNDECK_* environment variables
if [[ "${RUNDECK_ENVARS_UNSETALL:-true}" = "true" ]] ; then
    unset `env | awk -F '=' '{print $1}' | grep -e '^RUNDECK_'`
fi

# Unset specific environment variables
if [[ ! -z "${RUNDECK_ENVARS_UNSETS:-}" ]] ; then
    unset $RUNDECK_ENVARS_UNSETS
    unset RUNDECK_ENVARS_UNSETS
fi



# Support Arbitrary User IDs on OpenShift
if ! whoami &> /dev/null; then
    if [ -w /etc/passwd ]; then
        TMP_PASSWD=$(mktemp)
        cat /etc/passwd > "${TMP_PASSWD}"
        sed -i "\#rundeck#c\rundeck:x:$(id -u):0:rundeck user:${HOME}:/bin/bash" "${TMP_PASSWD}"
        cat "${TMP_PASSWD}" > /etc/passwd
        rm "${TMP_PASSWD}"
    fi
fi

# Exec custom command if provided
if [[ -n "${EXEC_CMD}" ]] ; then
    # shellcheck disable=SC2086
    exec $EXEC_CMD
fi

exec java \
    -XX:+UnlockExperimentalVMOptions \
    -XX:MaxRAMPercentage="${JVM_MAX_RAM_PERCENTAGE}" \
    -Dlog4j.configurationFile="${HOME}/server/config/log4j2.properties" \
    -Dlogging.config="file:${HOME}/server/config/log4j2.properties" \
    -Dloginmodule.conf.name=jaas-loginmodule.conf \
    -Duser.timezone="${TZ}" \
    -Dloginmodule.name=rundeck \
    -Drundeck.jaaslogin=true \
    -Drundeck.jetty.connector.forwarded="${SETTING_RUNDECK_FORWARDED}" \
    "${@}" \
    -jar rundeck.war
