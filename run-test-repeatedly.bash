!/bin/bash
d=`dirname $0`
basedir=`cd ${d}; pwd`
for ((i=1; i<=$3; i++)); do
        if [ `ps aux | grep iperf3 | grep -v grep | wc -l` -gt 0 ]; then
                sudo killall -9 iperf3
        fi
        echo "===== Iteration: $i ====="
        sudo `which python` ${basedir}/tests/${1}/${2}.py
        if [ $i -ne $3 ]; then
                sleep 30
        fi
done

