#!/usr/bin/env bash

PID=$(netstat -anp|grep 9001|awk '{printf $7}'|cut -d/ -f1)
echo "Killing PID ${PID}"
exec kill ${PID}
echo "Done!"