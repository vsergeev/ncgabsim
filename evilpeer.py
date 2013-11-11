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


