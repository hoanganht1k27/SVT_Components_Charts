#!/bin/bash
export memory_in_bytes=$(cat /sys/fs/cgroup/memory/memory.limit_in_bytes)
export memory_in_mb=$((memory_in_bytes/1024/1024))
export TERM=xterm
echo -e "==================================================================
=                           WARNING                              =
=           All connections are monitored and recorded           =
==================================================================
=========================: System Data :==========================
 \033[0mDate Time     = \033[1;32m`date`
 \033[0mHostname      = \033[1;32m`hostname`
 \033[0mAddress       = \033[1;32m`echo $(ifconfig |grep inet | grep -v inet6 |awk '{print $2}' | grep -v 127.0.0.1)`
 \033[0mUptime        = \033[1;32m`uptime |awk '{print $1, $2, $3, $4}' |cut -d "," -f 1`
 \033[0mLoad Average  = \033[1;32m`uptime |awk '{print $8, $9, $10, $11}' |cut -d ":" -f 1`
 \033[0mMemory limit  = \033[1;32m$memory_in_mb MB\033[0m
==========================: User Data :===========================
 \033[0mUsername      = \033[1;32m`whoami`
 \033[0mIP Address    = \033[1;32m`echo $SSH_CLIENT | awk '{ print $1}'`\033[0m
=================================================================="
tput sgr0
