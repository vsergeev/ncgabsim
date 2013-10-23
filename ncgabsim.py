#!/usr/bin/env python2

# NCGAB Simulator - Ivan A. Sergeev

import threading
import random
import json
import sys
import copy
import os

if sys.version_info.major == 2:
    import Queue as queue
else:
    import queue

import ff

import termcolor

################################################################################

simConfig = 1

# Cooperative Peer Simulation

SimTemplate = {
    'NAME':                     "",
    'DESC':                     "",

    'LOOKUP_PERCENT':           0.25,
    'CODE_SIZE':                4,
    'TTL_DECODE':               30,
    'TTL_GOSSIP':               10,

    'SIM_NUM_PEERS':            0,
    'SIM_NUM_EVIL_PEERS':       0,
    'CONTRIBUTE_INTERVAL':      0,

    'SIM_WARMUP_DECODES':       50,
    'SIM_DURATION_INSERTS':     100,

    'SEED':                     0,

    'PRINT_LOG':                False,
}

if simConfig == 1:
    NumPeersSweep = [10, 25, 50]
    ContributeIntervalSweep = [7.0, 10, 12.0, 15.0, 17.0, 20.0, 22.0]
    SeedSweep = [0x1, 0x2, 0x3]

    SimParamsList = []
    for numPeers in NumPeersSweep:
        for contributeInterval in ContributeIntervalSweep:
            for seed in SeedSweep:
                name = "Sim-N%d-R%d-S%d" % (numPeers, contributeInterval, seed)
                params = copy.deepcopy(SimTemplate)
                params['NAME'] = name
                params['SEED'] = seed
                params['SIM_NUM_PEERS'] = numPeers
                params['CONTRIBUTE_INTERVAL'] = contributeInterval
                SimParamsList.append(params)

if simConfig == 7:
    NumPeersSweep = [25]
    ContributeIntervalSweep = [7.0, 10, 12.0, 15.0, 17.0, 20.0, 22.0]
    SeedSweep = [0x1, 0x2, 0x3]

    SimParamsList = []
    for numPeers in NumPeersSweep:
        for contributeInterval in ContributeIntervalSweep:
            for seed in SeedSweep:
                name = "SimSelect2-N%d-R%d-S%d" % (numPeers, contributeInterval, seed)
                params = copy.deepcopy(SimTemplate)
                params['NAME'] = name
                params['SEED'] = seed
                #params['SELECTION'] = 'Uniform'
                params['SELECTION'] = 'Weighted'
                params['SIM_NUM_PEERS'] = numPeers
                params['CONTRIBUTE_INTERVAL'] = contributeInterval
                SimParamsList.append(params)

################################################################################

# Evil Peer Simulations

SimTemplate = {
    'NAME':                     "Evil-Base",
    'DESC':                     "",

    'LOOKUP_PERCENT':           0.25,
    'CODE_SIZE':                4,
    'TTL_DECODE':               30,
    'TTL_GOSSIP':               20,

    'SIM_NUM_PEERS':            0,
    'SIM_NUM_EVIL_PEERS':       0,
    'CONTRIBUTE_INTERVAL':      20,

    'SIM_EVIL_PEER_TYPE':       "",

    'SIM_WARMUP_DECODES':       50,
    'SIM_DURATION_INSERTS':     75,

    'PRINT_LOG':                False,
}

# Inactive, Underdetermined Gossip
if simConfig == 2:
    EvilPeerTypeSweep = ["inactive", "underdetermined"]
    NumPeersSweep = [10, 20, 30]
    pNumEvilPeersSweep = [0.0, 0.10, 0.20, 0.30]
    SeedSweep = [0x1, 0x2, 0x3]

    SimParamsList = []
    for evilPeerType in EvilPeerTypeSweep:
        for numPeers in NumPeersSweep:
            for pNumEvilPeers in pNumEvilPeersSweep:
                for seed in SeedSweep:
                    name = "Evil-%s-N%d-E%0.2f-S%d" % (evilPeerType, numPeers, pNumEvilPeers, seed)
                    params = copy.deepcopy(SimTemplate)
                    params['NAME'] = name
                    params['SEED'] = seed
                    params['SIM_NUM_PEERS'] = numPeers
                    params['SIM_NUM_EVIL_PEERS'] = int(pNumEvilPeers * params['SIM_NUM_PEERS'])
                    params['SIM_EVIL_PEER_TYPE'] = evilPeerType
                    SimParamsList.append(params)

