import random

class Network():
    def __init__(self, simLog, simStats):
        self.simLog = simLog
        self.simStats = simStats
        self.network = {}

    def join(self, rnd, nid, q):
        self.network[nid] = q
        self.simLog.log(rnd, "join", nid, "")

    def leave(self, rnd, nid):
        if nid in self.network:
            del self.network[nid]
            self.simLog.log(rnd, "leave", nid, "")

    def lookup_random(self, nid, n):
        choices = list(self.network.keys())
        choices.remove(nid)
        random.shuffle(choices)
        return [self.network[choices[i]] for i in range(n)]

