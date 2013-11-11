import json
import os

class Stats():
    def __init__(self, simParams, simEventStop):
        # Statistics collected
        self.message_inserts = []
        self.message_decodes = {}
        self.matrix_reduces = []
        self.window_sizes = []
        self.last_message_exists = {}
        self.round_finished = 0

        # Simulation parameters
        self.simParams = simParams

        self.simEventStop = simEventStop

    #########################

    def message_track(self, rnd, decoded_objects, gossip_objects):
        if len(self.message_decodes) < self.simParams['SIM_WARMUP_DECODES']:
            return
        if len(self.message_inserts) < self.simParams['SIM_DURATION_INSERTS']:
            return

        # If the last message disappeared in the previous round, signal
        # simulation stop
        if rnd > 0 and (rnd-1) in self.last_message_exists:
            if self.last_message_exists[rnd-1] == False:
                self.simEventStop.set()
                return

        # If we already saw the last message in this round
        if rnd in self.last_message_exists and self.last_message_exists[rnd] == True:
                return

        # Look for all messages inserted inside peers on the network
        for (_, _, last_pid) in self.message_inserts:
            # Look for the inserted message in the decoded objects
            for p in decoded_objects:
                if str(p) == last_pid:
                    self.last_message_exists[rnd] = True
                    return
            # Look for the inserted message in the gossip objects
            for lc in gossip_objects:
                for p in lc.messages:
                    if str(p) == last_pid:
                        self.last_message_exists[rnd] = True
                        return

        self.last_message_exists[rnd] = False

    def message_insert(self, rnd, nid, pid):
        if len(self.message_decodes) < self.simParams['SIM_WARMUP_DECODES']:
            return

        # If we have already collected our simulation number of inserts
        if len(self.message_inserts) >= self.simParams['SIM_DURATION_INSERTS']:
            return

        self.message_inserts.append( (rnd, nid, pid) )

    def message_decode(self, rnd, nid, pid):
        # If we hadn't started recording this PID yet
        if pid not in self.message_decodes:
            self.message_decodes[pid] = []

        # If this nid already decoded this pid in the past
        if nid in [ n for (_, n) in self.message_decodes[pid] ]:
            return

        self.message_decodes[pid].append( (rnd, nid) )

    def matrix_reduce(self, rnd, nid, numrows, numcols, numsolved):
        self.matrix_reduces.append( (rnd, nid, numrows, numcols, numsolved) )

    def window_size(self, rnd, nid, solved_size, gossip_size):
        self.window_sizes.append( (rnd, nid, solved_size, gossip_size) )

    def finished(self, rnd):
        self.round_finished = rnd

    #########################

    def dump(self):
        i = 0
        while True:
            path = "data/%s-%d.data" % (self.simParams['NAME'], i)
            if not os.path.exists(path): break
            i += 1

        f = open(path, "w")
        data = {'simParams': self.simParams,
                'message_inserts': self.message_inserts,
                'message_decodes': self.message_decodes,
                'matrix_reduces': self.matrix_reduces,
                'window_sizes': self.window_sizes,
                'round_finished': self.round_finished}
        f.write(json.dumps(data))
        f.close()

        return path