# Decodable with CODE_SIZE = 4
if simConfig == 3:
    EvilPeerTypeSweep = ["decodable"]
    NumPeersSweep = [25]
    pNumEvilPeersSweep = [0.0, 0.10, 0.20, 0.30]
    SeedSweep = [0x1, 0x2, 0x3]

    SimParamsList = []
    for evilPeerType in EvilPeerTypeSweep:
        for numPeers in NumPeersSweep:
            for pNumEvilPeers in pNumEvilPeersSweep:
                for seed in SeedSweep:
                    name = "Evil-%s-CS4-N%d-E%0.2f-S%d" % (evilPeerType, numPeers, pNumEvilPeers, seed)
                    params = copy.deepcopy(SimTemplate)
                    params['NAME'] = name
                    params['SEED'] = seed
                    params['SIM_NUM_PEERS'] = numPeers
                    params['SIM_NUM_EVIL_PEERS'] = int(pNumEvilPeers * params['SIM_NUM_PEERS'])
                    params['SIM_EVIL_PEER_TYPE'] = evilPeerType
                    params['CODE_SIZE'] = 4
                    SimParamsList.append(params)

# Decodable with CODE_SIZE = 6
if simConfig == 4:
    EvilPeerTypeSweep = ["decodable"]
    NumPeersSweep = [25]
    pNumEvilPeersSweep = [0.0, 0.10, 0.20, 0.30]
    SeedSweep = [0x1, 0x2, 0x3]

    SimParamsList = []
    for evilPeerType in EvilPeerTypeSweep:
        for numPeers in NumPeersSweep:
            for pNumEvilPeers in pNumEvilPeersSweep:
                for seed in SeedSweep:
                    name = "Evil-%s-CS6-N%d-E%0.2f-S%d" % (evilPeerType, numPeers, pNumEvilPeers, seed)
                    params = copy.deepcopy(SimTemplate)
                    params['NAME'] = name
                    params['SEED'] = seed
                    params['SIM_NUM_PEERS'] = numPeers
                    params['SIM_NUM_EVIL_PEERS'] = int(pNumEvilPeers * params['SIM_NUM_PEERS'])
                    params['SIM_EVIL_PEER_TYPE'] = evilPeerType
                    params['CODE_SIZE'] = 6
                    SimParamsList.append(params)

# Decodable with CODE_SIZE = 10
if simConfig == 5:
    EvilPeerTypeSweep = ["decodable"]
    NumPeersSweep = [25]
    pNumEvilPeersSweep = [0.0, 0.10, 0.20, 0.30]
    SeedSweep = [0x1, 0x2, 0x3]

    SimParamsList = []
    for evilPeerType in EvilPeerTypeSweep:
        for numPeers in NumPeersSweep:
            for pNumEvilPeers in pNumEvilPeersSweep:
                for seed in SeedSweep:
                    name = "Evil-%s-CS10-N%d-E%0.2f-S%d" % (evilPeerType, numPeers, pNumEvilPeers, seed)
                    params = copy.deepcopy(SimTemplate)
                    params['NAME'] = name
                    params['SEED'] = seed
                    params['SIM_NUM_PEERS'] = numPeers
                    params['SIM_NUM_EVIL_PEERS'] = int(pNumEvilPeers * params['SIM_NUM_PEERS'])
                    params['SIM_EVIL_PEER_TYPE'] = evilPeerType
                    params['CODE_SIZE'] = 10
                    SimParamsList.append(params)


