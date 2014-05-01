#!/bin/bash
d=`dirname $0`
BASE_DIR=`cd ${d}; pwd`
BUILD_DIR="${BASE_DIR}/dependencies"

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
	exit 1;
fi

echo -e "\n\nInstalling useful networking features and utilities\n"
sudo apt-get update || { echo -e "\n\nCould not update package list for APT ... aborting!\n"; exit 1; }
sudo apt-get install -y vlan bridge-utils nmap python-pexpect r-base || { echo -e "\n\nCould not install selected network feature and utility packages ... aborting!\n"; exit 1; }
sudo modprobe 8021q || { echo -e "\n\nCould not enable 8021q kernel module for vlans ... aborting!\n"; exit 1; }

echo -e "\n\nInfrastructure for running experiments tests has been successfully installed.  You can run the following experiment test sets:
	basicIPv6
	basicIPv6Multicast
	complexIPv6

These can either be run once directly using python:

	sudo python ${BASE_DIR}/<testset_name>Tests.py

Or multiple times using the runTestsRepeated.bash script:

	sudo ${BASE_DIR}/runTestsRepeated.bash <testset_name>Tests.py <iterations>
	
	E.g. ${BASE_DIR}/runTestsRepeated.bash basicIPv6Tests.py 10\n"

