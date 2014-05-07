import unittest
import pexpect
import os
import re
import sys
import uuid
import json
from time import sleep
from mininet.util import quietRun

class Oftutils():

    prompt = 'mininet>'
    startup_sleep = 10
    rule_change_sleep = 5

    @staticmethod
    def setupNetwork( topo, basepath ):
        network = Oftutils.createShell( topo, basepath )
        Oftutils.configureNetwork( network, topo, basepath )
        return network

    @staticmethod
    def createShell( topo, basepath ):
        print >> sys.stderr, "Creating Mininet shell for "+topo
        topofile = os.path.normpath(os.path.join( basepath, 'oftest-topos.py' ))
        p = pexpect.spawn( 'mn --custom %s --topo %s --mac --switch user --controller remote' % ( topofile, topo ) )
        p.expect( Oftutils.prompt )
        print >> sys.stderr, "Sleeping for " + str(Oftutils.startup_sleep) + " seconds to allow the OpenFlow controller to learn the network"
        sleep(Oftutils.startup_sleep)
        return p

    @staticmethod
    def expectline( p, command ):
        p.sendline( command )
        p.expect( [pexpect.TIMEOUT, Oftutils.prompt], timeout=60 )
	return p.before.split( '\n' )

    @staticmethod
    def configureNetwork( p, topo, basepath ):
        print >> sys.stderr, "Setting up "+topo+" network topology"
	json_data = open(os.path.normpath(os.path.join( basepath, 'config', 'ifconfig', topo + ".json" )))
        commands = json.load(json_data)
	for cmd in commands:
	    command =  cmd['host'] + " ifconfig " + cmd['interface'] + " " + cmd['action'] + " " + cmd['address_netmask'] + " up"
	    Oftutils.expectline( p, command)
	init_file = os.path.normpath(os.path.join( basepath, 'dpctl', topo, 'init.json' ))
	if os.path.isfile(init_file):
	    json_data = open( init_file )
            ofcommands = json.load(json_data)
            for ofcommand in ofcommands:
                Oftutils.applyDpctl(p, ofcommand['switch'], ofcommand['command_type'], 'add', ofcommand['arguments'])

    @staticmethod
    def getMultipleIfconfigs( p, switch, interfaces ):
        results = ""
        for interface in interfaces:
            Oftutils.expectline( p, switch + ' ifconfig ' + interface )
	    regex = re.compile( r"(^.*(inet|Ethernet).*$)", re.MULTILINE )
            ifconflines = regex.findall ( p.before )
            for line in ifconflines:
                results += line[0].strip() + "\n"
            results += "\n"
	return results

    @staticmethod
    def getMultipleIfconfigIOs( p, switch, interfaces ):
        results = ""
        for interface in interfaces:
            Oftutils.expectline( p, switch + ' ifconfig ' + interface )
            regex = re.compile('RX bytes.*')
            bytes_in_out = regex.findall( p.before )
            results += interface + ": " + bytes_in_out[ 0 ] + "\n"
        results += "\n"
	return results

    @staticmethod
    def doPing( p, source, dest, args='', count=10 ):
      return Oftutils.doPingGeneric( p, 'ping', source, dest, count, args )

    @staticmethod
    def doPing6( p, source, dest, args='', count=10 ):
      return Oftutils.doPingGeneric( p, 'ping6', source, dest, count, args )

    @staticmethod
    def doPingGeneric( p, ping_type, source, dest, count, args='' ):
        command = source + " " + ping_type + " -c " + str(count) + " " + args + " " + dest
        lines = Oftutils.expectline( p, command )
        results = Ping()
        if len(lines) < 4:
          return results
	regex_int = re.compile('[0-9]+');
	pkts = regex_int.findall(lines[-3])
        results = Ping();
        results.pkts_tran = int(pkts[0])
        results.pkts_recv = int(pkts[1])
        if len(pkts) == 4:
          results.pkts_err = int(pkts[2])
          results.pkts_loss_pct = int(pkts[3])
        else:
          results.pkts_loss_pct = int(pkts[2])
        regex_float = re.compile('[0-9]+\.?[0-9]*');          
        rtt = regex_float.findall(lines[-2])
	if len(rtt) == 4:
          results.rtt_min = float(rtt[0])
          results.rtt_max = float(rtt[1])
          results.rtt_avg = float(rtt[2])
          results.rtt_dev = float(rtt[3])
        return results

    @staticmethod 
    def applyDpctl( p, switch, command_type, action, args ):
      command = switch + " dpctl unix:/tmp/" + switch + " " + command_type + " cmd=" + action + "," + args
      print >> sys.stderr, "COMMAND: " + command 
      p.sendline( command )
      p.expect( Oftutils.prompt )