# Colluded Decodable with CODE_SIZE = 8
if simConfig == 6:
    EvilPeerTypeSweep = ["colluded"]
    NumPeersSweep = [20]
    pNumEvilPeersSweep = [0.0, 0.10, 0.20, 0.30]
    SeedSweep = [0x1, 0x2, 0x3]

    SimParamsList = []
    for evilPeerType in EvilPeerTypeSweep:
        for numPeers in NumPeersSweep:
            for pNumEvilPeers in pNumEvilPeersSweep:
                for seed in SeedSweep:
                    name = "Evil-%s-CS6-N%d-E%0.2f-S%d" % (evilPeerType, numPeers, pNumEvilPeers, seed)
                    params = copy.deepcopy(SimTemplate)
                    params['NAME'] = name
                    params['SEED'] = seed
                    params['SIM_NUM_PEERS'] = numPeers
                    params['SIM_NUM_EVIL_PEERS'] = int(pNumEvilPeers * params['SIM_NUM_PEERS'])
                    params['SIM_EVIL_PEER_TYPE'] = evilPeerType
                    params['CODE_SIZE'] = 8
                    SimParamsList.append(params)

################################################################################

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

################################################################################

class Log():
    def __init__(self, simParams):
        self.elog = []
        self.simParams = simParams

    def log(self, rnd, etype, enid, emsg):
        e = {}
        e['time'] = rnd
        e['type'] = etype
        e['nid'] = enid
        e['msg'] = emsg
        ejson = json.dumps(e)
        self.elog.append(ejson)

        if self.simParams['PRINT_LOG']:
            if etype == "join" or etype == "leave": print(termcolor.colored(ejson, "yellow"))
            elif etype == "receive": print(termcolor.colored(ejson, "yellow"))
            elif etype == "insert": print(termcolor.colored(ejson, "red"))
            elif etype == "reduce": print(termcolor.colored(ejson, "blue"))
            elif etype == "decode": print(termcolor.colored(ejson, "green"))
            else: print(termcolor.colored(ejson, "white"))

    def dump(self):
        i = 0
        while True:
            path = "logs/%s-%d.log" % (self.simParams['NAME'], i)
            if not os.path.exists(path): break
            i += 1

        f = open(path, "w")
        for e in self.elog:
            f.write(e + "\n")
        f.close()

        return path

################################################################################

class Network():
    def __init__(self, simlog, simstats):
        self.simlog = simlog
        self.simstats = simstats
        self.network = {}

    def join(self, rnd, nid, q):
        self.network[nid] = q
        self.simlog.log(rnd, "join", nid, "")

    def leave(self, rnd, nid):
        if nid in self.network:
            del self.network[nid]
            self.simlog.log(rnd, "leave", nid, "")

    def lookup_random(self, nid, n):
        choices = list(self.network.keys())
        choices.remove(nid)
        random.shuffle(choices)
        return [self.network[choices[i]] for i in range(n)]

################################################################################

class Message():
    def __init__(self, pid):
        self.pid = pid

    def __str__(self):
        return self.pid

    def __eq__(self, other):
        if (self.pid == other.pid):
            return True
        return False

class DummyMessage(Message):
    def __init__(self):
        Message.__init__(self, "R%04x" % random.getrandbits(32))

class RealMessage(Message):
    def __init__(self, nid):
        Message.__init__(self, "M%d/%04x" % (nid, random.getrandbits(32)))

class EvilMessage(Message):
    def __init__(self, nid):
        Message.__init__(self, "E%d/%04x" % (nid, random.getrandbits(32)))

class RLC(Message):
    def __init__(self, messages):
        coefs = [random.randint(0, 255) for p in messages]
        pid = "LC/(" + ",".join([p.pid for p in messages]) + ")" + "/(" + \
                       ",".join(["%02x" % c for c in coefs]) + ")"
        Message.__init__(self, pid)
        self.messages = messages
        self.coefs = coefs

