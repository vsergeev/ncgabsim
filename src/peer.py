import sys

if sys.version_info.major == 2:
    import Queue as queue
else:
    import queue

from window import *
from message import *

class Peer():
    def __init__(self, nid, simNetwork, simLog, simStats, simParams):
        # Our unique peer ID
        self.nid = nid
        # Network, Log, Stats handles
        self.simNetwork = simNetwork
        self.simLog = simLog
        self.simStats = simStats
        # Simulation parameters
        self.simParams = simParams

        # Create an input queue
        self.queue = queue.Queue()
        # Create a solved message window
        self.decoded_window = Decoded_Window()
        # Create a gossip window
        self.gossip_window = Gossip_Window()

        # Initialize our window with dummy messages
        for _ in range(self.simParams['CODE_SIZE']):
            self.decoded_window.add(DummyMessage(), self.simParams['TTL_DECODE'])

        # Choose an initial random insert message timeout
        self.insert_message_timeout = int(random.randint(0, int(self.simParams['CONTRIBUTE_INTERVAL'])))

        # Join the network
        self.simNetwork.join(0, nid, self.queue)

    def simulate(self, rnd):
        # Update the TTLs of our object windows
        self.decoded_window.tick()
        self.gossip_window.tick()

        # Keep track of the last tracked message disappearing
        self.simStats.message_track(rnd, self.decoded_window.live_objects(), self.gossip_window.live_objects())
        # Log our window sizes
        self.simStats.window_size(rnd, self.nid, len(self.decoded_window.objects()), len(self.gossip_window.objects()))

        # Decrement our insert message timeout counter
        self.insert_message_timeout = max(0, self.insert_message_timeout - 1)

        # Introduce a new message if our random insert timeout expired, but only
        # if we've have a Decoded Window of at least CODE_SIZE
        if self.insert_message_timeout == 0:
            p = RealMessage(self.nid)
            # Add a real message to our decoded window
            if self.decoded_window.add(p, self.simParams['TTL_DECODE']):
                # Log the insert
                self.simLog.log(rnd, "insert", self.nid, str(p))
                self.simStats.message_insert(rnd, self.nid, p.pid)

            # Choose a new insert message timeout
            self.insert_message_timeout = int(self.simParams['CONTRIBUTE_INTERVAL'])

        # Process all received gossip
        while not self.queue.empty():
            try:
                (src, gossip) = self.queue.get(False)
            except queue.Empty:
                break

            # Add the linear combinations to our gossip window
            for lc in gossip:
                self.gossip_window.add(src, lc, self.simParams['TTL_GOSSIP'])

            # Log the receive
            self.simLog.log(rnd, "receive", self.nid, "src: %d, gossip: %s" % (src, str([str(p) for p in gossip])))

        # Try to solve some gossip
        (m_numrows, m_numcols, solved) = self.gossip_window.solve(self.decoded_window)
        # Log the reduce attempt
        self.simLog.log(rnd, "reduce", self.nid, "%dx%d to %d" % (m_numrows, m_numcols, len(solved)))
        self.simStats.matrix_reduce(rnd, self.nid, m_numrows, m_numcols, len(solved))

        # Add the decoded messages to our Decoded Window
        for p in solved:
            if self.decoded_window.add(p, self.simParams['TTL_DECODE']):
                # Log the decodes
                self.simLog.log(rnd, "decode", self.nid, str(p))
                if isinstance(p, RealMessage):
                    self.simStats.message_decode(rnd, self.nid, p.pid)

        # Fill up Decoded Window with dummy messages if it is short
        for _ in range(self.simParams['CODE_SIZE'] - len(self.decoded_window.live_objects())):
            self.decoded_window.add(DummyMessage(), self.simParams['TTL_DECODE'])

        # Look up LOOKUP_PERCENT subset of peers on the network
        dests = self.simNetwork.lookup_random(self.nid, int(self.simParams['LOOKUP_PERCENT']*self.simParams['SIM_NUM_PEERS']))
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

