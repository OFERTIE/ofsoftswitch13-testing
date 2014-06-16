Tutorial 1: Getting Started
===========================

Installing Test Environment
---------------------------
To install this test environment you will need a Ubuntu 64-bit (x86\_64) installed machine running 12.04.  It is possible to install on non-64-bit system but you will need to manual build some binaries from source that requires the latest build tools, which Ubuntu 12.04 does not have, so you would have to build the binary on a different machine.

This test environment can be installed using the installer script provided, as follows

> ./install.bash

This will install MiniNet that can be used to run network simulations in a virtualised environment.  It will also install CPqD's of13softswitch, which is one of the most fully-featured virtualised implementations of a OpenFlow version 1.3.  It is accompanied by a modified NOX controller that also supports OpenFlow version 1.3.  If you are installing on a 64-bit architecture, the installer will also install IPerf version 3, built from a recent version of the GitHub repository (https://github.com/esnet/iperf).  If you are not installing a 64-bit architecture, you will have to build Iperf version 3 from source, which can be found in the dependencies/iperf/ directory after installation.  Finally the installer, will install R, a graphing tool that can use the collated network statistics to visualize experimental results.  This will be explained in tutorial 4.


Testing Installation
--------------------
Once the install is complete you can do a quick test to make sure everything is working correctly.

1. Start the modified NOX OpenFlow 1.3 controller:

> cd dependencies/nox13oflib/build/src/

> sudo ./nox\_core -v -i ptcp:6633 switch

2. Run the Mininet with topo1 as provided by oftest-topos.py:

> sudo mn --topo minimal --mac --switch user --controller remote

3. Once Mininet has loaded, check that ping works between the two hosts:

> h1 ping -c 4 h2


Getting Use to OpenFlow Configuration and Network Utilities
-----------------------------------------------------------
As part of this repository there is a python script that define several topologies (oftest-topos.py).  These can be used with MiniNet by slightly modifying the command in step 2 of Test Installation.  Be aware that the OpenFlow controller must aready bee running, (see step 1 of Installation Testing), before you run this command:

>  sudo mn --custom oftest-topos.py --topo topo1 --mac --switch user --controller remote

Once you have a topology running you can add further configuration.  By default, Mininet will use 10.0.0.0/24 address for the default (eth1) interfaces on the hosts creates.  So for topo1 in the command above there are two hosts, h1 will have its h1-eth1 interface set to 10.0.0.1 and h2 will have its h2-eth1 interface set to 10.0.0.2.  If you want to configure IPv6 address this will need to be doing manually using ifconfig.

MiniNet provides it own command prompt from where commands can be run.  However, it is important to specify the host of switch you want to run the command from the following command send 4 pings from h1 to h2's default interface (i.e. h2-eth1):

> h1 ping -c 4 h2

Now you can ping between the hosts on IPv4 and IPv6, lets try sending some more interesting traffic.  This can be done using IPerf.  IPerf works in a server and client arrangement the server runs as a listener on one host and the client can then send various types of IP traffic to the server on an agreed port number.  Lets start the IPerf (version 3) server on host h2 on port 5001:

> h2 iperf3 -sD -p 5001

the -sD flag specify this is a server instance of IPerf and that it shoyld be run in daemon mode (i.e. in the background) to keep the MiniNet command prompt free.  Next, we need to start the client.  There are many configuration options that can be set to produce different types of traffic you can type "h1 iperf3 -h" to have a look at these options.  However,  we will keep it simple to start with.  The following command will generate 10 seconds of IPv4 TCP traffic and once finished, the bandwidth and other statistics of the transmission of this data will be captured and output to the screen:

> h1 iperf3 -c 10.0.0.2 -p 5001

The output will display the aamount of data transferred each second and then probably a summary at the end something like:

> [ ID] Interval           Transfer     Bandwidth       Retr

> [  4]   0.00-10.02  sec  34.9 MBytes  29.2 Mbits/sec   15             sender

> [  4]   0.00-10.02  sec  34.9 MBytes  29.2 Mbits/sec                  receiver

You can also run a similar test using an iperf client but sending UDP data instead:

> h1 iperf3 -c 10.0.0.2 -u -p 5001

With UDP traffic iperf will give a slightly different summary to TCP traffic:

> [ ID] Interval           Transfer     Bandwidth       Jitter    Lost/Total Datagrams

> [  4]   0.00-10.00  sec  12.4 MBytes  10.4 Mbits/sec  1.911 ms  0/1585 (0%)

> [  4] Sent 1585 datagrams

Now that we can show we can send different types of data about lets start playing withe OpenFlow controller.  There are lots of different options you can set on the controllers but fo this topology the most visble is metering.  I.e. restricting the bandwidth on data being sent.  The tool for doing this on the OpenFlow 1.3 NOX controller is called dpctl.

To apply a meter to some traffic we first need to need to define the meter using dpctl, using the following command:

> s1 dpctl unix:/tmp/s1 meter-mod cmd=add,flags=1,meter=1 drop:rate=5000

This command means for switch 1 (s1) whose configuration is stored in /tmp/s1 make a modification to the meters by adding a new meter with ID 1.  This meter should drop traffic above 5000 Kbits/s (5MBit/s).

Next we need to apply this meter to some traffic.  Lets say for some reason we want to restrict the amount of UDP traffic between the two hosts.  We can apply the following dpctl command to do this:

> s1 dpctl unix:/tmp/s1 flow-mod cmd=add,table=0 in\_port=1,ip_proto=6 meter:1 apply:output=2

This command says for switch 1 make a modification to the flows by adding a new flow rule to the default table (i.e. 0) for traffic comming in port 1 (i.e. the port connect to h1) if it is UDP it will be described as having IP protocol 6. applying the meter with ID 1 and send data from this flow out port 2, which goes to switch 2 (s2) and ultimately, h2.  The reverse of these rule could be created to restrict IPv6 traffic from h2 to h1, However as it is the iperf client h1 that is sending the data this would have no real effect in our scenario.

So now we have the meter in place for IPv6 traffic we can run the IPerf client command on h1 again.  (The IPerf server on h2 shoudl still be running):

> h1 iperf3 -c 10.0.0.2 -p 5001

The results should show much the same bandwidth (approximately 30Mbits/s).  Now lets try with UDP:

> h1 iperf3 -c 10.0.0.2 -u -p 5001

The results for this should show that the bandwidth has been limited to around 5MBit/s.  It is unlikely to be exactly 5Mbits/s because OpenFlow will drop packets when it see its meter is exceeded, as these packets can be reasonably large a decision to drop a packet or not will make a lot of difference to the exact bandwidth, expecially over only a 10 second test period.

