Test Environment for OpenFlow 1.3
=================================

This codebase provide a test environment for OpenFlow 1.3 specifically for the CPqD's ofsoftswitch13 and the modified NOX controller they built to work with this OpenFlow 1.3 software switch.  There are a number of tutorials provided in the tutorials directory, describing how to make use of test environment and do some OpenFlow experimentation:

### [Tutorial 1: Gettting Started](../../tutorials/01_getting_started.md)
This tutorial provides details on how to install the test environment and get an OpenFlow 1.3 test network up and running.  It then explains how to make use of the network uttilities and how to construct OpenFlow flow and meter commands on an OpenFlow switch.

### [Tutorial 2: Basic IPv6 Experiments](../../tutorials/02_basic_ipv6_experiments.md)
This tutorial does some basic investigation of IPv6 on OpenFlow, using flow and meter commands to test various different types of IPv6 traffic that can be identified by switches that support OpenFlow versiob 1.3.
																				
### [Tutorial 3: Basic Multicast Experiments](../../tutorials/03_basic_multicast_experiments.md)
This tutorial does sone basic investigation of multicast on OpenFlow.  It investigates the comparative performance of using both IPv4 and IPv6 multicast to their unicast equivalents, when the same data needs to be distributed to a number of hosts.

### [Tutorial 4: Automating Experimentation and Visualizing Results](../../tutorials/04_automated_experimentation_and_visualizing_results.md)
This tutorial demonstrates how the test environment provided within this codebase can be used to programatically define an experiment.  This allows experiments to be run multiple times in a consistent manner.  It also makes it easier to copy experiments between systems, allowing results from experiments to be reproduced, as well as allowing modification so different hypotheses can be investigated.  This tutorial also explains how results collected by the test environment can be collated and visualized using box plot graphs.
