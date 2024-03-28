#!/bin/bash

source /usr/bin/default-attributes.sh
alias help=$'cat /usr/bin/default-attributes.sh  |sed \'s/=${/ /g\' |sed \'s/:=/ /g\' |sed \'s/}//g\' |sed \'s/ "/ - Default value: "/g\''

function printdate(){
  date '+%Y/%m/%d %H:%M:%S'
}

if [ -n "$SECURE" ];then
export SECURE_LOWKEY=$(echo $SECURE | awk '{print tolower($0)}')
        if [ "$SECURE_LOWKEY" == true ]; then
            echo "[INFO]" - `printdate`" - Creating selfsign Certificates"
            export DATADIR=/var/lib/maxscale
            export CA_KEY=ca-key.pem
            export CA_CERT=ca-cert.pem
            export SERVER_KEY=server-key.pem
            export SERVER_REQ=server-req.pem
            export SERVER_CERT=server-cert.pem
            openssl genrsa 2048 > $DATADIR/$CA_KEY
            openssl req -new -x509 -nodes -days 365000 -key $DATADIR/$CA_KEY -out $DATADIR/$CA_CERT -subj "/C=VN/ST=Hanoi/L=Hanoi/O=SVTECH/CN=maxscale" 2>&1 > /dev/null
            openssl req -newkey rsa:2048 -nodes -days 365000 -keyout $DATADIR/$SERVER_KEY -out $DATADIR/$SERVER_REQ -subj "/C=VN/ST=Hanoi/L=Hanoi/O=SVTECH/CN=maxscale" 2>&1 > /dev/null
            openssl x509 -req -days 365000 -set_serial 01 -in $DATADIR/$SERVER_REQ -out $DATADIR/$SERVER_CERT -CA $DATADIR/$CA_CERT -CAkey $DATADIR/$CA_KEY 2>&1 > /dev/null
            chmod -R 775 $DATADIR/*.pem

		sed -i -e "/^threads.*/d" -e "/\[maxscale\]/a threads=auto" /etc/maxscale.cnf
		sed -i -e "/^admin_host.*/d" -e "/\[maxscale\]/a admin_host=0.0.0.0" /etc/maxscale.cnf	

		echo "[INFO]" - `printdate`" - Config Admin Secure GUI for Maxscale"
		sed -i -e "/^admin_secure_gui.*/d" -e "/admin_host=.*/a admin_secure_gui=true" /etc/maxscale.cnf
		echo "[INF0] - Config selfsign Certificates for Maxscale"
		sed -i -e "/^admin_ssl_key.*/d" -e "/^admin_secure_gui=.*/a admin_ssl_key=$DATADIR/$SERVER_KEY" /etc/maxscale.cnf
		sed -i -e "/^admin_ssl_cert.*/d" -e "/^admin_ssl_key=.*/a admin_ssl_cert=$DATADIR/$SERVER_CERT" /etc/maxscale.cnf
		sed -i -e "/^admin_ssl_ca_cert.*/d" -e "/^admin_ssl_cert=.*/a admin_ssl_ca_cert=$DATADIR/$CA_CERT" /etc/maxscale.cnf
		
		export IGNORE_VERIFY_CERT=$(echo "-s -n false")	
        export PROTOCOL="https"
        fi
else
	export IGNORE_VERIFY_CERT=$(echo "")
    export PROTOCOL="http"
fi

checkAdminUser() {
	unset $CHECK_ADMIN_USER_EXITCODE
	export DEFAULT_ADMIN_USER_EXITCODE=$(maxctrl $IGNORE_VERIFY_CERT list servers 2>&1 > /dev/null; echo $?)
	export NEW_ADMIN_USER_EXITCODE=$(maxctrl $IGNORE_VERIFY_CERT -u $MAXSCALE_ADMIN_USER -p $MAXSCALE_ADMIN_PASSWORD list servers 2>&1 > /dev/null; echo $?)
}

function exitMaxScale {
	/usr/bin/monit unmonitor all
	/usr/bin/maxscale-stop
	/usr/bin/monit quit
}

