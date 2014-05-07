Test Environment for OpenFlow 1.3
=================================

Installation
------------
To install this test environment you will need a Ubuntu 64-bit (x86\_64) installed machine running 12.04.  It is possible to install on non-64-bit system but you will need to manual build some binaries from source that requires the latest build tools, which Ubuntu 12.04 does not have, so you would have to build the binary on a different machine.

This test environment can be installed using the installer script provided, as follows

> ./install.bash

This will install MiniNet that can be used to run network simulations in a virtualised environment.  It will also install CPqD's of13softswitch, which is one of the most fully-featured virtualised implementations of a OpenFlow version 1.3.  It is accompanied by a modified NOX controller that also supports OpenFlow version 1.3.  If you are installing on a 64-bit architecture, the installer will also install IPerf version 3, built from a recent version of the GitHub repository (https://github.com/esnet/iperf).  If you are not installing a 64-bit architecture, you will have to build from source, which can be found in the dependencies/iperf/ directory after installation.  Finally the installer, will install R, a graphing tool that can use the collated network statistics gathered bya automated testing (see below) and generate box plots for this data, (see Graphing Results below).

## Installation Testing
Once the install is complete you can do a quick test to make sure everything is working correctly.

1. Start the modified NOX OpenFlow 1.3 controller:

> cd dependencies/nox13oflib/build/src/

> sudo ./nox\_core -v -i ptcp:6633 switch

2. Run the Mininet with topo1 as provided by oftest-topos.py:

> sudo mn --topo minimal --mac --switch user --controller remote

3. Once Mininet has loaded, check that ping works between the two hosts:

> h1 ping -c 4 h2


Manual Testing
--------------
As part of this repository there is a python script that define several topologies (oftest-topos.py).  These can be used with MiniNet by slightly modifying the command in step 2 of Test Installation.  Be aware that the OpenFlow controller must aready bee running, (see step 1 of Installation Testing), before you run this command:

>  sudo mn --custom oftest-topos.py --topo topo1 --mac --switch user --controller remote

Once you have a topology running you can add further configuration.  By default, Mininet will use 10.0.0.0/24 address for the default (eth1) interfaces on the hosts creates.  So for topo1 in the command above there are two hosts, h1 will have its h1-eth1 interface set to 10.0.0.1 and h2 will have its h2-eth1 interface set to 10.0.0.2.  If you want to configure IPv6 address this will need to be doing manually using ifconfig.  

MiniNet provides it own command prompt from where commands can be run.  However, it is important to specify the host of switch you want to run the command from the following command send 4 pings from h1 to h2's default interface (i.e. h2-eth1):

> h1 ping -c 4 h2

MiniNet does not have great support for IPv6, therefore IPv6 address cannot be configured into the Python topology script (oftest-topos.py).  ifconfig can be run from the MiniNet command prompt to assign IPv6 addresses as follows:

> h1 ifconfig h1-eth1 add fd10:0:0::1/48 up

> h2 ifconfig h2-eth1 add fd10:0:0::2/48 up

Now that your two hosts have IPv6 address you can test that they can ping6 each other@

> h1 ping6 -c 4 fd10:0:0::2

Now you can ping between the hosts on IPv4 and IPv6, lets try sending some more interesting traffic.  This can be done using IPerf.  IPerf works in a server and client arrangement the server runs as a listener on one host and the client can then send various types of IP traffic to the server on an agreed port number.  Lets start the IPerf (version 3) server on host h2 on port 5001:

> h2 iperf3 -sD -p 5001

the -sD flag specify this is a server instance of IPerf and that it shoyld be run in daemon mode (i.e. in the background) to keep the MiniNet command prompt free.  Next, we need to start the client.  There are many configuration options that can be set to produce different types of traffic you can type "h1 iperf3 -h" to have a look at these options.  However,  we will keep it simple to start with.  The following command will generate 10 seconds of IPv4 TCP traffic and once finished, the bandwidth and other statistics of the transmission of this data will be captured and output to the screen:

> h1 iperf3 -c 10.0.0.2 -p 5001

The output will display the aamount of data transferred each second and then probably a summary at the end something like:

> [ ID] Interval           Transfer     Bandwidth       Retr

> [  4]   0.00-10.02  sec  34.9 MBytes  29.2 Mbits/sec   15             sender

> [  4]   0.00-10.02  sec  34.9 MBytes  29.2 Mbits/sec                  receiver

You can also run a similar test using an iperf client that connects over IPv6:

> h1 iperf3 -c fd10:0:0::2 -p 5001

Instead of sending TCP traffic we could sen UDP traffic.  You need to specify the banddwith for UDP or it will just send at 1Mbit/s.  The software switch can generally cope with 10Mbits/s before it starts to lose packets, so lets try that:

> h1 iperf3 -u -b 10M -c fd10:0:0::2 -p 5001

With UDP traffic iperf will give a slightly different summary to TCP traffic:

> [ ID] Interval           Transfer     Bandwidth       Jitter    Lost/Total Datagrams

