Tutorial 4: Automating Experimenation and Visualizing Results
=============================================================

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