################################################################################

def choose_weighted_random(objects, scores):
    scores_cdf = []
    for s in scores[:]:
        scores_cdf.append(sum(scores_cdf) + s)

    random_score = random.random()*scores_cdf[-1]
    for index in range(len(scores_cdf)):
        if scores_cdf[index] > random_score:
            break

    return index

class Window():
    def __init__(self, keep_expired = False):
        self.window = []
        self.ttl = {}
        self.keep_expired = keep_expired

    def add(self, p, ttl):
        if type(p) == type(None) or p in self.window:
            return False

        self.window.append(p)
        self.ttl[str(p)] = ttl
        return True

    def prune(self):
        if self.keep_expired:
            return []

        # Create a list of expired objects
        expiredList = list(filter(lambda x: self.ttl[str(x)] == 0, self.window))

        # Remove all expired objects from our window
        for e in expiredList:
            self.window.remove(e)
            del self.ttl[str(e)]

        return expiredList

    def tick(self):
        # Decrement the TTL for each object in the window
        for x in self.window:
            self.ttl[str(x)] = max(0, self.ttl[str(x)] - 1)

        return self.prune()

    def live_objects(self):
        return list(filter(lambda x: self.ttl[str(x)] > 0, self.window))

    def objects(self):
        return self.window[:]

    def __str__(self):
        s = "Window\n"
        for x in self.window:
            s += "\t" + str(x) + " TTL: " + str(self.ttl[str(x)]) + "\n"
        return s

class Decoded_Window(Window):
    def __init__(self):
        Window.__init__(self, keep_expired = True)

    def choose_random_uniform(self, n):
        choices = self.live_objects()
        random.shuffle(choices)
        return choices[0 : min(n, len(choices))]

    def choose_random(self, n):
        choices = self.live_objects()
        scores = [self.ttl[str(c)] for c in choices]

        n = min(n, len(choices))
        chosen = []
        for i in range(n):
            k = choose_weighted_random(choices, scores)
            chosen.append(choices[k])
            del choices[k]
            del scores[k]

        return chosen

