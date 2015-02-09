#!/usr/bin/env python2

# NCGAB Simulator - Ivan A. Sergeev

import threading
import random
import time
import sys
import os

from stats import *
from log import *
from network import *
from message import *
from window import *
from peer import *
from evilpeer import *
from config import *

################################################################################

if __name__ == "__main__":
    # Make data and logs folders if they don't exist
    if not os.path.exists("data/"): os.mkdir("data")
    if not os.path.exists("logs/"): os.mkdir("logs")

    for si in range(len(SimParamsList)):
        simParams = SimParamsList[si]

        # If we have already completed this simulation, skip it
        if os.path.exists("data/%s-0.data" % simParams['NAME']):
            continue

        random.seed(simParams['SEED'])

        # Simulation stop event set by simStats
        simEventStop = threading.Event()

        # Simulation objects
        simStats = Stats(simParams, simEventStop)
        simLog = Log(simParams)
        simNetwork = Network(simLog, simStats)
        simPeers = []

        # Add cooperative peers to the network
        for i in range(simParams['SIM_NUM_PEERS'] - simParams['SIM_NUM_EVIL_PEERS']):
            simPeers.append(Peer(i, simNetwork, simLog, simStats, simParams))

        # Add evil peers to the network
        for i in range(simParams['SIM_NUM_EVIL_PEERS']):
            if simParams['SIM_EVIL_PEER_TYPE'] == "inactive":
                evilPeer = EvilPeer_Inactive
            elif simParams['SIM_EVIL_PEER_TYPE'] == "underdetermined":
                evilPeer = EvilPeer_Underdetermined
            elif simParams['SIM_EVIL_PEER_TYPE'] == "decodable":
                evilPeer = EvilPeer_Decodable

            simPeers.append(evilPeer(i + (simParams['SIM_NUM_PEERS'] - simParams['SIM_NUM_EVIL_PEERS']), \
                                simNetwork, simLog, simStats, simParams))

        print("\nStarting simulation %d / %d: %s" % (si+1, len(SimParamsList), simParams['NAME']))

        startTime = time.time()

        roundCount = 0
        while True:
            # Simulate the peers in a different order each round
            random.shuffle(simPeers)
            for n in simPeers:
                n.simulate(roundCount)

            sys.stdout.write("\r%d, %d -- Round %d" % \
                (len(simStats._message_inserts), len(simStats._message_decodes), roundCount+1))
            # Stop the simulation if we've collected enough data
            if simEventStop.is_set():
                break

            roundCount += 1

        endTime = time.time()

        # Log the finish
        simStats.round_finished(roundCount)
        simStats.time_elapsed(endTime - startTime)
        simStats.time_finished(endTime)
        simLog.log(roundCount, "finish", 0, "")

        print()

        # Dump stats
        print("Wrote stats to %s" % simStats.dump())
        # Dump log
        print("Wrote log to %s" % simLog.dump())
        # Print time elapsed
        print("Time elapsed: %.3f sec" % (endTime - startTime))

