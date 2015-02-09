import random
import operator
import ctypes
ctypes.cdll.LoadLibrary("./ff.so")
cff = ctypes.CDLL("./ff.so")

# Pre-compute finite field tables
cff.ff8_precompute()
# Pre-allocate ctypes matrix for Gaussian Elimination
Matrix = (ctypes.c_uint8 * (2048 * 2048))()
# Pre-allocate ctypes solved indices array
SolvedIndices = (ctypes.c_uint16 * (2048))()

def choose_weighted_random(scores):
    scores_cdf = []

    runningSum = 0
    for s in scores:
        runningSum += s
        scores_cdf.append(runningSum)

    random_score = random.random()*scores_cdf[-1]

    index = None
    for index in range(len(scores_cdf)):
        if scores_cdf[index] > random_score:
            break

    return index

class Decoded_Window():
    def __init__(self):
        self.window_live = []
        self.window_expired = []
        self.ttl = {}

    def add(self, p, ttl):
        if p in self.window_live or p in self.window_expired:
            return False

        # Add it to our live window
        self.window_live.append(p)
        self.ttl[p.pid] = ttl

        return True

    def tick(self):
        # Decrement the TTL for each object in the live window
        for p in self.window_live[:]:
            self.ttl[p.pid] -= 1
            # Move the item to the expired window if it expired
            if self.ttl[p.pid] <= 0:
                del self.ttl[p.pid]
                self.window_live.remove(p)
                self.window_expired.append(p)

    def live_objects(self):
        return self.window_live[:]

    def objects(self):
        return self.window_live[:] + self.window_expired[:]

    def choose_random_uniform(self, n):
        # Shuffle all live objects
        choices = random.shuffle(self.live_objects())
        n = min(n, len(choices))

        # Choose first n
        return choices[0:n]

    def choose_random(self, n):
        # Sort live objects by TTL
        choices, scores = [list(t) for t in zip(*sorted([(m, self.ttl[m.pid]) for m in self.live_objects()], key=operator.itemgetter(1)))]

        n = min(n, len(choices))

        # Choose n weighted random choices
        chosen = []
        for _ in range(n):
            k = choose_weighted_random(scores)
            chosen.append(choices[k])
            del choices[k]
            del scores[k]

        return chosen

    def __str__(self):
        s = "Decoded Window\n"
        for x in self.window_live:
            s += "\t" + str(x) + " TTL: " + str(self.ttl[x.pid]) + "\n"
        return s

class Gossip_Window():
    def __init__(self):
        self.window_live = []
        self.ttl = {}

        self.window_live_by_source = {}

    def add(self, src, p, ttl):
        if p in self.window_live:
            return False

        # Add it to our live window
        self.window_live.append(p)
        self.ttl[p.pid] = ttl

        # Create a new list for the source if it's not in our dictionary
        if src not in self.window_live_by_source:
            self.window_live_by_source[src] = []

        # Add the message to the source's list
        self.window_live_by_source[src].append(p)

        return True

    def tick(self):
        # For each source
        for src in self.window_live_by_source:
            # For each live object
            for p in self.window_live_by_source[src]:
                # Decrement the TTL
                self.ttl[p.pid] -= 1
                # Delete the object if it expires
                if self.ttl[p.pid] <= 0:
                    del self.ttl[p.pid]
                    self.window_live_by_source[src].remove(p)
                    self.window_live.remove(p)


    def choose_random_uniform(self):
        # Choose a random source
        src = random.choice(list(self.window_live_by_source.keys()))

        # Gather a list of objects by this source
        choices = self.window_live_by_source[src]

        return random.choice(choices)

    def choose_random(self):
        # Choose a random source
        src = random.choice(list(self.window_live_by_source.keys()))

        # Sort live objects by TTL
        choices, scores = [list(t) for t in zip(*sorted([(m, self.ttl[m.pid]) for m in self.live_objects()], key=operator.itemgetter(1)))]

        return choices[choose_weighted_random(scores)]

    def live_objects(self):
        return self.window_live[:]

    def objects(self):
        return self.window_live[:]

    def __str__(self):
        s = "Gossip Window\n"
        for x in self.window_live:
            s += "\t" + str(x) + " TTL: " + str(self.ttl[x.pid]) + "\n"
        return s

    def solve(self, decoded_window):
        # Map of column index -> message
        col_map = {}
        # Map of pid -> column index
        pid_map = {}

        num_cols = 0

        decoded = decoded_window.objects()
        # Gather unique columns from decoded messages
        for m in decoded:
            col_map[num_cols] = m
            pid_map[m.pid] = num_cols
            num_cols += 1
        num_rows = len(decoded)
        num_decoded = num_cols

        undecoded_lc = self.live_objects()
        # Gather unique columns from linear combinations
        for lc in undecoded_lc:
            for m in lc.messages:
                if m.pid not in pid_map:
                    col_map[num_cols] = m
                    pid_map[m.pid] = num_cols
                    num_cols += 1
        num_rows += len(undecoded_lc)

        # Clear matrix and solved indices
        cff.matrix_util_clear(SolvedIndices, Matrix, num_rows, num_cols)

        row = 0
        # Build decoded rows (... 0, 0, 1, 0, 0 ... )
        for m in decoded:
            Matrix[num_cols*row + pid_map[m.pid]] = 1
            row += 1

        # Build linear combined rows ( ..., a, b, c, d, ... )
        for lc in undecoded_lc:
            for i in range(len(lc.coefs)):
                Matrix[num_cols*row + pid_map[lc.messages[i].pid]] = lc.coefs[i]
            row += 1

        # rref matrix
        num_solved = cff.matrix_solve(SolvedIndices, Matrix, num_rows, num_cols)

        # Gather newly solved messages
        solved = []
        for i in range(num_solved):
            if SolvedIndices[i] >= num_decoded:
                m = col_map[SolvedIndices[i]]
                solved.append(m)

        return (num_rows, num_cols, solved)