class Gossip_Window(Window):
    def __init__(self):
        Window.__init__(self, keep_expired = False)
        # Keep active objects in a dictionary by source as well
        self.active_objects_by_source = {}

    def add(self, src, p, ttl):
        if Window.add(self, p, ttl) == True:
            # Create a new list for the source if it's not in our dictionary
            if src not in self.active_objects_by_source:
                self.active_objects_by_source[src] = []

            # Add the message to the source's list
            self.active_objects_by_source[src].append(p)
            return True

        return False

    def prune(self):
        expiredList = Window.prune(self)
        # For each expired object
        for e in expiredList:
            for src in self.active_objects_by_source:
                # If the object exists in this source's list
                if e in self.active_objects_by_source[src]:
                    # Delete it
                    self.active_objects_by_source[src].remove(e)
                    # Delete the source's list if it's empty now
                    if len(self.active_objects_by_source[src]) == 0:
                        del self.active_objects_by_source[src]
                    break
        return expiredList

    def choose_random_uniform(self):
        # Choose a random source
        source = random.choice(list(self.active_objects_by_source.keys()))

        # Gather a list of objects by this source
        objects = self.active_objects_by_source[source]

        return random.choice(objects)

    def choose_random(self):
        # Choose a random source
        source = random.choice(list(self.active_objects_by_source.keys()))

        # Gather a list of objects by this source
        choices = self.active_objects_by_source[source]
        scores = [self.ttl[str(c)] for c in choices]

        return choices[choose_weighted_random(choices, scores)]

    def fast_rref(self, m, b, x):
        done = False
        pi = 0

        # Iterate through each row
        for j in range(len(m)):
            # While we do not have a pivot for this row
            while m[j][pi] == 0:
                # Find a row below to swap with for a pivot at pi
                for k in range(j+1, len(m)):
                    if m[k][pi] != 0:
                        # Swap with this row
                        (m[j], m[k]) = (m[k], m[j])
                        (b[j], b[k]) = (b[k], b[j])
                        break

                # Increment pivot index if we could not find a row to swap with
                if m[j][pi] == 0:
                    pi += 1

                # If there is no pivots left, we're done reducing
                if pi == len(m[0]):
                    done = True
                    break

            if done:
                break

            # Divide through to have a pivot of 1
            m[j] = [ ff.FiniteFieldArray.ff_elem_div(m[j][i], m[j][pi]) for i in range(len(m[0])) ]

            # Eliminate above & below
            for k in range(len(m)):
                if k != j and m[k][pi] != 0:
                    m[k] = [ ff.FiniteFieldArray.ff_elem_sub(m[k][i], \
                      ff.FiniteFieldArray.ff_elem_mul(m[j][i], m[k][pi])) for i in range(len(m[0])) ]

            # Move onto the next pivot
            pi += 1
            # If there is no pivots left, we're done reducing
            if pi == len(m[0]):
                break

        solved = []
        used = []

        for i in range(len(m)):
            # If this row has only one non-zero entry
            reduced_coefs = [1*(m[i][j] != 0) for j in range(len(m[0]))]
            if sum(reduced_coefs) == 1:
                # Add the solution to our solved list
                solved.append(x[reduced_coefs.index(1)])
                # Add the decoded LC to our used list
                used.append(b[i])

        return (solved, used)

    def solve(self, decoded_window):
        unsolved_message_map = {}

        # Get a list of decoded messages
        decoded_messages = decoded_window.objects()

        # Make a list of undecoded linear combinations
        undecoded_lc = []
        for lc in self.live_objects():
            # If we've decoded this entire linear combination, don't add it
            if sum([p in decoded_messages for p in lc.messages]) == len(lc.messages):
                continue
            undecoded_lc.append(lc)

        # Put together a list of all decoded messages referenced by undecoded
        # linear combinations
        ref_decoded_messages = []
        for lc in undecoded_lc:
            for p in lc.messages:
                if p in decoded_messages and p not in ref_decoded_messages:
                    ref_decoded_messages.append(p)

        # Assemble x of mx=b
        #   x maps messages to column indices
        x = {}
        # Assign a col index to each referenced decoded message
        for p in ref_decoded_messages:
            x[str(p)] = len(x)
        # Assign a col index to each undecoded message
        for lc in undecoded_lc:
            for p in lc.messages:
                if str(p) not in x:
                    x[str(p)] = len(x)
                    unsolved_message_map[str(p)] = p

        # Assemble m and b of mx = b
        m = []
        b = []
        # Create a row for each solved message
        for p in ref_decoded_messages:
            r = [0] * len(x)
            r[x[str(p)]] = 1
            m.append(r)
            b.append(p)
        # Create a row for each linear combination
        for lc in undecoded_lc:
            r = [0] * len(x)
            for i in range(len(lc.messages)):
                pid = str(lc.messages[i])
                coef = lc.coefs[i]
                r[x[pid]] = coef
            m.append(r)
            b.append(lc)

        # Information about the size of this reduce attempt
        b_pids = [str(p) for p in b]
        m_numrows = len(m)
        m_numcols = len(m[0]) if m_numrows > 0 else 0

        (solved, used) = self.fast_rref(m, b, sorted(x, key=x.get))

        # Remove previously decoded objects from our solution
        for p in ref_decoded_messages:
            if str(p) in solved:
                solved.remove(str(p))
            if p in used:
                used.remove(p)

        # Map message ids to message objects in our solution
        for i in range(len(solved)):
            solved[i] = unsolved_message_map[solved[i]]

        # Information about the solution of this reduce attempt
        s_pids = [str(p) for p in solved]

        return (m_numrows, m_numcols, b_pids, s_pids, solved)