#      print >> sys.stderr, p.before

    @staticmethod
    def doDpctl( p, switch, ofcommand, args ):
      command = switch + " dpctl unix:/tmp/" + switch + " " + ofcommand + " " + args
      command = command.strip()
      print >> sys.stderr, "COMMAND: " + command
    # lines = Oftutils.expectline( p, command )
      p.sendline( command )
      p.expect( Oftutils.prompt )
    #  print >> sys.stderr, p.before
    
    @staticmethod
    def getNewTempFile( directory ):
      filename = os.path.normpath(os.path.join(directory, uuid.uuid4().hex))
      while os.path.isfile(filename):
        filename = os.path.normpath(os.path.join(directory, uuid.uuid4().hex))
      return filename
    
    @staticmethod 
    def doIperf3( p, host, connect_to, args="", time=10, port=5001 ):
      directory = os.path.join( os.path.sep, "tmp", "ofsoftswitch13-testing",  "iperf" )
      if not os.path.exists(directory):
        os.makedirs(directory)
	os.chown(directory,1001,1001)
      filename = Oftutils.getNewTempFile( directory )
      command = host + " iperf3 -i 0 -J -c " + connect_to + " -p " + str(port) + " -t " + str(time) + " " + args + " | tail -n +2 | sed '/^\[/d' > " + filename
      lines = Oftutils.expectline( p, command )
      return filename

    @staticmethod
    def doIperf3Debug( p, host, connect_to, args="", port=5001 ):
      command = host + " iperf3 -i 0 -t 10 -J -c " + connect_to + " -p " + str(port) + " " + args
      command = command.strip()
      lines = Oftutils.expectline( p, command )
      for line in lines:
        print line
      
    @staticmethod
    def doIperf3Server( p, host,args="", port=5001 ):
      print >> sys.stderr, "Starting iperf3 server on ROIA provider"
      command = host + " iperf3 -sD -p " + str(port) + " " + args
      command = command.strip()
      lines = Oftutils.expectline( p, command )
      return Oftutils.getPid( p, host, "iperf3 -sD -p " + str(port) )

    @staticmethod
    def killProcess( p, host, pid ):
      command = host + " kill -9 " + pid
      Oftutils.expectline( p, command )

    @staticmethod
    def getIperf3Results( filename, udp = 0, result_types = ["bandwidth", "throughput", "cpu_usage"] ):
      with open(filename, 'r') as filehandle:
        try:
          jsondata = json.load(filehandle)
        except:
          message = "error - No valid JSON results file generated for this test at " + filename
          return {'error': message}
      if 'error' in jsondata:
        return jsondata
      results = {'error': ''}
      if 'bandwidth' in result_types:
        results['bandwidth'] = 0
        if len(jsondata['end']['streams']) < 2:
          if udp == 1:
            results['bandwidth'] = jsondata['end']['streams'][0]['udp']['bits_per_second'] / 1000000
          else:
            results['bandwidth'] = jsondata['end']['streams'][0]['receiver']['bits_per_second'] / 1000000
        else:
          if udp == 1: 
            results['bandwidth'] = jsondata['end']['sum']['bits_per_second'] / 1000000
          else:
            results['bandwidth'] = jsondata['end']['sum_received']['bits_per_second'] / 1000000
      if 'throughput' in result_types:
        results['throughput'] = {}
        if len(jsondata['end']['streams']) < 2:
          if udp == 1:
            results['throughput']['megabytes'] = jsondata['end']['streams'][0]['udp']['bytes'] / 1000000
            results['throughput']['packets'] = jsondata['end']['streams'][0]['udp']['packets']
            results['throughput']['lost_packets'] = jsondata['end']['streams'][0]['udp']['lost_packets']
            results['throughput']['lost_percent'] = jsondata['end']['streams'][0]['udp']['lost_percent']
            results['throughput']['jitter'] = jsondata['end']['streams'][0]['udp']['jitter_ms']
          else:
            sent_bytes = jsondata['end']['streams'][0]['sender']['bytes']
            results['throughput']['megabytes'] = jsondata['end']['streams'][0]['sender']['bytes'] / 1000000
            received_bytes = jsondata['end']['streams'][0]['receiver']['bytes']
            if 'retransmits' in jsondata['end']['streams'][0]['sender']:
              results['throughput']['retransmits'] = jsondata['end']['streams'][0]['sender']['retransmits'] 
        else:
          if udp == 1:
            results['throughput']['megabytes'] = jsondata['end']['sum']['bytes'] / 1000000
            results['throughput']['packets'] = jsondata['end']['sum']['packets']
            results['throughput']['lost_packets'] = jsondata['end']['sum']['lost_packets']
            results['throughput']['lost_percent'] = jsondata['end']['sum']['lost_percent']
            results['throughput']['jitter'] = jsondata['end']['sum']['jitter_ms']
          else:
            sent_bytes = jsondata['end']['sum_sent']['bytes']
            results['throughput']['megabytes'] = jsondata['end']['sum_sent']['bytes'] / 1000000
            received_bytes = jsondata['end']['sum_received']['bytes'] / 1000000	
            if 'retransmits' in jsondata['end']['sum_sent']:
              results['throughput']['retransmits'] = jsondata['end']['sum_sent']['retransmits']
        if udp == 0:
          results['throughput']['lost_megabytes'] = ( sent_bytes - received_bytes ) / 1000000
          results['throughput']['lost_percent'] = ( sent_bytes - received_bytes ) / sent_bytes * 100
      if 'cpu_usage' in result_types:
        results['cpu_usage'] = jsondata['end']['cpu_utilization_percent']
      return results

    @staticmethod
    def printResults(output_type, output_destination, test, udp, results):
      if 'bandwidth' not in results:
        results['bandwidth'] = 0
        results['throughput'] = {}
        results['throughput']['lost_percent'] = 0;
        if udp == 1:
          results['throughput']['jitter'] = 0
	else:
          results['throughput']['retransmits'] = 0
	results['cpu_usage'] = {}
	results['cpu_usage']['host_total'] = 0
        results['cpu_usage']['remote_total'] = 0 
      if output_type == "human":
         Oftutils.printResultsHumanReadable(test, results, output_destination)
      else:
         Oftutils.printResultsMachineReadable(test, results, output_destination)

    @staticmethod
    def printResultsHumanReadable(test, results, output_destination):
      print >> output_destination, "Tested: " + test
      print >> output_destination, "  Data rate: " + str(results['bandwidth']) + "Mb/s"
      print >> output_destination, "  Data lost: " + str(results['throughput']['lost_percent']) + "%"
      if 'retransmits' in results['throughput']:
          print >> output_destination, "  Data restransmits: " + str(results['throughput']['retransmits'])
      else:
          print >> output_destination, "  Data jitter: " + str(results['throughput']['jitter']) + "ms" 
      print >> output_destination, "  Host total CPU usage: " + str(results['cpu_usage']['host_total']) + "%"
      print >> output_destination, "  Remote total CPU usage: " + str(results['cpu_usage']['remote_total']) + "%"

    @staticmethod
    def printResultsMachineReadable(test, results, output_destination):
      if 'retransmits' in results['throughput']:
        print >> output_destination, '"' + test + '",' + str(results['bandwidth']) + ',' + str(results['throughput']['lost_percent']) + ',' + str(results['throughput']['retransmits']) + ',' + str(results['cpu_usage']['host_total']) + ',' + str(results['cpu_usage']['remote_total'])
      else:
        print >> output_destination, '"' + test + '",' + str(results['bandwidth']) + ',' + str(results['throughput']['lost_percent']) + ',' + str(results['throughput']['jitter']) + ',' + str(results['cpu_usage']['host_total']) + ',' + str(results['cpu_usage']['remote_total'])

    @staticmethod
    def runTestSet(p, tests, tester, output_destination, set_name="Baseline"):
      if tester.output_type == "human":
        print >> output_destination, set_name
      else:
        print >> output_destination, "\"" + set_name + "\""
      for test in tests:
        print >> sys.stderr, "Testing: "+ test['name']
	arguments = test['arguments'].split(' ')
	if '-u' in test['arguments'].split(' '):
          test['udp'] = 1
        else:
          test['udp'] = 0
        filename = Oftutils.doIperf3(p, test['host'], test['destination'], test['arguments'])
	results = Oftutils.getIperf3Results(filename, test['udp'])
	if results['error'] != "":
		print >> sys.stderr, "WARNING: No iperf data generated.  This may be intentional for this particular test or it may be an error."
	
	Oftutils.printResults(tester.output_type, output_destination, test['name'], test['udp'], results) 

    @staticmethod
    def runTestSets(p, tests, ofcommands_list, tester, results_directory = "/tmp/"):
      if tester.output_destination != "sys.stdout":
        if not os.path.exists(results_directory):
          os.makedirs(results_directory)        
        output_destination = open(results_directory + "/" + uuid.uuid4().hex + ".csv" , 'w')
      else:
        output_destination = tester.output_destination
      Oftutils.runTestSet( p, tests, tester, output_destination )
      last_ofcommands = {}
      for ofcommands in ofcommands_list:
        if len(last_ofcommands) > 0 and len(last_ofcommands['commands']) > 0:
          print >> sys.stderr, "Removing OpenFlow commands for: " + last_ofcommands['name']
          for ofcommand in last_ofcommands['commands']:
            Oftutils.applyDpctl(p, ofcommand['switch'], ofcommand['command_type'], 'del', ofcommand['arguments'])
        print >> sys.stderr, "Applying OpenFlow commands for: " + ofcommands['name']
        for ofcommand in ofcommands['commands']:
          Oftutils.applyDpctl(p, ofcommand['switch'], ofcommand['command_type'], 'add', ofcommand['arguments'])
        sleep(Oftutils.rule_change_sleep)
        print >> sys.stderr, "Sleeping for " + str(Oftutils.rule_change_sleep) + " seconds to ensure OpenFlow commands have been applied."
        Oftutils.runTestSet( p, tests, tester, output_destination, ofcommands['name'] )
        last_ofcommands = ofcommands
  
 
    @staticmethod
    def getPid( p, host, cmdline ):
      command = host + " ps aux | grep \"" + cmdline + "\" | grep -v grep | tail -n 1 | awk 'BEGIN{FS=\"[\t ]+\"}{print $2}'" 
      lines = Oftutils.expectline( p, command )
      return lines[-2]

    @staticmethod 
    def finished( p ):
       print >> sys.stderr, "Finished with Mininet shell"
       p.sendline( 'exit' )
       p.wait()


