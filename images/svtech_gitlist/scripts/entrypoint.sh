#!/bin/bash

TZ="${TZ:-Asia/Ho_Chi_Minh}"

rm -rf /etc/localtime
ln -s /usr/share/zoneinfo/$TZ /etc/localtime
echo $TZ > /etc/timezone
check_exists=`ls -la /opt/gitlist/backup_config | grep "\.git" | wc -l`

if [ $check_exists == 0 ]; then
  cd /opt/gitlist/backup_config
  git init /opt/gitlist/backup_config
  git config --global user.name "NMS"
  git config --global user.email 'NMS@localhost'
  echo 'Repository for backup Juniper devices' > /opt/gitlist/backup_config/README
  echo 'Repository for backup Juniper devices' > /opt/gitlist/backup_config/.git/description
  git add /opt/gitlist/backup_config/README
  git commit -m initial
fi

service ssh start
exec apache2-foreground