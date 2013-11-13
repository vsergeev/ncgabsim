#!/usr/bin/python3

# Plotter for NCGAB Simulator Results

import sys
import json
import numpy
import pylab

def avg(x):
    if len(x) > 0:
        return (sum(x) / float(len(x)))
    return 0.0

def ci_95(x):
    std = numpy.std(x)
    ci = 1.96*std/numpy.sqrt(len(x))
    return ci

class ProcStats():
    def __init__(self, filename):
        with open(filename) as f:
            data = json.loads(f.read())

        print("Loaded %s %s" % (data['simParams']['NAME'], data['simParams']['DESC']))
        self.simParams = data['simParams']
        self.message_inserts = data['message_inserts']
        self.message_decodes = data['message_decodes']
        self.matrix_reduces = data['matrix_reduces']
        self.window_sizes = data['window_sizes']

        # Convert string keys back to integer keys (JSON doesn't support
        # integer keys in dictionaries)
        conv_message_decodes = {}
        for k in self.message_decodes.keys():
            conv_message_decodes[int(k)] = self.message_decodes[k]
        self.message_decodes = conv_message_decodes

    #########################

    def dump_decodes(self):
        for i in range(len(self.message_inserts)):
            # Print time, node id, and message id of insert
            (itime, nid, pid) = self.message_inserts[i]
            print("[%.6f]: nid %d, insert %s" % (itime, nid, pid))
            # If this message was decoded by others
            if pid in self.message_decodes and len(self.message_decodes[pid]) > 0:
                # Count number of decodes
                ndecodes = len(self.message_decodes[pid])
                # Print time and node id of the decode
                for (dtime, nid) in self.message_decodes[pid]:
                    print("\t[%.6f]: nid %d, decode" % (dtime, nid))
                print("\n\tnumber of decodes: %d / %d = %.2f %%\n" % (ndecodes, \
                     self.simParams['SIM_NUM_PEERS'] - 1 - self.simParams['SIM_NUM_EVIL_PEERS'], \
                     100.0 * float(ndecodes)/(self.simParams['SIM_NUM_PEERS']-1-self.simParams['SIM_NUM_EVIL_PEERS'])))

    def dump_reduces(self):
        for (itime, nid, m, n, ns) in self.matrix_reduces:
            print("[%.6f]: nid %d, reduce %dx%d to %d" % (itime, nid, m, n, ns))

    def dump_window_sizes(self):
        for (t, nid, ss, gs) in self.window_sizes:
            print("[%.6f]: nid %d, solved size %d, gossip size %d" % (t, nid, ss, gs))

    #########################

    def compute_delays(self):
        delay_min = []
        delay_max = []
        delay_avg = []

        # For each inserted message
        for (itime, _, pid) in self.message_inserts:
            # If it was decoded
            if pid in self.message_decodes and len(self.message_decodes[pid]) > 0:
                # Collect the delays to decoding
                delays = [ (dtime - itime) for (dtime, _) in self.message_decodes[pid] ]
                # Add it to our min, max, avg tables
                delay_min.append( delays[0] )
                delay_max.append( delays[-1] )
                delay_avg.append( sum(delays) / float(len(delays)) )

        return (delay_min, delay_max, delay_avg)

    def compute_pdecodes(self):
        times = []
        pids = []
        pdecode = []

        # For each inserted message
        for (time, _, pid) in self.message_inserts:
            times.append(time)
            pids.append(pid)
            # If the message was decoded
            if pid in self.message_decodes and len(self.message_decodes[pid]) > 0:
                # Calculate the percent of other nodes that decoded it
                pdecode.append( 100.0 * \
                    (float((len(self.message_decodes[pid]))) / \
                    float(self.simParams['SIM_NUM_PEERS']-1-self.simParams['SIM_NUM_EVIL_PEERS'])))
            else:
                pdecode.append(0.0)

        return (times, pids, pdecode)

    def compute_avg_delay(self):
        (_, _, delay_avg) = self.compute_delays()
        return (numpy.mean(delay_avg), ci_95(delay_avg))

    def compute_avg_pdecode(self):
        (_, _, pdecode) = self.compute_pdecodes()
        return (numpy.mean(pdecode), ci_95(pdecode))

    #########################

    def __str__(self):
        s = self.simParams['NAME']

        s += "\tNum inserts: %d" % len(self.message_inserts)

        (_, _, pdecode) = self.compute_pdecodes()
        avg_pdecode = avg(pdecode)
        s += "\tDecode Percent: %.2f\t" % avg_pdecode

        (delay_min, delay_max, delay_avg) = self.compute_delays()
        avg_delay_min = avg(delay_min)
        avg_delay_max = avg(delay_max)
        avg_delay_avg = avg(delay_avg)
        s += "\tAvg Delay: %.6f" % avg_delay_avg
        s += "\tMin Delay: %.6f" % avg_delay_min
        s += "\tMax Delay: %.6f" % avg_delay_max

        return s


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: %s <simulation data file>" % sys.argv[0])
        sys.exit(1)


    elif len(simsToProcess) > 1:
        statsProcList = [ StatsProcess(p) for p in simsToProcess ]

        for s in statsProcList:
            s.print_stats()

        p = StatsPlot(plotFilePrefix, statsProcList)
        if "Evil" in sys.argv[2]:
            p.plot_pdecode_vs_evil_nodes()
            p.plot_delay_vs_evil_nodes()
        else:
            p.plot_pdecode_vs_throughput()
            p.plot_delay_vs_throughput()
        pylab.show()

