#!/bin/bash

kill_switch_processes(){
        if [ `ps aux | grep "ofdatapath\|ofprotocol" | grep -v grep | wc -l` -gt 0 ]; then
		echo "Killing switch processes that should no longer be running."
                sudo killall -9 ofdatapath ofprotocol &>/dev/null
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
		sudo kill -9 ${process} &>/dev/null
		pkilled=`expr ${pkilled} + 1`
	done
	if [ ${pkilled} -gt 0 ]; then 
		if [[ -n "$1" && $1 -gt 0 ]]; then
			echo "Sleeping $1 seconds to make sure controller processes are dead."
			sleep $1
		fi
	fi
}

kill_process_if_exists(){
	if [ `ps aux | awk 'BEGIN{FS="[\t ]+"}{ print $2 }' | grep "^${1}$" | wc -l` -gt 0 ]; then
		echo "Killing controller process ${process}"
                sudo kill -9 ${1} &>/dev/null
        fi
}

d=`dirname $0`
basedir=`cd ${d}; pwd`
if [ "$#" -ne 3 ]; then
        echo "This script requires thre arguments.  E.g.

	$0 topo1 test1 10
";
	exit 1
fi
if [ ! -d "${basedir}/tests/$1" ]; then
	echo -e "No tests directory for topology: $1\n\nAvailable topologies:\n\n`ls ${basedir}/tests/`\n"
	exit 1
fi
if [ ! -f "${basedir}/tests/$1/$2.py" ]; then
        echo -e "No test called $2 in tests directory for topology: $1\n\nAvailable tests:\n\n`ls ${basedir}/tests/$1/`\n"
        exit 1
fi
if [ -f "${basedir}/rtr-settings.bash" ]; then 
	source "${basedir}/rtr-settings.bash"
else
	source "${basedir}/rtr-default-settings.bash"
fi

tempdir="/tmp/`basename ${basedir}`"
if [ ! -d ${tempdir} ]; then
	echo "Creating temporary directory: ${tempdir}"
	sudo mkdir -p ${tempdir}
fi
processlist=`ps aux | grep "run-test-repeatedly.bash" | grep -v "grep" | grep -v "vim* "`
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
                sudo killall -9 iperf3 &>/dev/null
        fi
	cd  ${nox_core_dir}
        sudo ${nox_core_dir}/nox_core -v -i ptcp:6633 switch 1>> ${tempdir}/nox_core.log 2>> ${tempdir}/nox_core.err &
	sleep 10
        echo "===== Iteration: $i ====="
        sudo `which python` ${basedir}/tests/${1}/${2}.py
	kill_nox_core
	kill_switch_processes
        if [ $i -ne $3 ]; then	
                sleep 5
        fi
done