################################################################################

class EvilPeer():
    def __init__(self, nid, network, simlog, simstats, simParams):
        # Our unique peer ID
        self.nid = nid
        # Network, Log, Stats handles
        self.network = network
        self.simlog = simlog
        self.simstats = simstats
        # Simulation parameters
        self.simParams = simParams

        # Create a solved message window
        self.decoded_window = Decoded_Window()

        # Create an input queue
        self.queue = queue.Queue()

        # Join the network
        self.network.join(0, nid, self.queue)


class EvilPeer_Inactive(EvilPeer):
    def simulate(self, rnd):
        # Process all received gossip
        while not self.queue.empty():
            try: (src, gossip) = self.queue.get(False)
            except queue.Empty: break
            # Throw it away...

class EvilPeer_Underdetermined(EvilPeer):
    def simulate(self, rnd):
        # Process all received gossip
        while not self.queue.empty():
            try: (src, gossip) = self.queue.get(False)
            except queue.Empty: break
            # Throw it away...

        # Send our own gossip
        dests = self.network.lookup_random(self.nid, self.simParams['SIM_NUM_PEERS'] - 1)
        for d in dests:
            # Code some gossip based on our Decoded Window
            gossip = []

            # Code an RLC of new messages
            gossip.append(RLC([EvilMessage(self.nid) for i in range(self.simParams['CODE_SIZE'])]))

            # Transmit to the destination
            d.put( (self.nid, gossip) )

class EvilPeer_Decodable(EvilPeer):
    def simulate(self, rnd):
        # Update the TTLs of our object windows
        self.decoded_window.tick()

        # Keep our decoded window filled with our own messages
        for i in range(self.simParams['CODE_SIZE'] - len(self.decoded_window.live_objects())):
            self.decoded_window.add(EvilMessage(self.nid), self.simParams['CODE_SIZE'])

        # Process all received gossip
        while not self.queue.empty():
            try: (src, gossip) = self.queue.get(False)
            except queue.Empty: break
            # Throw it away...

        # Send our own gossip
        dests = self.network.lookup_random(self.nid, self.simParams['SIM_NUM_PEERS'] - 1)
        for d in dests:
            # Code some gossip based on our Decoded Window
            gossip = []

            # Send RLCs of our current decoded window
            gossip.append(RLC(self.decoded_window.choose_random(self.simParams['CODE_SIZE'])))

            # Transmit to the destination
            d.put( (self.nid, gossip) )

################################################################################

