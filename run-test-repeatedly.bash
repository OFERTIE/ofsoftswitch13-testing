#!/bin/bash

kill_switch_processes(){
        if [ `ps aux | grep "ofdatapath\|ofprotocol" | grep -v grep | wc -l` -gt 0 ]; then
		echo "Killing switch processes that should no longer be running."
                sudo killall -9 ofdatapath ofprotocol
                if [ -z "$1" -a $1 -gt 0 ]; then
			echo "Sleeping $1 seconds to make sure switch processes are dead."
                        sleep $1
                fi
        fi
}

kill_nox_core(){
	pkilled=0
	for process in `ps aux | grep "nox_core" | grep -v "grep" | awk 'BEGIN{FS="[\t ]+"}{ print $2 }'`; do
		echo "Killing controller process ${process}"
		sudo kill -9 ${process}
		pkilled=`expr ${pkilled} + 1`
	done
	if [ ${pkilled} -gt 0 -a -z "$1" -a $1 -gt 0 ]; then
		echo "Sleeping $1 seconds to make sure controller processes are dead."
		sleep $1
	fi
}

kill_process_if_exists(){
	if [ `ps aux | awk 'BEGIN{FS="[\t ]+"}{ print $2 }' | grep "^${1}$" | wc -l` -gt 0 ]; then
		echo "Killing controller process ${process}"
                sudo kill -9 ${1}
        fi
}

d=`dirname $0`
basedir=`cd ${d}; pwd`
tempdir="/tmp/ofsoftswitch13-testing"
processlist=`ps aux | grep "run-test-repeatedly.bash" | grep -v "grep"`
if [ `echo "${processlist}" | wc -l` -gt 2 ]; then
	echo "run-test-repeatedly.bash is already running.  Please kill this process before running the script."
	exit 1
fi
sudo touch ${tempdir}/nox_core.log ${tempdir}/nox_core.err
sudo chown $USER:$USER ${tempdir}/nox_core.*

for ((i=1; i<=$3; i++)); do
	kill_nox_core 5
	kill_switch_processes 5
        if [ `ps aux | grep iperf3 | grep -v grep | wc -l` -gt 0 ]; then
		echo "Killing iperf3 processes that should no longer be running"
                sudo killall -9 iperf3
        fi
	cd  ${basedir}/dependencies/nox13oflib/build/src/
        sudo ./nox_core -v -i ptcp:6633 switch 1>> ${tempdir}/nox_core.log 2>> ${tempdir}/nox_core.err &
	sleep 10
        echo "===== Iteration: $i ====="
        sudo `which python` ${basedir}/tests/${1}/${2}.py
	kill_nox_core
	kill_switch_processes
        if [ $i -ne $3 ]; then	
                sleep 5
        fi
done