rm -f /var/run/*.pid
rsyslogd

trap exitMaxScale SIGTERM

exec "$@" &

checkAdminUser
echo ""
echo "========= CREATING NEW ADMIN USER ========="
if [ -n "$MAXSCALE_ADMIN_USER" ] && [ -n "$MAXSCALE_ADMIN_PASSWORD" ];then
	echo -n "[INFO]" - `printdate`" - Creating new admin user: "
	maxctrl $IGNORE_VERIFY_CERT create user $MAXSCALE_ADMIN_USER $MAXSCALE_ADMIN_PASSWORD --type=admin
	echo -n "[INFO]" - `printdate`" - Removing default admin user: "
	maxctrl $IGNORE_VERIFY_CERT destroy user admin
	checkAdminUser
	if [ "$NEW_ADMIN_USER_EXITCODE" == 0 ]; then
		echo "[INFO]" - `printdate`" - New Maxscale Admin user '$MAXSCALE_ADMIN_USER' with password '$MAXSCALE_ADMIN_PASSWORD' has been created successfully"
        export CURL_CREDENTIAL="--user $MAXSCALE_ADMIN_USER:$MAXSCALE_ADMIN_PASSWORD"
	else
		echo "[WARNING] - Can not create new Maxscale Admin user"
		exit 1
	fi
else
        export MAXSCALE_ADMIN_USER="admin"
        export MAXSCALE_ADMIN_PASSWORD="mariadb"
        echo "[INFO]" - `printdate`" - Using default maxscale admin user"
fi

echo ""
echo "======== Maxscale Services Type for the Database Servers ========"
echo -n "[INFO]" - `printdate`" - Creating MariaDB-Monitor service: "
export RESPONSE_CODE=$(curl -s -w "%{http_code}\n" -XPOST "${PROTOCOL}://localhost:8989/v1/monitors" \
--header "Content-Type: application/json" \
--user $MAXSCALE_ADMIN_USER:$MAXSCALE_ADMIN_PASSWORD \
--insecure \
--silent \
-d@- <<EOF
{
    "data": {
        "id": "MariaDB-Monitor",
        "type": "monitors",
        "attributes": {
            "module": "mariadbmon",
            "parameters": {
                "assume_unique_hostnames": "$ASSUME_UNIQUE_HOSTNAMES",
                "auto_failover": "$AUTO_FAILOVER",
                "auto_rejoin": "$AUTO_REJOIN",
                "backend_connect_attempts": "$BACKEND_CONNECT_ATTEMPTS",
                "backend_connect_timeout": "$BACKEND_CONNECT_TIMEOUT",
                "backend_read_timeout": "$BACKEND_READ_TIMEOUT",
                "backend_write_timeout": "$BACKEND_WRITE_TIMEOUT",
                "cooperative_monitoring_locks": "$COOPERATIVE_MONITORING_LOCKS",
                "enforce_read_only_slaves": "$ENFORCE_READ_ONLY_SLAVES",
                "enforce_writable_master": "$ENFORCE_WRITABLE_MASTER",
                "events": "all",
                "failcount": "$FAILCOUNT",
                "failover_timeout": "$FAILCOUNT_TIMEOUT",
                "maintenance_on_low_disk_space": "$MAINTENANCE_ON_LOW_DISK_SPACE",
                "master_conditions": "$MASTER_CONDITIONS",
                "master_failure_timeout": "$MASTER_FAILURE_TIMEOUT",
                "module": "mariadbmon",
                "monitor_interval": "$MONITOR_INTERVAL",
                "user": "$MONITOR_USER",
                "password": "$MONITOR_PASSWORD",
                "replication_password": "$REPLICATION_PASSWORD",
                "replication_user": "$REPLICATION_USER",
                "slave_conditions": "$SLAVE_CONDITIONS",
                "switchover_timeout": "$SWITCHOVER_TIMEOUT",
                "verify_master_failure": "$VERIFY_MASTER_FAILURE"
            }
        }
    }
}
EOF
)
if [[ $RESPONSE_CODE =~ 20[0-9] ]]; then
    echo "OK (CODE: $RESPONSE_CODE)"
else
    echo "FAILED (CODE: $RESPONSE_CODE)"
    exit 1
fi

echo -n "[INFO]" - `printdate`" - Creating Maxscale RW Split service: "
export RESPONSE_CODE=$(curl -s -w "%{http_code}\n" -XPOST "${PROTOCOL}://localhost:8989/v1/services" \
--header "Content-Type: application/json" \
--user $MAXSCALE_ADMIN_USER:$MAXSCALE_ADMIN_PASSWORD \
--insecure \
--silent \
-d@- <<EOF
{
    "data": {
        "id": "maxscale-RW-split",
        "type": "services",
        "attributes": {
            "router": "readwritesplit",
            "parameters": {
                "auth_all_servers": $AUTH_ALL_SERVERS,
                "causal_reads": "$CAUSAL_READS",
                "causal_reads_timeout": "$CAUSAL_READS_TIMEOUT",
                "connection_keepalive": "$CONNECTION_KEEPALIVE",
                "connection_timeout": "$CONNECTION_TIMEOUT",
                "delayed_retry": $DELAYED_RETRY,
                "delayed_retry_timeout": "$DELAYED_RETRY_TIMEOUT",
                "disable_sescmd_history": $DISABLE_SESCMD_HISTORY,
                "enable_root_user": $ENABLE_ROOT_USER,
                "idle_session_pool_time": "$IDLE_SESSION_POOL_TIME",
                "lazy_connect": $LAZY_CONNECT,
                "localhost_match_wildcard_host": $LOCALHOST_MATCH_WILDCARD_HOST,
                "log_auth_warnings": $LOG_AUTH_WARNINGS,
                "log_debug": $LOG_DEBUG,
                "log_info": $LOG_INFO,
                "log_notice": $LOG_NOTICE,
                "log_warning": $LOG_WARNING,
                "master_accept_reads": $MASTER_ACCEPT_READS,
                "master_failure_mode": "$MASTER_FAILURE_MODE",
                "master_reconnection": $MASTER_RECONNECTION,
                "max_connections": $MAX_CONNECTIONS,
                "max_sescmd_history": $MAX_SESCMD_HISTORY,
                "max_slave_connections": $MAX_SLAVE_CONNECTIONS,
                "max_slave_replication_lag": "$MAX_SLAVE_REPLICATION_LAG",
                "net_write_timeout": "$NET_WRITE_TIMEOUT",
                "optimistic_trx": $OPTIMISTIC_TRX,
                "password": "$MAXSCALE_PASSWORD",
                "prune_sescmd_history": $PRUNE_SESCMD_HISTORY,
                "rank": "$RANK",
                "retain_last_statements": $RETAIN_LAST_STATEMENTS,
                "retry_failed_reads": $RETRY_FAILED_READS,
                "reuse_prepared_statements": $REUSE_PREPARED_STATEMENTS,
                "router": "$ROUTER",
                "session_trace": $SESSION_TRACE,
                "session_track_trx_state": $SESSION_TRACK_TRX_STATE,
                "slave_connections": $SLAVE_CONNECTIONS,
                "slave_selection_criteria": "$SLAVE_SELECTION_CRITERIA",
                "strict_multi_stmt": $STRICT_MULTI_STMT,
                "strict_sp_calls": $STRICT_SP_CALLS,
                "strip_db_esc": $STRIP_DB_ESC,
                "transaction_replay": $TRANSACTION_REPLAY,
                "transaction_replay_attempts": $TRANSACTION_REPLAY_ATTEMPTS,
                "transaction_replay_checksum": "$TRANSACTION_REPLAY_CHECKSUM",
                "transaction_replay_max_size": "$TRANSACTION_REPLAY_MAX_SIZE",
                "transaction_replay_retry_on_deadlock": $TRANSACTION_REPLAY_RETRY_ON_DEADLOCK,
                "transaction_replay_retry_on_mismatch": $TRANSACTION_REPLAY_RETRY_ON_MISMATCH,
                "transaction_replay_timeout": "$TRANSACTION_REPLAY_TIMEOUT",
                "type": "service",
                "use_sql_variables_in": "$USE_SQL_VARIABLES_IN",
                "user": "$MAXSCALE_USER",
                "user_accounts_file": $USER_ACCOUNTS_FILE,
                "user_accounts_file_usage": "$USER_ACCOUNTS_FILE_USAGE",
                "version_string": "$VERSION_STRING"
            }
        }
    }
}
EOF
)
if [[ $RESPONSE_CODE =~ ^20[0-9] ]]; then
    echo "OK (CODE: $RESPONSE_CODE)"
else
    echo "FAILED (CODE: $RESPONSE_CODE)"
    exit 1
fi

echo -n "[INFO]" - `printdate`" - Creating Maxscale RW Listener : "
export RESPONSE_CODE=$(curl -s -w "%{http_code}\n" -XPOST "${PROTOCOL}://localhost:8989/v1/listeners" \
--header "Content-Type: application/json" \
--user $MAXSCALE_ADMIN_USER:$MAXSCALE_ADMIN_PASSWORD \
--insecure \
--silent \
-d@- <<EOF
{
    "data": {
        "id": "maxscale-RW-listener",
        "type": "listeners",
        "attributes": {
            "parameters": {
                "address": "::",
                "authenticator": null,
                "authenticator_options": null,
                "connection_init_sql_file": null,
                "port": 4006,
                "protocol": "MariaDBClient",
                "service": "maxscale-RW-split",
                "socket": null,
                "sql_mode": "default",
                "ssl": false,
                "ssl_ca_cert": null,
                "ssl_cert": null,
                "ssl_cert_verify_depth": 9,
                "ssl_cipher": null,
                "ssl_crl": null,
                "ssl_key": null,
                "ssl_verify_peer_certificate": false,
                "ssl_verify_peer_host": false,
                "ssl_version": "MAX",
                "type": "listener",
                "user_mapping_file": null
            }
        },
        "relationships": {
            "services": {
                "data": [
                    {
                        "id": "maxscale-RW-split",
                        "type": "services"
                    }
                ]
            }
        }
    }
}
EOF
)
if [[ $RESPONSE_CODE =~ ^20[0-9] ]]; then
    echo "OK (CODE: $RESPONSE_CODE)"
else
    echo "FAILED (CODE: $RESPONSE_CODE)"
    exit 1
fi

echo "[INFO]" - `printdate`" - Creating Maxscale Servers : "
export VALIDATE_SERVER=fasle
export SPLIT_SERVER=$(echo $SERVER| sed 's/,/ /g')
for i in $SPLIT_SERVER
do
#   if [[ ! $i =~ .*:\/\/((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\.|:)){4}((6553[0-5])|(655[0-2][0-9])|(65[0-4][0-9]{2})|(6[0-4][0-9]{3})|([1-5][0-9]{4})|([0-5]{0,5})|([0-9]{1,4})) ]]; then
#     echo [ERROR] - $i in SERVER parameters is invalid address. Please input correct pattern, such as: "db-01://192.168.10.1:3306"
#     exit 1
#   else
    echo -n "- Creating $i as a backend server: "
    export SERVER_NAME=$(echo $i |sed 's/:.*//g')
    export SERVER_IP=$(echo $i |sed 's/.*\/\///g' |sed 's/:.*//g')
    export SERVER_PORT=$(echo $i |sed 's/.*://g')
    export RESPONSE_CODE=$(curl -s -w "%{http_code}\n" -XPOST "${PROTOCOL}://localhost:8989/v1/servers" \
    --header "Content-Type: application/json" \
    --user $MAXSCALE_ADMIN_USER:$MAXSCALE_ADMIN_PASSWORD \
    --insecure \
    --silent \
    -d@- <<EOF
{
    "data": {
        "id": "$SERVER_NAME",
        "type": "servers",
        "attributes": {
            "parameters": {
                "address": "$SERVER_IP",
                "port": $SERVER_PORT
            }
        },
        "relationships": {
            "services": {
                "data": [
                    {
                        "id": "maxscale-RW-split",
                        "type": "services"
                    }
                ]
            },
            "monitors": {
                "data": [
                    {
                        "id": "MariaDB-Monitor",
                        "type": "monitors"
                    }
                ]
            }
        }
    }
}
EOF
)
    if [[ $RESPONSE_CODE =~ 20[0-9] ]]; then
      echo "OK (CODE: $RESPONSE_CODE)"
    else
      echo "FAILED (CODE: $RESPONSE_CODE)"
      exit 1
    fi
