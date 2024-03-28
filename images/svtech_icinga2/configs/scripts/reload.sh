#!/bin/bash
for i in `ps -e |grep icinga2 | head -n 1 |awk '{print $1}'`; do kill -1 $i; done