class Ping():

  def __init__(self):
    self.pkts_tran = 0
    self.pkts_recv = 0
    self.pkts_err = 0
    self.pkts_loss_pct = 0
    self.rtt_min = 0.0
    self.rtt_max = 0.0
    self.rtt_avg = 0.0
    self.rtt_dev = 0.0

  def _setPktsTran(self, pkts_tran=None):
        self._pkts_tran = pkts_tran

  def _getPktsTran(self):
        return self._pkts_tran

  def _setPktsRecv(self, pkts_recv=None):
        self._pkts_recv = pkts_recv

  def _getPktsRecv(self):
        return self._pkts_recv

  def _setPktsErr(self, pkts_err=None):
        self._pkts_err = pkts_err

  def _getPktsErr(self):
        return self._pkts_err

  def _setPktsLossPct(self, pkts_loss_pct=None):
        self._pkts_loss_pct = pkts_loss_pct

  def _getPktsLossPct(self):
        return self._pkts_loss_pct

  def _setRttMin(self, rtt_min=None):
        self._rtt_min = rtt_min

  def _getRttMin(self):
        return self._rtt_min

  def _setRttMax(self, rtt_ax=None):
        self._rtt_max = rtt_max

  def _getRttMax(self):
        return self._rtt_max

  def _setRttAvg(self, rtt_avg=None):
        self._rtt_avg = rtt_avg

  def _getRttAvg(self):
        return self._rtt_avg

  def _setRttDev(self, rtt_dev=None):
        self._rtt_dev = rtt_dev

  def _getRttDev(self):
        return self._rtt_dev

  pkts_tran = property(_getPktsTran, _setPktsTran)
  pkts_recv = property(_getPktsRecv, _setPktsRecv)
  pkts_err = property(_getPktsErr, _setPktsErr)
  pkts_loss_pct = property(_getPktsLossPct, _setPktsLossPct)
  rtt_min = property(_getRttMin, _setRttMin)
  rtt_max = property(_getRttMax, _setRttMax)
  rtt_avg = property(_getRttAvg, _setRttAvg)
  rtt_dev = property(_getRttDev, _setRttDev)

