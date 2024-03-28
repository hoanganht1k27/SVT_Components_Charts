#!/bin/sh

source /bin/default-attributes.sh
alias testhelp=$'cat /bin/default-attributes.sh  |sed \'s/=${/ /g\' |sed \'s/:=/ /g\' |sed \'s/}//g\' |sed \'s/ "/ - Default value: "/g\''

if [ "$(id -u)" = '0' ]; then
  binary="$1"
  if [ "${PCAP:-}" == "" ] ; then
    # If Syncthing should have no extra capabilities, make sure to remove them
    # from the binary. This will fail with an error if there are no
    # capabilities to remove, hence the || true etc.
    setcap -r "$binary" 2>/dev/null || true
  else
    # Set capabilities on the Syncthing binary before launching it.
    setcap "$PCAP" "$binary"
  fi

  chown "${PUID}:${PGID}" "${HOME}" \
    && exec su-exec "${PUID}:${PGID}" \
       env HOME="$HOME" "$@" &
else
  exec "$@" &
fi

function checkresponse() {
	if [[ $RESPONSE_CODE =~ ^20[0-9] ]]; then
	  echo "OK (CODE: $RESPONSE_CODE)" 
	else
	  echo "FAILED (CODE: $RESPONSE_CODE)" 
	  exit 1
	fi
}
function printdate(){
  date '+%Y/%m/%d %H:%M:%S'
}
export LOG_PREFIX=$(echo [$HOSTNAME/"SVTECH-INIT-CONFIG]" | tr '[:lower:]' '[:upper:]')

# Healthcheck syncthing startup
echo "========= SYNCTHING STARTUP CONFIG ========="
sleep 30
export COUNT=0
until [[ $RESPONSE_CODE =~ ^20[0-9] ]]
do
   export RESPONSE_CODE=$(curl -s -o /dev/null -w "%{http_code}\n" "http://localhost:8384/rest/noauth/health")
   sleep 3
   export COUNT=$(($COUNT + $INTERVAL_HEALTHCHECK))
   if [[ $COUNT = $TIMEOUT ]]; then
     echo "$LOG_PREFIX" `printdate` "ERROR: Syncthing process failed to start (RESPONSE_CODE=${RESPONSE_CODE}, INTERVAL=${INTERVAL_HEALTHCHECK}s, TIMEOUT=$TIMEOUT)"
     exit 1
   fi
done
echo -n "$LOG_PREFIX" `printdate` "INFO: Checking syncthing process is ready to use (INTERVAL=${INTERVAL_HEALTHCHECK}s, TIMEOUT=${TIMEOUT}): "
checkresponse

echo -n "$LOG_PREFIX" `printdate` "INFO: Config GUI Authentication: "
export RESPONSE_CODE=$(curl -s -o /dev/null -w "%{http_code}\n" -XPUT "http://localhost:8384/rest/config/gui" \
--header "Content-Type: application/json" \
--header "X-API-Key: $STGUIAPIKEY" \
-d@- << EOF
{
  "user": "$STGUIUSER",
  "password": "$STGUIPASSWORD"
}
EOF
)
checkresponse

sleep 5

echo -n "$LOG_PREFIX" `printdate` "INFO: Config default folder settings: "
export RESPONSE_CODE=$(curl -L -s -o /dev/null -w "%{http_code}\n" -XPUT "http://localhost:8384/rest/config/defaults/folder" \
--header "Content-Type: application/json" \
--header "X-API-Key: $STGUIAPIKEY" \
-d@- << EOF
{
  "rescanIntervalS": $FOLDERS_RESCANINTERVALS,
  "fsWatcherEnabled": $FOLDERS_FSWATCHERENABLED,
  "fsWatcherDelayS": $FOLDERS_FSWATCHERDELAYS,
  "versioning": {
      "type": "$FOLDERS_VERSIONING_TYPE", 
      "params": {
          "cleanoutDays": "$FOLDERS_VERSIONING_PARAMS_CLEANOUTDAYS"
      },
      "cleanupIntervalS": $FOLDERS_VERSIONING_CLEANUPINTERVALS,
      "fsPath": "$FOLDERS_VERSIONING_FSPATH",
      "fsType": "$FOLDERS_VERSIONING_FSTYPE"
  },
  "maxConflicts": $FOLDERS_MAXCONFLICTS,
  "copyOwnershipFromParent": $FOLDERS_COPYOWNERSHIPFROMPARENT,
  "maxConcurrentWrites": $FOLDERS_MAXCONCURRENTWRITES,
  "caseSensitiveFS": $FOLDERS_CASESENSITIVEFS,
  "junctionsAsDirs": $FOLDERS_JUNCTIONSASDIRS,
  "syncOwnership": $FOLDERS_SYNCOWNERSHIP,
  "sendOwnership": $FOLDERS_SENDOWNERSHIP,
  "syncXattrs": $FOLDERS_SYNCXATTRS,
  "sendXattrs": $FOLDERS_SENDXATTRS,
  "xattrFilter": {
      "entries": $FOLDERS_XATTRFILTER_ENTRIES,
      "maxSingleEntrySize": $FOLDERS_XATTRFILTER_MAXSINGLEENTRYSIZE,
      "maxTotalSize": $FOLDERS_XATTRFILTER_MAXTOTALSIZE
  }
}
EOF
)
checkresponse

echo -n "$LOG_PREFIX" `printdate` "INFO: Config default device settings: "
export RESPONSE_CODE=$(curl -L -s -o /dev/null -w "%{http_code}\n" -XPUT "http://localhost:8384/rest/config/defaults/device" \
--header "Content-Type: application/json" \
--header "X-API-Key: $STGUIAPIKEY" \
-d@- << EOF
{
  "deviceID": "$DEVICE_DEVICEID",
  "name": "$DEVICE_NAME",
  "addresses": [
    "$DEVICE_ADDRESSES"
  ],
  "compression": "$DEVICE_COMPRESSION",
  "certName": "$DEVICE_CERTNAME",
  "introducer": $DEVICE_INTRODUCER,
  "skipIntroductionRemovals": $DEVICE_SKIPINTRODUCTIONREMOVALS,
  "introducedBy": "$DEVICE_INTRODUCEDBY",
  "paused": $DEVICE_PAUSED,
  "allowedNetworks": ["$DEVICE_ALLOWEDNETWORKS"],
  "autoAcceptFolders": $DEVICE_AUTOACCEPTFOLDERS,
  "maxSendKbps": $DEVICE_MAXSENDKBPS,
  "maxRecvKbps": $DEVICE_MAXRECVKBPS,
  "ignoredFolders": $DEVICE_IGNOREDFOLDERS,
  "maxRequestKiB": $DEVICE_MAXREQUESTKIB,
  "untrusted": $DEVICE_UNTRUSTED,
  "remoteGUIPort": $DEVICE_REMOTEGUIPORT
}
EOF
)
checkresponse

echo "$LOG_PREFIX" `printdate` "INFO: Config Options: "
export RESPONSE_CODE=$(curl -L -s -o /dev/null -w "%{http_code}\n" -XPUT "http://localhost:8384/rest/config/options" \
--header "Content-Type: application/json" \
--header "X-API-Key: $STGUIAPIKEY" \
-d@- << EOF
{
  "listenAddresses": $OPTION_LISTENADDRESSES,
  "globalAnnounceServers": ["$OPTION_GLOBALANNOUNCESERVERS"],
  "globalAnnounceEnabled": $OPTION_GLOBALANNOUNCEENABLED,
  "localAnnounceEnabled": $OPTION_LOCALANNOUNCEENABLED,
  "localAnnouncePort": $OPTION_LOCALANNOUNCEPORT,
  "localAnnounceMCAddr": "$OPTION_LOCALANNOUNCEMCADDR",
  "reconnectionIntervalS": $OPTION_RECONNECTIONINTERVALS,
  "relaysEnabled": $OPTION_RELAYSENABLED,
  "relayReconnectIntervalM": $OPTION_RELAYRECONNECTINTERVALM,
  "startBrowser": $OPTION_STARTBROWSER,
  "natEnabled": $OPTION_NATENABLED,
  "natLeaseMinutes": $OPTION_NATLEASEMINUTES,
  "natRenewalMinutes": $OPTION_NATRENEWALMINUTES,
  "natTimeoutSeconds": $OPTION_NATTIMEOUTSECONDS,
  "urAccepted": $OPTION_URACCEPTED,
  "autoUpgradeIntervalH": $OPTION_AUTOUPGRADEINTERVALH,
  "progressUpdateIntervalS": $OPTION_PROGRESSUPDATEINTERVALS,
  "alwaysLocalNets": ["$OPTION_ALWAYSLOCALNETS"],
  "overwriteRemoteDeviceNamesOnConnect": $OPTION_OVERWRITEREMOTEDEVICENAMESONCONNECT,
  "crashReportingEnabled": $OPTION_CRASHREPORTINGENABLED,
  "databaseTuning": "$OPTION_DATABASETUNING",
  "announceLANAddresses": $OPTION_ANNOUNCELANADDRESSES,
  "connectionLimitEnough": $OPTION_CONNECTIONLIMITENOUGH,
  "connectionLimitMax": $OPTION_CONNECTIONLIMITMAX
}
EOF
)

sleep 10
echo "========= SYNCTHING INIT DEFAULT FOLDER ========="
for FOLDER_ID in `echo $LIST_FOLDER | tr ',' ' '`
do
    export RESPONSE_CODE=$(curl -L -s -o /dev/null -w "%{http_code}\n" -XGET "http://127.0.0.1:8384/rest/config/folders/$FOLDER_ID" \
      -H "Content-Type: application" \
      -H "X-API-KEY: $STGUIAPIKEY" )
    if [ $RESPONSE_CODE = "200" ];then
      echo "$LOG_PREFIX" `printdate` "INFO: Folder with ID \"$FOLDER_ID\" is already existed. Ignoring"
      continue
    elif [ $RESPONSE_CODE != "404" ];then
      echo "$LOG_PREFIX" `printdate` "WARNING: Something wrong with HTTP response code: $RESPONSE. Please check it"
      exit 1
    elif [ $RESPONSE_CODE = "404" ];then
      echo "$LOG_PREFIX" `printdate` "INFO: Folder with ID \"$FOLDER_ID\" is not existed."
      echo "$LOG_PREFIX" `printdate` "INFO: Preparing to create Folder with ID \"$FOLDER_ID\"."
      export RESPONSE_CODE=$(curl -L -s -o /dev/null -w "%{http_code}\n" -XPUT "http://127.0.0.1:8384/rest/config/folders/$FOLDER_ID" \
        --header "Content-Type: application/json" \
        --header "X-API-Key: $STGUIAPIKEY" \
        -d '
        {
          "id": "'"$FOLDER_ID"'",
          "label": "'"$FOLDER_ID"'",
          "path": "'"~/$FOLDER_ID"'"
        }' 
      )
    fi
done

sleep 30
source /bin/auto_discovery_node.sh $AUTO_DISCOVERY_NODE_INTERVAL & sleep 10; source /bin/auto_share_folder.sh $AUTO_SHARE_FOLDER_INTERVAL && fg

wait
