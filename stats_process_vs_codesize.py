#!/usr/bin/python3

# Plotter for NCGAB Simulator Results

import sys
import json
import numpy
import pylab

################################################################################

def avg(x):
    return (sum(x) / float(len(x))) if len(x) > 0 else 0.0

def ci_95(x):
    std = numpy.std(x)
    ci = 1.96*std/numpy.sqrt(len(x))
    return ci

class StatsProcess():
    def __init__(self, filename):
        f = open(filename)
        data = json.loads(f.read())
        print("Loaded %s %s" % (data['simParams']['NAME'], data['simParams']['DESC']))
        self.simParams = data['simParams']
        self.message_inserts = data['message_inserts']
        self.message_decodes = data['message_decodes']
        self.matrix_reduces = data['matrix_reduces']
        self.window_sizes = data['window_sizes']
        f.close()

    #########################

    def dump_decodes(self):
        for i in range(len(self.message_inserts)):
            (itime, nid, pid) = self.message_inserts[i]
            print("[%.6f]: nid %d, insert %s" % (itime, nid, pid))
            ndecodes = 0
            for (dtime, nid) in self.message_decodes[pid]:
                print("\t[%.6f]: nid %d, decode" % (dtime - itime, nid))
                ndecodes += 1
            print("\n\tnumber of decodes: %d / %d = %.2f %%\n" % (ndecodes, \
                 self.simParams['SIM_NUM_PEERS'] - 1, 100.0 * float(ndecodes)/(self.simParams['SIM_NUM_PEERS']-1)))

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
                # Calculated the delays to decoding
                delays = [ (dtime - itime) for (dtime, _) in self.message_decodes[pid] ]
                # Add it to our tables
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
            if pid in self.message_decodes and len(self.message_decodes[pid]) > 0:
                pdecode.append( 100.0 * \
                    (float((len(self.message_decodes[pid]))) / \
                    float(self.simParams['SIM_NUM_PEERS']-self.simParams['SIM_NUM_EVIL_PEERS']-1)))
            else:
                pdecode.append(0.0)

        return (times, pids, pdecode)

    def compute_avg_delay(self):
        (_, _, delay_avg) = self.compute_delays()
        return (numpy.mean(delay_avg), ci_95(delay_avg))

    def compute_avg_pdecode(self):
        (_, _, pdecode) = self.compute_pdecodes()
        pdecode_mean = numpy.mean(pdecode)
        pdecode_std = numpy.std(pdecode)
        pdecode_ci = 1.96*pdecode_std/numpy.sqrt(len(pdecode))
        return (pdecode_mean, pdecode_ci)

    #########################

    def print_stats(self):
        print(self.simParams['NAME'])

        print("\tNum inserts: %d" % len(self.message_inserts))

        (_, _, pdecode) = self.compute_pdecodes()
        avg_pdecode = avg(pdecode)
        print("\tDecode Percent: %.2f\t" % avg_pdecode)

        (delay_min, delay_max, delay_avg) = self.compute_delays()
        avg_delay_min = avg(delay_min)
        avg_delay_max = avg(delay_max)
        avg_delay_avg = avg(delay_avg)
        print("\tAvg Delay: %.6f" % avg_delay_avg)
        print("\tMin Delay: %.6f" % avg_delay_min)
        print("\tMax Delay: %.6f" % avg_delay_max)

        print ()

    #########################

    def plot_pdecodes_vs_time(self):
        (times, pids, pdecode) = self.compute_pdecodes()
        avg_pdecode = avg(pdecode)

        pylab.figure()
        pylab.plot(times, pdecode, 's')
        pylab.vlines(times, 0, pdecode)
        pylab.hlines(avg_pdecode, times[0], times[-1])
        pylab.title('Final Decoding of Inserted messages')
        pylab.xlabel('Time')
        pylab.ylabel('Percent Peers Decode')
        pylab.ylim([0, 101])

    def plot_window_sizes_vs_time(self):
        time = {}
        solved_size = {}
        gossip_size = {}

        for (t, nid, ss, gs) in self.window_sizes:
            if nid not in time:
                time[nid] = []
                solved_size[nid] = []
                gossip_size[nid] = []

            time[nid].append(t)
            solved_size[nid].append(ss)
            gossip_size[nid].append(gs)

        pylab.figure()
        for nid in time.keys():
            pylab.plot(time[nid], solved_size[nid])
        pylab.title('Solved Window Size')
        pylab.xlabel('Time')
        pylab.ylabel('Items')

        pylab.figure()
        for nid in time.keys():
            pylab.plot(time[nid], gossip_size[nid])
        pylab.title('Gossip Window Size')
        pylab.xlabel('Time')
        pylab.ylabel('Items')

################################################################################

