#!/usr/bin/python
import os
import sys
import csv
import pprint
import string

basepath = str(os.path.normpath(os.path.dirname(os.path.realpath( __file__ ))))
topology = sys.argv[1]
test_num = sys.argv[2]
results_path = os.path.normpath(os.path.join( basepath, 'results', topology, test_num ))
if not os.path.isdir(results_path):
  print >> sys.stderr, "ERROR: There are no results for topology "+topology+" test "+test_num+"."
  exit(1)
results_files = [ os.path.join(results_path, f) for f in os.listdir(results_path) if os.path.isfile(os.path.join(results_path,f)) ]
if len(results_files) == 0:
  print >> sys.stderr, "ERROR: There are no results for topology "+topology+" test "+test_num+"."
  exit(1)
results = {}
field_maps = { 'bandwidth':'Bandwidth (Mb/s)', 'packet_loss':'Packet Loss %', 'jitter_retransmits':'Jitter ms / Packet Retransmits', 'local_cpu_load':'Local CPU Load', 'remote_cpu_load':'Remote CPU Load' }
fields = field_maps.keys()

graph_dirs = [ "csv", "png", "rscript" ]
for graph_dir in graph_dirs:
  graph_dir_full = os.path.join( basepath, "graphs", topology, test_num, graph_dir )
  if not os.path.exists(graph_dir_full):
    os.makedirs(graph_dir_full)

for results_file in results_files:
    with open(results_file, 'rb') as file_handle:
        reader = csv.reader(file_handle)
	rows = []
        for row in reader:
            rows.append(row)
        n = 0
        while n < len(rows):
            if len(rows[n]) == 1:
                subset_name = rows[n][0].replace(" ", "_")
                if subset_name not in results:
                    results[subset_name] = {}
		    for (field, field_name) in field_maps.iteritems():
                        results[subset_name][field] = {}
                n = n + 1
            
            while n < len(rows) and len(rows[n]) > 1:
                subtest_name = rows[n][0].replace(" ", "_")
	        for f in range(0, len(field_maps)): 
                    if subtest_name not in results[subset_name][fields[f]]:
                        results[subset_name][fields[f]][subtest_name] = {'values':[]}
                    results[subset_name][fields[f]][subtest_name]['values'].append(float(rows[n][f+1]))
                n = n + 1

colours = [ 'red', 'blue', 'green', 'yellow', 'purple', 'orange', 'pink', 'brown' ]
for (r, result) in results.items():
    for (f, field) in result.items():
        filename = r + "-" + f
        csv_file_location = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "graphs", topology, test_num, "csv", filename+".csv"))
        rscript_file_location = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "graphs", topology, test_num, "rscript", filename+".r"))
	csv_fh = open(csv_file_location, "w")
        rscript_fh = open(rscript_file_location, "w")
        csv_fh.write('"Traffic Type","' + field_maps[f] + '"\n')
        rscript_fh.write('csv <- read.csv("../csv/'+filename+'.csv",header=T,sep=",")\n')
        rscript_fh.write('data <- t(csv)\n')
	graph_width = 120 + 100 * len(field.items())
        boxplots = ','.join(field.keys())
	subtest_num = 0
	startnum = 1
	boxplots_arr = []
        bp_colours_arr = []
        subtest_ids_arr = []
        subtest_names_arr = []
	max_value = 0
        for (s, subtest) in field.items():
            bp_colours_arr.append(colours[subtest_num%len(colours)])
	    subtest_ids_arr.append(s)
            subtest_names_arr.append(s.replace("_", " "))
	    subtest_num = subtest_num + 1
	    if max(subtest['values']) > max_value:
                max_value = max(subtest['values'])
            for value in subtest['values']:
               csv_fh.write('"' + s + '",' + str(value) + '\n')
            stopnum = startnum - 1 + len(subtest['values'])
            rscript_fh.write(s+' <- as.numeric(data[2,'+str(startnum)+':'+str(stopnum)+'])\n')
            startnum = stopnum + 1
        csv_fh.close()
	bp_colours = '"' + '","'.join(bp_colours_arr) + '"'
	subtest_ids = ','.join(subtest_ids_arr)
	subtest_names = '"' + '","'.join(subtest_names_arr) + '"'
        ylim_max = str(max_value * 1.1)
        print >> sys.stderr, r + ":" + s + ":"+ f + ":" + ylim_max
	rscript_fh.write('png("../png/'+filename+'.png", '+str(graph_width)+', 300)\n')
	rscript_fh.write('boxplot('+subtest_ids+',col=c('+bp_colours+'),names=c('+subtest_names+'),main="Topology: '+topology+', Test: '+test_num+'\n'+r.replace("_", " ")+'",xlab="Traffic Type",ylab="'+field_maps[f]+'",ylim=c(0,'+ylim_max+'))\n')
	rscript_fh.write('graphics.off()')
	rscript_fh.close()
	os.system('cd '+os.path.dirname(rscript_file_location)+'; /usr/bin/Rscript ' + filename + ".r")