#   fi
done

echo ""
echo "========= NEW DATABASE USER and PRIVILEGES for MAXSCALE ========="
echo "[INFO]" - `printdate`" - Please edit following commands (if needed) and execute them in Mariadb Master-Slave"
echo "[INFO]" - `printdate`" + Creating Maxscale Monitoring user (FOR MONITORING AND SWITCHOVER/FAILOVER BACKEND DATABASES):"
echo "GRANT RELOAD, FILE, SUPER, REPLICATION SLAVE, BINLOG MONITOR ON *.* TO ${MONITOR_USER}@'${MONITOR_USER_SUBNET}' IDENTIFIED BY '${MONITOR_PASSWORD}';"
echo ""
echo "[INFO]" - `printdate`" + Creating Maxscale user (CHECK VALID USER FROM CLIENT ONLY):"
echo "GRANT SHOW DATABASES, REPLICATION SLAVE, BINLOG MONITOR ON *.* TO ${MAXSCALE_USER}@'${MAXSCALE_USER_SUBNET}' IDENTIFIED BY '${MAXSCALE_PASSWORD}';"
echo "GRANT SELECT ON mysql.columns_priv TO maxscale@'${MAXSCALE_USER_SUBNET}';"
echo "GRANT SELECT ON mysql.user TO maxscale@'${MAXSCALE_USER_SUBNET}';"
echo "GRANT SELECT ON mysql.proxies_priv TO maxscale@'${MAXSCALE_USER_SUBNET}';"
echo "GRANT SELECT ON mysql.db TO maxscale@'${MAXSCALE_USER_SUBNET}';"
echo "GRANT SELECT ON mysql.procs_priv TO maxscale@'${MAXSCALE_USER_SUBNET}';"
echo "GRANT SELECT ON mysql.roles_mapping TO maxscale@'${MAXSCALE_USER_SUBNET}';"
echo "GRANT SELECT ON mysql.tables_priv TO maxscale@'${MAXSCALE_USER_SUBNET}';"

echo ""
echo "========= List MariaDB Servers ========="
echo "[INFO]" - `printdate`" - Waiting 5 seconds for Maxscale connect to the Bakend Servers"
sleep 5
maxctrl $IGNORE_VERIFY_CERT -u $MAXSCALE_ADMIN_USER -p $MAXSCALE_ADMIN_PASSWORD list servers
sleep 10

echo ""
echo "========= Printing Maxscale log  ========="
grep "\S" /var/log/maxscale/maxscale.log 
ln -sf /proc/1/fd/1 /var/log/maxscale/maxscale.log
wait
