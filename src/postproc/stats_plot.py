from stats_process import *

def plot_simulation_pdecodes_vs_time(simProcStats):
    (times, _, pdecode) = simProcStats.compute_pdecodes()
    avg_pdecode = avg(pdecode)

    pylab.figure()
    pylab.plot(times, pdecode, 's')
    pylab.vlines(times, 0, pdecode)
    pylab.hlines(avg_pdecode, times[0], times[-1])
    pylab.title('Final Decoding of Inserted messages')
    pylab.xlabel('Time')
    pylab.ylabel('Percent Peers Decode')
    pylab.ylim([0, 101])

def plot_simulation_window_sizes_vs_time(simProcStats):
    time = {}
    solved_size = {}
    gossip_size = {}

    for (t, nid, ss, gs) in simProcStats.window_sizes:
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

def plot_aggregate_pdecode_vs_throughput(simProcStatsList, plotFilePrefix=None):
    data = {}
    for sim in simProcStatsList:
        params = sim.simParams
        numPeers = params['SIM_NUM_PEERS']
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
        pylab.errorbar(x, y, yerr=ci, fmt="s-", label="N=%d" % numPeers)
    pylab.xlabel('Contribution Interval')
    pylab.xlim([5, 25])
    pylab.ylabel('Average Percent Decode')
    pylab.ylim([0, 105])
    pylab.title('Availability vs. Contribution Interval')
    pylab.legend(loc='lower right')

    if plotFilePrefix is not None:
        pylab.savefig(plotFilePrefix + "-availability.eps")

def plot_aggregate_delay_vs_throughput(simProcStatsList, plotFilePrefix=None):
    data = {}
    for sim in simProcStatsList:
        params = sim.simParams
        numPeers = params['SIM_NUM_PEERS']
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
        pylab.errorbar(x, y, yerr=ci, fmt="s-", label="N=%d" % numPeers)
    pylab.xlabel('Contribution Interval')
    pylab.xlim([5, 25])
    pylab.ylabel('Average Delay')
    pylab.ylim([0, 25])
    pylab.title('Delay vs. Contribution Interval')
    pylab.legend()

    if plotFilePrefix is not None:
        pylab.savefig(plotFilePrefix + "-delay.eps")

def plot_aggregate_pdecode_vs_evil_nodes(simProcStatsList, plotFilePrefix=None):
    data = {}
    for sim in simProcStatsList:
        params = sim.simParams
        numPeers = params['SIM_NUM_PEERS']
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
        pylab.errorbar(x, y, yerr=ci, fmt="s-", label="N=%d" % numPeers)
    pylab.xlabel('Percent Attackers')
    pylab.xlim([-1, 31])
    pylab.ylabel('Average Percent Decoded')
    pylab.ylim([0, 105])
    pylab.title('Availability vs. Percent Attackers')
    pylab.legend(loc='lower right')

    if plotFilePrefix is not None:
        pylab.savefig(plotFilePrefix + "-availability.eps")

def plot_aggregate_delay_vs_evil_nodes(simProcStatsList, plotFilePrefix=None):
    data = {}
    for sim in simProcStatsList:
        params = sim.simParams
        numPeers = params['SIM_NUM_PEERS']
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
        pylab.errorbar(x, y, yerr=ci, fmt="s-", label="N=%d" % numPeers)
    pylab.xlabel('Percent Attackers')
    pylab.xlim([-1, 31])
    pylab.ylabel('Average Delay')
    pylab.ylim([0, 25])
    pylab.title('Delay vs. Percent Attackers')
    pylab.legend()

    if plotFilePrefix is not None:
        pylab.savefig(plotFilePrefix + "-delay.eps")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: %s <simulation files>" % sys.argv[0])
        sys.exit(1)

    # Make plots folder if it doesn't exist
    #if not os.path.exists("plots/"):
    #    os.mkdir("plots")

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

    simDataFiles = sys.argv[2:]

    if len(simDataFiles) == 1:
        simProcStats = ProcStats(simDataFiles)
        print(str(simProcStats))

        plot_simulation_pdecodes_vs_time(simProcStats)
        plot_simulation_window_sizes_vs_time(simProcStats)
        pylab.show()

    else:
        simProcStatsList = [ ProcStats(s) for s in simDataFiles ]
        for s in simProcStatsList:
            print(str(s) + "\n")

        if "Evil" in sys.argv[2]:
            plot_aggregate_pdecode_vs_evil_nodes(simProcStatsList)
            plot_aggregate_delay_vs_evil_nodes(simProcStatsList)
        else:
            plot_aggregate_pdecode_vs_throughput(simProcStatsList)
            plot_aggregate_delay_vs_throughput(simProcStatsList)

        pylab.show()

