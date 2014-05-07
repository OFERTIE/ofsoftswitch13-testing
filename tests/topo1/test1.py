#!/usr/bin/python
import sys
import os
rootdir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.sys.path.insert(0, rootdir)
import unittest
import pexpect
import re
import json
import random
import uuid
from oftestutils import Oftutils
from time import sleep
from mininet.util import quietRun

class Topo1Test1( unittest.TestCase ):

    output_type = "machine"
    output_destination = "file"
    topology = "topo1"
    basepath = str(os.path.normpath(rootdir))

    def test1( self ):
        print >> sys.stderr, "Test 1: Testing flow modifications using eth_type=0x86dd"
        network = Oftutils.setupNetwork( self.topology, self.basepath )
        iperf_pid = Oftutils.doIperf3Server( network, 'h2' )

        test_file = os.path.normpath(os.path.join( self.basepath, 'config', 'iperf', self.topology, 'test1.json' ))
        json_data = open(test_file)
        tests = json.load(json_data)
        random.shuffle(tests)

        ofcommands_file = os.path.normpath(os.path.join( self.basepath, 'config', 'dpctl', self.topology, 'test1.json' ))
        json_data = open(ofcommands_file)
        ofcommands_list = json.load(json_data)

        results_folder = os.path.normpath(os.path.join( self.basepath, 'results', self.topology, "test1" ))

        Oftutils.runTestSets( network, tests, ofcommands_list, self, results_folder )

        Oftutils.killProcess( network, 'h2', iperf_pid )
        Oftutils.finished( network )

if __name__ == '__main__':
    unittest.main()

