#!/bin/bash
d=`dirname $0`
BASE_DIR=`cd ${d}; pwd`
BUILD_DIR="${BASE_DIR}/dependencies"

echo "----------------------------------------------------------"
echo "OpenFlow 1.3 Software Switch Testing Environment Installer"
echo "----------------------------------------------------------"

sudo apt-get update || { echo -e "\n\nCould not update package list for APT.\n"; exit 1; }
cd ${BUILD_DIR}
echo -e "\n\nDownloading dependencies\n"
if [ ! -d mininet ]; then
	echo "Git cloning Mininet"
	git clone git://github.com/mininet/mininet || { echo -e "\n\nCould not clone Git respository for Mininet ... aborting!\n"; exit 1; }
fi
if [ ! -d iperf ]; then
	echo "Git cloning Iperf"
	git clone https://github.com/esnet/iperf.git || { echo -e "\n\nCould not clone Git respository for iperf3 ... aborting!\n"; exit 1; }
fi

echo -e "\n\nInstalling Mininet with OpenFlow Software Switch and Modified NOX Controller\n"
sudo mininet/util/install.sh -3fxn || { echo -e "\n\nCould not install Mininet core files and dependencies ... aborting!\n"; exit 1; }

architecture=`arch`
if [ -f ${BUILD_DIR}/${architecture}/iperf3 ]; then
	echo -e "\n\nInstalling Iperf3 binary (compiled for ${architecture} architectures)\n"
	sudo cp ${BUILD_DIR}/${architecture}/iperf3 /usr/local/bin/
else
	echo -e "\n\nERROR: Iperf3 needs to be built from source for your architecture (${architecture}).  Follow the instructions in ${BUILD_DIR}/iperf/INSTALL\n"
fi

echo -e "\n\nInstalling useful networking features and utilities\n"
sudo apt-get update || { echo -e "\n\nCould not update package list for APT ... aborting!\n"; exit 1; }
sudo apt-get install -y vlan bridge-utils nmap python-pexpect r-base || { echo -e "\n\nCould not install selected network feature and utility packages ... aborting!\n"; exit 1; }
sudo modprobe 8021q || { echo -e "\n\nCould not enable 8021q kernel module for vlans ... aborting!\n"; exit 1; }

architecture=`arch`
if [ -f ${BUILD_DIR}/${architecture}/iperf3 ]; then
        echo -e "\n\nInstalling Iperf3 binary (compiled for ${architecture} architectures)\n"
        sudo cp ${BUILD_DIR}/${architecture}/iperf3 /usr/local/bin/
else
        echo -e "\n\nERROR: Iperf3 needs to be built from source for your architecture (${architecture}).  Follow the instructions in ${BUILD_DIR}/iperf/INSTALL\n"
	exit 1
fi

cd ${BASE_DIR}
echo "------------------------------------------------------"
echo "OpenFlow 1.3 Software Switch Testing Environment Usage"
echo "------------------------------------------------------"

echo -e "\n\nOpenFlow 1.3 software switch testing environment been successfully installed.  You can run tests against the following topologies:
`ls tests/`

These can either be run once directly using python:

	sudo python ${BASE_DIR}/tests/TOPOLOGY/TEST.py

	E.g.  python ${BASE_DIR}/tests/topo1/test1.py

Or multiple times using the run-tests-repeatedly.bash script:

	sudo ${BASE_DIR}/run-test-repeatedly.bash TOPOLOGY TEST ITERATIONS
	
	E.g. ${BASE_DIR}/run-test-repeatedly.bash topo1 test1 10

Results from these tests can be found in CSV format in ${BASE_DIR}/results/TOPOLOGY/TEST/ in the form:

	Traffic Type,Bandwidth (MBits/s),Packet Loss (%),Jitter / Packet Retransmits,Local CPU Load,Remote CPU Load

Once you have produced results for a particular topology and test you can process these results to produces box plots of network statistics:

	${BASE_DIR}/process-results.py TOPOLOGY TEST
	
	E.g. ${BASE_DIR}/process-results.py topo1 test1

Box plots produced by this script can be found in ${BASE_DIR}/graphs/TOPOLOGY/TEST/png/
