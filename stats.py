import json
import os

class Stats():
    def __init__(self, simParams, simEventStop):
        # Statistics collected
        self._message_inserts = []
        self._message_decodes = {}
        self._matrix_reduces = []
        self._window_sizes = []
        self._last_message_exists = {}
        self._round_finished = 0
        self._time_elapsed = -1.0
        self._time_finished = -1.0

        # Simulation parameters
        self.simParams = simParams

        self.simEventStop = simEventStop

    #########################

    def message_track(self, rnd, decoded_objects, gossip_objects):
        if len(self._message_decodes) < self.simParams['SIM_WARMUP_DECODES']:
            return
        if len(self._message_inserts) < self.simParams['SIM_DURATION_INSERTS']:
            return

        # If the last message disappeared in the previous round, signal
        # simulation stop
        if rnd > 0 and (rnd-1) in self._last_message_exists:
            if self._last_message_exists[rnd-1] == False:
                self.simEventStop.set()
                return
        # If we already saw the last message in this round
        elif rnd in self._last_message_exists and self._last_message_exists[rnd] == True:
            return

        # Look for all messages inserted inside peers on the network
        for (_, _, last_pid) in self._message_inserts:
            # Look for the inserted message in the decoded objects
            for p in decoded_objects:
                if p.pid == last_pid:
                    self._last_message_exists[rnd] = True
                    return
            # Look for the inserted message in the gossip objects
            for lc in gossip_objects:
                for p in lc.messages:
                    if p.pid == last_pid:
                        self._last_message_exists[rnd] = True
                        return

        self._last_message_exists[rnd] = False

    # Record inserting message "pid"
    def message_insert(self, rnd, nid, pid):
        if len(self._message_decodes) < self.simParams['SIM_WARMUP_DECODES']:
            return

        # If we have already collected our simulation number of inserts
        if len(self._message_inserts) >= self.simParams['SIM_DURATION_INSERTS']:
            return

        self._message_inserts.append( (rnd, nid, pid) )

    # Record decoding message "pid"
    def message_decode(self, rnd, nid, pid):
        # If we hadn't started recording this PID yet
        if pid not in self._message_decodes:
            self._message_decodes[pid] = []

        # If this nid already decoded this pid in the past
        if nid in [ n for (_, n) in self._message_decodes[pid] ]:
            return

        self._message_decodes[pid].append( (rnd, nid) )

    # Record reducing "numrows" x "numcols" matrix, yielding "numsolved" new solutions
    def matrix_reduce(self, rnd, nid, numrows, numcols, numsolved):
        self._matrix_reduces.append( (rnd, nid, numrows, numcols, numsolved) )

    # Record solved and gossip window sizes
    def window_size(self, rnd, nid, solved_size, gossip_size):
        self._window_sizes.append( (rnd, nid, solved_size, gossip_size) )

    # Record simulation finished
    def round_finished(self, rnd):
        self._round_finished = rnd

    # Record time elapsed
    def time_elapsed(self, duration):
        self._time_elapsed = duration

    # Record time finished
    def time_finished(self, time):
        self._time_finished = time

    #########################

    def dump(self):
        i = 0
        while True:
            path = "data/%s-%d.data" % (self.simParams['NAME'], i)
            if not os.path.exists(path):
                break
            i += 1

        f = open(path, "w")
        data = {'simParams': self.simParams,
                'message_inserts': self._message_inserts,
                'message_decodes': self._message_decodes,
                'matrix_reduces': self._matrix_reduces,
                'window_sizes': self._window_sizes,
                'round_finished': self._round_finished,
                'time_elapsed': self._time_elapsed,
                'time_finished': self._time_finished}
        f.write(json.dumps(data))
        f.close()

        return path