class StatsPlot():
    def __init__(self, plotFilePrefix, statsProcList):
        self.statsProcList = statsProcList
        self.plotFilePrefix = plotFilePrefix

    def plot_pdecode_vs_throughput(self):
        data = {}
        for sim in self.statsProcList:
            params = sim.simParams
            numPeers = params['CODE_SIZE']
            contributeInterval = params['CONTRIBUTE_INTERVAL']
            if numPeers not in data:
                data[numPeers] = {}
            if contributeInterval not in data[numPeers]:
                data[numPeers][contributeInterval] = []
            data[numPeers][contributeInterval].append(sim.compute_avg_pdecode()[0])

        pylab.figure()
        for numPeers in sorted(data.keys()):
            x = sorted(data[numPeers].keys())
            y = [ numpy.mean(data[numPeers][r]) for r in x]
            ci = [ ci_95(data[numPeers][r]) for r in x]
            pylab.errorbar(x, y, yerr=ci, fmt="s-", label="%s" % numPeers)
        pylab.xlabel('Contribution Interval')
        pylab.xlim([5, 25])
        pylab.ylabel('Average Percent Decode')
        pylab.ylim([0, 105])
        pylab.title('Availability vs. Contribution Interval')
        pylab.legend(loc='lower right')
        pylab.savefig(self.plotFilePrefix + "-availability.eps")

    def plot_delay_vs_throughput(self):
        data = {}
        for sim in self.statsProcList:
            params = sim.simParams
            numPeers = params['CODE_SIZE']
            contributeInterval = params['CONTRIBUTE_INTERVAL']
            if numPeers not in data:
                data[numPeers] = {}
            if contributeInterval not in data[numPeers]:
                data[numPeers][contributeInterval] = []
            data[numPeers][contributeInterval].append(sim.compute_avg_delay()[0])

        pylab.figure()
        for numPeers in sorted(data.keys()):
            x = sorted(data[numPeers].keys())
            y = [ numpy.mean(data[numPeers][r]) for r in x]
            ci = [ ci_95(data[numPeers][r]) for r in x]
            pylab.errorbar(x, y, yerr=ci, fmt="s-", label="%s" % numPeers)
        pylab.xlabel('Contribution Interval')
        pylab.xlim([5, 25])
        pylab.ylabel('Average Delay')
        pylab.ylim([0, 40])
        pylab.title('Delay vs. Contribution Interval')
        pylab.legend()
        pylab.savefig(self.plotFilePrefix + "-delay.eps")

    def plot_pdecode_vs_evil_nodes(self):

        data = {}
        for sim in self.statsProcList:
            params = sim.simParams
            numPeers = params['CODE_SIZE']
            percentEvil = 100.0 * params['SIM_NUM_EVIL_PEERS'] / float(params['SIM_NUM_PEERS'])
            if numPeers not in data:
                data[numPeers] = {}
            if percentEvil not in data[numPeers]:
                data[numPeers][percentEvil] = []
            data[numPeers][percentEvil].append(sim.compute_avg_pdecode()[0])

        pylab.figure()
        for numPeers in sorted(data.keys()):
            x = sorted(data[numPeers].keys())
            y = [ numpy.mean(data[numPeers][r]) for r in x]
            ci = [ ci_95(data[numPeers][r]) for r in x]
            pylab.errorbar(x, y, yerr=ci, fmt="s-", label="CODE\_SIZE=%d" % numPeers)
        pylab.xlabel('Percent Attackers')
        pylab.xlim([-1, 31])
        pylab.ylabel('Average Percent Decoded')
        pylab.ylim([0, 101])
        pylab.title('Availability vs. Percent Attackers')
        pylab.legend(loc='lower left')
        pylab.savefig(self.plotFilePrefix + "-availability.eps")

    def plot_delay_vs_evil_nodes(self):
        data = {}
        for sim in self.statsProcList:
            params = sim.simParams
            numPeers = params['CODE_SIZE']
            percentEvil = 100.0 * params['SIM_NUM_EVIL_PEERS'] / float(params['SIM_NUM_PEERS'])
            if numPeers not in data:
                data[numPeers] = {}
            if percentEvil not in data[numPeers]:
                data[numPeers][percentEvil] = []
            data[numPeers][percentEvil].append(sim.compute_avg_delay()[0])

        pylab.figure()
        for numPeers in sorted(data.keys()):
            x = sorted(data[numPeers].keys())
            y = [ numpy.mean(data[numPeers][r]) for r in x]
            ci = [ ci_95(data[numPeers][r]) for r in x]
            pylab.errorbar(x, y, yerr=ci, fmt="s-", label="CODE\_SIZE=%d" % numPeers)
        pylab.xlabel('Percent Attackers')
        pylab.xlim([-1, 31])
        pylab.ylabel('Average Delay')
        pylab.ylim([0, 25])
        pylab.title('Delay vs. Percent Attackers')
        pylab.legend()
        pylab.savefig(self.plotFilePrefix + "-delay.eps")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: <plot output prefix> <simulation data files ...>")
        sys.exit(1)

    # From http://www.scipy.org/Cookbook/Matplotlib/LaTeX_Examples
    fig_width_pt = 253.0
    inches_per_pt = 1.0/72.27
    golden_mean = (numpy.sqrt(5)-1.0)/2.0
    fig_width = fig_width_pt*inches_per_pt
    fig_height = fig_width*golden_mean
    fig_size =  [fig_width,fig_height]
    params = {'backend': 'ps',
              'axes.labelsize': 9,
              'text.fontsize': 9,
              'legend.fontsize': 9,
              'xtick.labelsize': 7,
              'ytick.labelsize': 7,
              'text.usetex': True,
              'figure.figsize': fig_size,
              'figure.subplot.bottom': 0.15,
              'font.size': 9,
              'font.family': 'serif'}
    pylab.rcParams.update(params)

    plotFilePrefix = sys.argv[1]
    simsToProcess = sys.argv[2:]

    if len(simsToProcess) == 1:
        statsProc = StatsProcess(simsToProcess[0])
        statsProc.print_stats()
        statsProc.plot_pdecodes_vs_time()
        statsProc.plot_window_sizes_vs_time()
        pylab.show()

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