> [  4]   0.00-10.00  sec  12.4 MBytes  10.4 Mbits/sec  1.911 ms  0/1585 (0%)  

> [  4] Sent 1585 datagrams

Now that we can show we can send different types of data about lets start playing withe OpenFlow controller.  There are lots of different options you can set on the controllers but fo this topology the most visble is metering.  I.e. restricting the bandwidth on data being sent.  The tool for doing this on the OpenFlow 1.3 NOX controller is called dpctl.  

To apply a meter to some traffic we first need to need to define the meter using dpctl, using the following command:

> s1 dpctl unix:/tmp/s1 meter-mod cmd=add,flags=1,meter=1 drop:rate=5000

This command means for switch 1 (s1) whose configuration is stored in /tmp/s1 make a modification to the meters by adding a new meter with ID 1.  This meter should drop traffic above 5000 Kbits/s (5MBit/s).

Next we need to apply this meter to some traffic.  Lets say for some reason we want to restrict the amount of IPv6 traffic between the two hosts.  We could apply the following dpctl command:

> s1 dpctl unix:/tmp/s1 flow-mod cmd=add,table=0 in\_port=1,eth\_type=0x86dd meter:1 apply:output=2

This command says for switch 1 make a modification to the flows by adding a new flow rule to the default table (i.e. 0) for traffic comming in port 1 (i.e. the port connect to h1) if it is IPv6 defined by having and Ethernet type of 0x86dd rather than 0x800 that is IPv4, aplly the meter with ID 1 and send data from this flow out port 2, which goes to switch 2 (s2) and ultimately, h2.  The reverse of these rule could be created to restrict IPv6 traffic from h2 to h1, However as it is the iperf client h1 that is sending the data this would have no real effect in our scenario.

So now we have the meter in place for IPv6 traffic we can run the IPerf client command on h1 again.  (The IPerf server on h2 shoudl still be running):

> h1 iperf3 -c 10.0.0.2 -p 5001

The results should show much the same bandwidth (approximately 30Mbits/s).  Now lets try with IPv6:

> h1 iperf3 -c fd10:0:0::2 -p 5001

The results for this should show that the bandwidth has been limited to around 5MBit/s.  It is likely it will be slightly over because of the dynamics of how the bandwidth restriction is applied and how this interacts with TCP.

There are numerous other flow modification rules you could add.  Here is a selection below, see if you can figure out what they do:

> s1 dpctl unix:/tmp/s1 flow-mod cmd=add,table=0 in\_port=2,eth\_type=0x86dd,ipv6\_src=fd10:0:0::2/48 meter:1 apply:output=1

> s2 dpctl unix:/tmp/s2 flow-mod cmd=add,table=0 in\_port=1,eth\_type=0x86dd,ipv6\_dst=fd10:0:0::1/48 meter:1 apply:output=2

> s1 dpctl unix:/tmp/s1 flow-mod cmd=add,table=0 in\_port=1,eth\_type=0x800,ip\_proto=6 meter:1 apply:output=2

> s2 dpctl unix:/tmp/s2 flow-mod cmd=add,table=0 in\_port=1,eth\_type=0x86dd,ip\_proto=17 meter:1 apply:output=2

> s1 dpctl unix:/tmp/s1 flow-mod cmd=add,table=0 in\_port=1,eth\_type=0x800,ip\_dscp=8 meter:1 apply:output=2

> s2 dpctl unix:/tmp/s2 flow-mod cmd=add,table=0 in\_port=1,eth\_type=0x86dd,ipv6\_flabel=23 meter:1 apply:output=2


Automated Testing
-----------------
These can be produced in human or machine-readable format (CSV) by specifying this in the python test suite.  See examples/tests.py.  Multiple iterations of machine-readable results can be generated by running the run-tests-repeated.bash script.

> ./run-test-repeatedly.bash TOPOLOGY TEST ITERATIONS

> E.g. ./run-test-repeatedly.bash topo1 test1 10


Graphing Results
----------------
Once you have run multiple iterations of a test you generate box plots (http://en.wikipedia.org/wiki/Box\_plot) to visualise these results.  To run this for a particular test use the following command:

> ./process-results.py TOPOLOGY TEST

> E.g. ./process-results topo1 test1

Running this will produce box plots for the (currently) five different statistics generated by IPerf when the automated testing was run:
- Bandwidth (Mb/s)
- Packet loss (%)
- Jitter (for UDP) | Number of packet retransmits for TCP
- Local (the host sending data) CPU load 
- Remote (the host receiving data) CPU load

The images of these box plots can be found in graphs/TOPOLOGY/TEST\_NAME/png/.  These have been generated by an R script file with equivalent filename in graphs/TOPOLOGY/TEST\_NAME/rscript/ and from CSV generated by the test results that can also be found in an equivalent file in graphs/TOPOLOGY/TEST\_NAME/csv/.  You can modify the rscript if you wish and re run it from the rscript directory with the following command:

> Rscript FILENAME.r


