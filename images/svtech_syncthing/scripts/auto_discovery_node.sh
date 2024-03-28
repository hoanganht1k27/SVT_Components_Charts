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
export LOG_PREFIX=$(echo [$HOSTNAME/"SVTECH-DISCOVERY-NODE]" | tr '[:lower:]' '[:upper:]')

if [ -z "$1" ]; then
  echo "$LOG_PREFIX" `printdate` "ERROR: Discover remote syncthing server is not running, please input number of second when execute the script. Example: sh <script>.sh 30"
  exit 1
elif [ ! $1 -gt 10 ]; then
  echo "$LOG_PREFIX" `printdate` "ERROR: Discover remote syncthing server is not running, The recommend number of second is the number that greater than 10 (second). Example: sh <script>.sh 30"
  exit 1
fi

echo "$LOG_PREFIX" `printdate` "INFO: Discover remote syncthing server in cluster is running (interval: $1 seconds)..."

while true; do
export SERVER=$(dig srv +search +short $HEADLESS_SERVICE_NAME |awk '{print $4}' | uniq | sed 's/.$//g')
export MY_ID=$(curl -s -L -XGET "http://127.0.0.1:8384/rest/system/status" \
  -H "Content-Type: application" \
  -H "X-API-KEY: $STGUIAPIKEY" \
  |grep myID |awk '{print $2}' |sed 's/,//g' |sed 's/"//g')

for i in $SERVER
do
  export DEVICE_ID=$(curl -s -L -XGET "http://$i:8384/rest/system/status" \
    -H "Content-Type: application" \
    -H "X-API-KEY: $STGUIAPIKEY" \
    |grep myID |awk '{print $2}' |sed 's/,//g' |sed 's/"//g')

  export CURRENT_DEVICE_ID=$(curl -s -L -XGET "http://127.0.0.1:8384/rest/stats/device" \
    -H "Content-Type: application" \
    -H "X-API-KEY: $STGUIAPIKEY")

  #echo "$LOG_PREFIX" `printdate` "INFO: Checking '$i': "
  if [ $MY_ID = $DEVICE_ID ];then
    #echo "This device is local syncthing server, ignored."
    continue
  elif [[ "$CURRENT_DEVICE_ID" =~ "$DEVICE_ID" ]];then
    #echo "This device is already added to local syncthing server, ignored."
    continue
  else
    echo "$LOG_PREFIX" `printdate` "INFO: Discover new remote syncthing server: $i"
    echo "$LOG_PREFIX" `printdate` "INFO: Preparing to add above device with id \"$DEVICE_ID\": "
    export RESPONSE_CODE=$(curl -s -o /dev/null -w "%{http_code}\n" -XPOST "http://127.0.0.1:8384/rest/config/devices" \
      -H "Content-Type: application/json" \
      -H "X-API-Key: $STGUIAPIKEY" \
      -d '
      {
        "deviceID": "'"$DEVICE_ID"'",
        "addresses": [
           "tcp://'"$i"':22000"
        ],
        "autoAcceptFolders": true
      }'
      )
  fi
done

sleep $1
done