class Peer():
    def __init__(self, nid, network, simlog, simstats, simParams):
        # Our unique peer ID
        self.nid = nid
        # Network, Log, Stats handles
        self.network = network
        self.simlog = simlog
        self.simstats = simstats
        # Simulation parameters
        self.simParams = simParams

        # Create an input queue
        self.queue = queue.Queue()
        # Create a solved message window
        self.decoded_window = Decoded_Window()
        # Create a gossip window
        self.gossip_window = Gossip_Window()

        # Initialize our window with dummy messages
        for i in range(self.simParams['CODE_SIZE']):
            self.decoded_window.add(DummyMessage(), self.simParams['TTL_DECODE'])

        # Choose a random insert message timeout
        self.insert_message_timeout = int(random.randint(0, int(self.simParams['CONTRIBUTE_INTERVAL'])))

        # Join the network
        self.network.join(0, nid, self.queue)

    def simulate(self, rnd):
        # Update the TTLs of our object windows
        self.decoded_window.tick()
        self.decoded_window.prune()
        self.gossip_window.tick()
        self.gossip_window.prune()
        # Keep track of the last message disappearing
        self.simstats.message_track(rnd, self.decoded_window.live_objects(), self.gossip_window.live_objects())
        # Log our window sizes
        self.simstats.window_size(rnd, self.nid, len(self.decoded_window.objects()), len(self.gossip_window.objects()))

        # Update our insert message timeout counter
        if self.insert_message_timeout > 0:
            self.insert_message_timeout -= 1

        # Introduce a new message if our random insert timeout expired, but only
        # if we've have a Decoded Window of at least CODE_SIZE
        if self.insert_message_timeout == 0:
            p = RealMessage(self.nid)
            # Add a real message to our decoded window
            if self.decoded_window.add(p, self.simParams['TTL_DECODE']):
                # Log the insert
                self.simlog.log(rnd, "insert", self.nid, str(p))
                self.simstats.message_insert(rnd, self.nid, str(p))

            # Choose a new insert message timeout
            #self.insert_message_timeout = int(random.expovariate(1.0 / float(self.simParams['CONTRIBUTE_INTERVAL'])))
            self.insert_message_timeout = int(self.simParams['CONTRIBUTE_INTERVAL'])

        # Process all received gossip
        while not self.queue.empty():
            try: (src, gossip) = self.queue.get(False)
            except queue.Empty: break

            # Add the linear combinations to our gossip window
            for lc in gossip:
                self.gossip_window.add(src, lc, self.simParams['TTL_GOSSIP'])

            # Log the receive
            self.simlog.log(rnd, "receive", self.nid, "src: %d, gossip: %s" % (src, str([str(p) for p in gossip])))

        # Try to solve some gossip
        (m_numrows, m_numcols, b_pids, s_pids, solved) = self.gossip_window.solve(self.decoded_window)
        # Log the reduce attempt
        self.simlog.log(rnd, "reduce", self.nid, "%dx%d to %d" % (m_numrows, m_numcols, len(solved)))
        self.simstats.matrix_reduce(rnd, self.nid, m_numrows, m_numcols, len(solved))
        self.simlog.log(rnd, "reduce_info", self.nid, "%s to %s" % (str(b_pids), str(s_pids)))

        # Add the decoded messages to our Decoded Window
        for p in solved:
            if self.decoded_window.add(p, self.simParams['TTL_DECODE']):
                # Log the decodes
                self.simlog.log(rnd, "decode", self.nid, str(p))
                if isinstance(p, RealMessage):
                    self.simstats.message_decode(rnd, self.nid, str(p))

        # Fill up Decoded Window with dummy messages if it is short
        for i in range(self.simParams['CODE_SIZE'] - len(self.decoded_window.live_objects())):
            self.decoded_window.add(DummyMessage(), self.simParams['TTL_DECODE'])

        # Look up LOOKUP_PERCENT subset of peers on the network
        dests = self.network.lookup_random(self.nid, int(self.simParams['LOOKUP_PERCENT']*self.simParams['SIM_NUM_PEERS']))
        for d in dests:
            gossip = []

            if random.getrandbits(1):
                # Code new-gossip from our Decoded Window
                gossip.append(RLC(self.decoded_window.choose_random(self.simParams['CODE_SIZE'])))
            else:
                # Choose re-gossip from our Gossip Window
                if len(self.gossip_window.live_objects()) > 0:
                    gossip.append(self.gossip_window.choose_random())

            # Transmit to the destination
            d.put( (self.nid, gossip) )


################################################################################

if __name__ == "__main__":
    ff.FiniteFieldArray.ff_precompute()

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

        roundCount = 0
        while True:
            # Simulate the peers in a different order each round
            random.shuffle(simPeers)
            for n in simPeers:
                n.simulate(roundCount)

            sys.stdout.write("\r%d, %d -- Round %d" % \
                (len(simStats.message_inserts), len(simStats.message_decodes), roundCount+1))
            # Stop the simulation if we've collected enough data
            if simEventStop.is_set():
                break

            roundCount += 1

        # Log the finish at this round count
        simStats.finished(roundCount)
        simLog.log(roundCount, "finish", 0, "")

        print()

        # Dump stats
        print("Wrote stats to %s" % simStats.dump())
        # Dump log
        print("Wrote log to %s" % simLog.dump())

