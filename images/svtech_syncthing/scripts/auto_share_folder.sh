#!/bin/sh

export RESPONSE_CODE=0
function checkresponse() {
  if [[ $RESPONSE_CODE =~ ^20[0-9] ]]; then
    echo "OK (CODE: $RESPONSE_CODE)"
  else
    echo "FAILED (CODE: $RESPONSE_CODE)"
  fi
}
function printdate(){
  date '+%Y/%m/%d %H:%M:%S'
}
export LOG_PREFIX=$(echo [$HOSTNAME/"SVTECH-SHARE-FOLDER]" | tr '[:lower:]' '[:upper:]')

if [ -z "$1" ]; then
  echo "$LOG_PREFIX" `printdate` "ERROR: Auto share folder is not running, please input number of second when execute the script. Example: sh <script>.sh 30"
  exit 1
elif [ ! $1 -gt 10 ]; then
  echo "$LOG_PREFIX" `printdate` "ERROR: Auto share folder is not running, The recommend number of second is the number that greater than 10 (second). Example: sh <script>.sh 30"
  exit 1
fi

echo "$LOG_PREFIX" `printdate` "INFO: Auto share folder in cluster is running (interval: $1 seconds)..."

while true; do
export NUM_SERVER=$(dig srv +search +short $HEADLESS_SERVICE_NAME |awk '{print $4}' | uniq | sed 's/.$//g' |wc -l)
export MY_FOLDER_ID=$(curl -s -L -XGET 'http://127.0.0.1:8384/rest/config/folders/' \
  -H "Content-Type: application" \
  -H "X-API-KEY: $STGUIAPIKEY" \
  |grep id |awk '{print $2}' |sed 's/,//g' |sed 's/"//g')

for i in $MY_FOLDER_ID
do
  # CHECKING FOLDER's CURRENT NUMBER OF SHARED REMOTE DEVICE ID
  export NUM_SHARED_DEVICE_ID=$(curl -s -L -XGET "http://127.0.0.1:8384/rest/config/folders/$i" \
    -H "Content-Type: application" \
    -H "X-API-KEY: $STGUIAPIKEY" \
    |grep deviceID |awk '{print $2}' |sed 's/,//g' |sed 's/"//g' |wc -l)

  # CHECKING IF SHARED FOLDER IS SHARED TO ALL DEVICES IN CLUSTER
  if [ $NUM_SHARED_DEVICE_ID = $((`echo $NUM_SERVER`)) ];then
    continue
  elif [ $NUM_SHARED_DEVICE_ID -gt $((`echo $NUM_SERVER`)) ];then
    #echo "$LOG_PREFIX" `printdate` "WARNING: Current number of shared devices($NUM_SHARED_DEVICE_ID) is larger than current number of Syncthing servers($NUM_SERVER) ???"
    continue
  else
    echo "$LOG_PREFIX" `printdate` "INFO: Folder ID \"$i\" is not sharing to all remote device Syncthing servers."
    export ALL_DEVICE_ID=$(curl -s -L -XGET "http://localhost:8384/rest/config/devices" \
      -H "Content-Type: application" \
      -H "X-API-KEY: $STGUIAPIKEY" \
      |grep deviceID |awk '{print $2}' |sed 's/,//g' |sed 's/"//g')
    export LIST_ALL_DEVICE_ID=$(for i in $ALL_DEVICE_ID; do echo -n "{ \"deviceID\": \"$i\" }, ";done |sed 's/, $//')
    echo "$LOG_PREFIX" `printdate` "INFO: Preparing to share folder ID \"$i\" to all Syncthing servers: "
    export RESPONSE_CODE=$(curl -s -o /dev/null -w "%{http_code}\n" -XPATCH "http://127.0.0.1:8384/rest/config/folders/$i" \
      -H "Content-Type: application/json" \
      -H "X-API-Key: $STGUIAPIKEY" \
      -d '
      {
        "devices": [
          '"$LIST_ALL_DEVICE_ID"'
        ]
      }'
      )
  fi
done

sleep $1
done
